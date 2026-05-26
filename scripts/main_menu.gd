extends Control

## Main menu: New Game, Load Game, Credits, Quit. Load flow lists fixed user://
## slots via SaveManager (missing/corrupt JSON → empty slot dict).
## During a stub session (New Game), Escape opens pause: Resume, Save Game,
## Settings, Quit to Menu. Save writes JSON compatible with SaveManager.load_save_slot.

const SAVE_SLOT_PATHS: PackedStringArray = [
	"user://save_slot_1.json",
	"user://save_slot_2.json",
	"user://save_slot_3.json",
]

@onready var _center: Control = $Center
@onready var _load_panel: Control = $LoadSlotPanel
@onready var _gameplay_placeholder: Control = $GameplayPlaceholder
@onready var _pause_panel: Control = $PausePanel
@onready var _save_panel: Control = $SaveSlotPanel
@onready var _slot_buttons: Array[Button] = [
	$LoadSlotPanel/Margin/VBox/Slot1,
	$LoadSlotPanel/Margin/VBox/Slot2,
	$LoadSlotPanel/Margin/VBox/Slot3,
]
@onready var _save_slot_buttons: Array[Button] = [
	$SaveSlotPanel/SaveMargin/SaveVBox/SaveSlot1,
	$SaveSlotPanel/SaveMargin/SaveVBox/SaveSlot2,
	$SaveSlotPanel/SaveMargin/SaveVBox/SaveSlot3,
]

var _session_active: bool = false


func _ready() -> void:
	$Center/MainButtons/NewGame.pressed.connect(_on_new_game)
	$Center/MainButtons/LoadGame.pressed.connect(_on_load_game)
	$Center/MainButtons/Credits.pressed.connect(_on_credits)
	$Center/MainButtons/Quit.pressed.connect(_on_quit)
	$LoadSlotPanel/Margin/VBox/Back.pressed.connect(_return_to_main_buttons)
	for i in _slot_buttons.size():
		_slot_buttons[i].pressed.connect(_on_load_slot_pressed.bind(i))
	$PausePanel/PauseMargin/PauseVBox/Resume.pressed.connect(_close_pause_menu)
	$PausePanel/PauseMargin/PauseVBox/SaveGame.pressed.connect(_on_pause_save_game)
	$PausePanel/PauseMargin/PauseVBox/Settings.pressed.connect(_on_pause_settings)
	$PausePanel/PauseMargin/PauseVBox/QuitToMenu.pressed.connect(_on_quit_to_menu)
	$SaveSlotPanel/SaveMargin/SaveVBox/SaveBack.pressed.connect(_on_save_slot_back)
	for i in _save_slot_buttons.size():
		_save_slot_buttons[i].pressed.connect(_on_save_slot_chosen.bind(i))
	_load_panel.visible = false
	_pause_panel.visible = false
	_save_panel.visible = false
	_gameplay_placeholder.visible = false


func _unhandled_input(event: InputEvent) -> void:
	if not event.is_action_pressed("ui_cancel"):
		return
	if _save_panel.visible:
		_on_save_slot_back()
		get_viewport().set_input_as_handled()
		return
	if _load_panel.visible:
		_return_to_main_buttons()
		get_viewport().set_input_as_handled()
		return
	if not _session_active:
		return
	if _pause_panel.visible:
		_close_pause_menu()
	else:
		_open_pause_menu()
	get_viewport().set_input_as_handled()


func _on_new_game() -> void:
	_session_active = true
	_center.visible = false
	_gameplay_placeholder.visible = true


func _on_load_game() -> void:
	_refresh_load_slot_button_labels()
	_center.visible = false
	_load_panel.visible = true


func _on_credits() -> void:
	# Placeholder until credits scene exists.
	pass


func _on_quit() -> void:
	get_tree().quit()


func _return_to_main_buttons() -> void:
	_load_panel.visible = false
	_center.visible = true


func _refresh_load_slot_button_labels() -> void:
	for i in _slot_buttons.size():
		_apply_slot_label_for_button(_slot_buttons[i], SAVE_SLOT_PATHS[i], i + 1)


func _refresh_save_slot_button_labels() -> void:
	for i in _save_slot_buttons.size():
		_apply_slot_label_for_button(_save_slot_buttons[i], SAVE_SLOT_PATHS[i], i + 1)


func _apply_slot_label_for_button(btn: Button, path: String, slot_number: int) -> void:
	var data: Dictionary = SaveManager.load_save_slot(path)
	if data.get("empty", false) == true:
		btn.text = "Slot %d (Empty)" % slot_number
	else:
		btn.text = "Slot %d" % slot_number


func _on_load_slot_pressed(slot_index: int) -> void:
	var data: Dictionary = SaveManager.load_save_slot(SAVE_SLOT_PATHS[slot_index])
	if data.get("empty", false) == true:
		_return_to_main_buttons()
		return
	# Non-empty slot: no playable yet; leave UI stable and return to main menu.
	_return_to_main_buttons()


func _open_pause_menu() -> void:
	_pause_panel.visible = true


func _close_pause_menu() -> void:
	_pause_panel.visible = false


func _on_pause_save_game() -> void:
	_refresh_save_slot_button_labels()
	_pause_panel.visible = false
	_save_panel.visible = true


func _on_pause_settings() -> void:
	# Placeholder until settings UI exists.
	pass


func _on_quit_to_menu() -> void:
	_session_active = false
	_pause_panel.visible = false
	_save_panel.visible = false
	_gameplay_placeholder.visible = false
	_center.visible = true


func _on_save_slot_back() -> void:
	_save_panel.visible = false
	_pause_panel.visible = true


func _on_save_slot_chosen(slot_index: int) -> void:
	var path := SAVE_SLOT_PATHS[slot_index]
	var payload := _build_session_save_payload()
	if not _write_save_json(path, payload):
		push_error("MainMenu: could not write save to %s" % path)
		return
	_on_save_slot_back()


func _build_session_save_payload() -> Dictionary:
	return {
		"empty": false,
		"version": SaveManager.SAVE_SLOT_VERSION,
		"session_stub": true,
		"saved_at_unix": Time.get_unix_time_from_system(),
	}


func _write_save_json(path: String, data: Dictionary) -> bool:
	var text := JSON.stringify(data, "\t")
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(text)
	return f.get_error() == OK


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_GO_BACK_REQUEST:
		if _save_panel.visible:
			_on_save_slot_back()
			get_viewport().set_input_as_handled()
			return
		if _load_panel.visible:
			_return_to_main_buttons()
			get_viewport().set_input_as_handled()
			return
		if _session_active and _pause_panel.visible:
			_close_pause_menu()
			get_viewport().set_input_as_handled()

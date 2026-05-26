extends Control

## Main menu: New Game, Load Game, Credits, Quit. Load flow lists fixed user://
## slots via SaveManager (missing/corrupt JSON → empty slot dict).

const SAVE_SLOT_PATHS: PackedStringArray = [
	"user://save_slot_1.json",
	"user://save_slot_2.json",
	"user://save_slot_3.json",
]

@onready var _center: Control = $Center
@onready var _load_panel: Control = $LoadSlotPanel
@onready var _slot_buttons: Array[Button] = [
	$LoadSlotPanel/Margin/VBox/Slot1,
	$LoadSlotPanel/Margin/VBox/Slot2,
	$LoadSlotPanel/Margin/VBox/Slot3,
]


func _ready() -> void:
	$Center/MainButtons/NewGame.pressed.connect(_on_new_game)
	$Center/MainButtons/LoadGame.pressed.connect(_on_load_game)
	$Center/MainButtons/Credits.pressed.connect(_on_credits)
	$Center/MainButtons/Quit.pressed.connect(_on_quit)
	$LoadSlotPanel/Margin/VBox/Back.pressed.connect(_return_to_main_buttons)
	for i in _slot_buttons.size():
		_slot_buttons[i].pressed.connect(_on_slot_pressed.bind(i))
	_load_panel.visible = false


func _on_new_game() -> void:
	# Hook for first playable / scene change in a later phase.
	pass


func _on_load_game() -> void:
	_refresh_slot_button_labels()
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


func _refresh_slot_button_labels() -> void:
	for i in _slot_buttons.size():
		var data: Dictionary = SaveManager.load_save_slot(SAVE_SLOT_PATHS[i])
		var n := i + 1
		if data.get("empty", false) == true:
			_slot_buttons[i].text = "Slot %d (Empty)" % n
		else:
			_slot_buttons[i].text = "Slot %d" % n


func _on_slot_pressed(slot_index: int) -> void:
	var data: Dictionary = SaveManager.load_save_slot(SAVE_SLOT_PATHS[slot_index])
	if data.get("empty", false) == true:
		_return_to_main_buttons()
		return
	# Non-empty slot: no playable yet; leave UI stable and return to main menu.
	_return_to_main_buttons()


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_GO_BACK_REQUEST:
		if _load_panel.visible:
			_return_to_main_buttons()
			get_viewport().set_input_as_handled()

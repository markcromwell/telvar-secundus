extends Control
## Three-slot save picker using standard Control nodes (Panel, VBox, Buttons, Label).

signal dialog_closed

@onready var _notification: Label = $Panel/VBox/NotificationLabel
@onready var _slot1: Button = $Panel/VBox/Slot1
@onready var _slot2: Button = $Panel/VBox/Slot2
@onready var _slot3: Button = $Panel/VBox/Slot3


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_notification.visible = false
	_slot1.pressed.connect(_on_slot_pressed.bind(1))
	_slot2.pressed.connect(_on_slot_pressed.bind(2))
	_slot3.pressed.connect(_on_slot_pressed.bind(3))
	$Panel/VBox/Cancel.pressed.connect(_close_dialog)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_close_dialog()


func _on_slot_pressed(slot_index: int) -> void:
	var path := "user://save_slot_%d.json" % slot_index
	var payload: Variant = SceneManager.get_save_state()
	var text := JSON.stringify(payload)
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		push_error("Save failed (could not open path): %s" % path)
		return
	file.store_string(text)
	file.close()
	await _flash_saved_notification()


func _flash_saved_notification() -> void:
	_notification.text = "Game saved."
	_notification.visible = true
	await get_tree().create_timer(1.0, true).timeout
	_notification.visible = false


func _close_dialog() -> void:
	dialog_closed.emit()

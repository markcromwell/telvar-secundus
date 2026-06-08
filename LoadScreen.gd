extends Control
## Load-game UI overlay: shows a save-slot list and a Back button that returns to
## the main menu. Designed to be shown as an overlay (e.g. under a CanvasLayer) so
## the host main menu is preserved and its state (settings sliders, etc.) survives
## the round-trip. The Back action emits [signal back_requested] and frees this
## screen's own overlay; it is guarded against double-activation so repeated
## presses can never re-enter the teardown and crash.

## Emitted once when the player chooses to return to the main menu. The host
## (main menu) listens for this to restore focus / refresh persisted values.
signal back_requested

@onready var _slot_list: ItemList = $MarginContainer/VBoxContainer/SlotList
@onready var _back_button: Button = $MarginContainer/VBoxContainer/BackButton

## True once a back action has started, so a second press is a no-op.
var _back_in_progress: bool = false


func _ready() -> void:
	_back_button.pressed.connect(_on_back_pressed)
	set_process_unhandled_input(true)
	_populate_slots()


func _populate_slots() -> void:
	# Placeholder slot list. When SaveManager is present it provides the real
	# slot names; otherwise we show an empty-slot placeholder so the screen is
	# usable (and loads in CI) without a save system.
	if _slot_list == null:
		return
	_slot_list.clear()
	if Engine.has_singleton("SaveManager"):
		var manager: Object = Engine.get_singleton("SaveManager")
		if manager.has_method("list_user_save_paths"):
			for path in manager.list_user_save_paths():
				_slot_list.add_item(str(path))
	if _slot_list.item_count == 0:
		_slot_list.add_item("No saved games")


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_request_back()
		get_viewport().set_input_as_handled()


func _on_back_pressed() -> void:
	_request_back()


## Idempotent back-to-main-menu handler. Safe to call repeatedly: the
## `_back_in_progress` guard means only the first invocation does any work, so
## rapid double-clicks (or a click plus an Escape press) cannot double-free.
func _request_back() -> void:
	if _back_in_progress:
		return
	_back_in_progress = true
	set_process_unhandled_input(false)
	back_requested.emit()
	_free_overlay()


## Free only this screen's own overlay, never the host. When shown under a
## CanvasLayer (the overlay convention used by MainMenu/Credits), free that layer
## so the host main menu underneath is left intact. Null-guarded throughout.
func _free_overlay() -> void:
	var parent := get_parent()
	if parent != null and parent is CanvasLayer:
		parent.queue_free()
	else:
		queue_free()

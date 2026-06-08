extends Control
## Credits overlay: shows CREDITS.md and returns to the main menu. Mirrors the
## LoadScreen pattern so Credits/Settings/Load share one consistent back flow: a
## Back button and the ui_cancel action both emit [signal back_requested] and free
## this screen's own overlay (the host CanvasLayer), leaving the main menu intact.
## The teardown is guarded against double-activation so a Back press combined with
## an Escape press (or a rapid double-click) can never double-free or crash.

## Emitted once when the player chooses to return to the main menu. The host menu
## listens for this to restore focus.
signal back_requested

const _CREDITS_PATH := "res://CREDITS.md"

@onready var _scroll: ScrollContainer = $ScrollContainer
@onready var _label: RichTextLabel = $ScrollContainer/RichTextLabel
@onready var _back_button: Button = $BackButton

## True once a back action has started, so a second trigger is a no-op.
var _back_in_progress: bool = false


func _ready() -> void:
	_scroll.resized.connect(_on_scroll_resized)
	_back_button.pressed.connect(_on_back_pressed)
	set_process_unhandled_input(true)
	_on_scroll_resized()
	_load_credits()


func _on_scroll_resized() -> void:
	if _scroll.size.x > 0:
		_label.custom_minimum_size.x = _scroll.size.x


func _load_credits() -> void:
	if not FileAccess.file_exists(_CREDITS_PATH):
		_label.text = "CREDITS.md was not found at res://CREDITS.md."
		return
	var f := FileAccess.open(_CREDITS_PATH, FileAccess.READ)
	if f == null:
		_label.text = "Could not open CREDITS.md for reading."
		return
	_label.text = f.get_as_text()
	f.close()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_request_back()
		get_viewport().set_input_as_handled()


func _on_back_pressed() -> void:
	_request_back()


## Idempotent back-to-main-menu handler. The `_back_in_progress` guard means only
## the first invocation does any work, so a Back click plus an Escape press cannot
## double-free.
func _request_back() -> void:
	if _back_in_progress:
		return
	_back_in_progress = true
	set_process_unhandled_input(false)
	back_requested.emit()
	_free_overlay()


## Free only this screen's own overlay, never the host. When shown under a
## CanvasLayer (the overlay convention used by MainMenu), free that layer so the
## main menu underneath is left intact. Null-guarded throughout.
func _free_overlay() -> void:
	var parent := get_parent()
	if parent != null and parent is CanvasLayer:
		parent.queue_free()
	else:
		queue_free()

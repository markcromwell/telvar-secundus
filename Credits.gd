extends Control

const _CREDITS_PATH := "res://CREDITS.md"

@onready var _scroll: ScrollContainer = $ScrollContainer
@onready var _label: RichTextLabel = $ScrollContainer/RichTextLabel


func _ready() -> void:
	_scroll.resized.connect(_on_scroll_resized)
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

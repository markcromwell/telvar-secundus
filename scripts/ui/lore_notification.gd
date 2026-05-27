extends CanvasLayer

## HUD toast: shows a lore entry title for 3s when LoreManager unlocks an ID.

const LORE_JSON_PATH := "res://assets/lore/lore_entries.json"

@onready var _label: Label = $Label
@onready var _timer: Timer = $Timer

var _titles_by_id: Dictionary = {}


func _ready() -> void:
	_load_lore_titles()
	LoreManager.lore_unlocked.connect(_on_lore_unlocked)
	_timer.timeout.connect(_on_timer_timeout)
	_label.visible = false


func _load_lore_titles() -> void:
	if not FileAccess.file_exists(LORE_JSON_PATH):
		return
	var file := FileAccess.open(LORE_JSON_PATH, FileAccess.READ)
	if file == null:
		return
	var text := file.get_as_text()
	file.close()
	var parsed: Variant = JSON.parse_string(text)
	if parsed == null or typeof(parsed) != TYPE_ARRAY:
		return
	for item in parsed:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var d: Dictionary = item
		var id := String(d.get("id", ""))
		if id == "":
			continue
		_titles_by_id[id] = String(d.get("title", id))


func _on_lore_unlocked(entry_id: String) -> void:
	var title := String(_titles_by_id.get(entry_id, entry_id))
	_label.text = title
	_label.visible = true
	_timer.start(3.0)


func _on_timer_timeout() -> void:
	_label.visible = false

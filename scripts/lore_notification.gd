extends CanvasLayer

const LORE_ENTRIES_PATH := "res://assets/lore/lore_entries.json"

@onready var panel: PanelContainer = $PanelContainer
@onready var title_label: Label = $PanelContainer/Label
@onready var hide_timer: Timer = $HideTimer

var _titles_by_id: Dictionary = {}


func _ready() -> void:
	_load_lore_titles()
	LoreManager.lore_unlocked.connect(_on_lore_unlocked)
	hide_timer.timeout.connect(_on_hide_timer_timeout)


func _load_lore_titles() -> void:
	if not FileAccess.file_exists(LORE_ENTRIES_PATH):
		push_warning("LoreNotification: missing lore entries at %s" % LORE_ENTRIES_PATH)
		return
	var raw := FileAccess.get_file_as_string(LORE_ENTRIES_PATH)
	var parsed: Variant = JSON.parse_string(raw)
	if typeof(parsed) != TYPE_ARRAY:
		push_warning("LoreNotification: lore_entries.json is not a JSON array")
		return
	for item in parsed:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var d: Dictionary = item
		if d.has("id") and d.has("title"):
			_titles_by_id[str(d["id"])] = str(d["title"])


func _on_lore_unlocked(entry_id: String) -> void:
	var title: String = str(_titles_by_id.get(entry_id, entry_id))
	title_label.text = title
	show_notification()


func show_notification() -> void:
	panel.visible = true
	hide_timer.stop()
	hide_timer.start()


func _on_hide_timer_timeout() -> void:
	panel.visible = false

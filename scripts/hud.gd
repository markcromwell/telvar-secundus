extends CanvasLayer

@onready var _toast_panel: PanelContainer = $ToastPanel
@onready var _toast_label: Label = $ToastPanel/ToastLabel
@onready var _toast_timer: Timer = $ToastTimer

var _lore_titles: Dictionary = {}


func _ready() -> void:
	_load_lore_titles()
	LoreManager.lore_unlocked.connect(_on_lore_unlocked)
	_toast_timer.timeout.connect(_on_toast_timer_timeout)
	_toast_panel.visible = false


func _load_lore_titles() -> void:
	var path := "res://assets/lore/lore_entries.json"
	if not FileAccess.file_exists(path):
		return
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return
	var data = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_ARRAY:
		return
	for item in data:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var d: Dictionary = item
		var id := str(d.get("id", ""))
		if id.is_empty():
			continue
		_lore_titles[id] = str(d.get("title", id))


func _on_lore_unlocked(entry_id: String) -> void:
	_toast_label.text = str(_lore_titles.get(entry_id, entry_id))
	_toast_panel.visible = true
	_toast_timer.start()


func _on_toast_timer_timeout() -> void:
	_toast_panel.visible = false

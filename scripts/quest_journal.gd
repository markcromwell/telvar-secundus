extends Control

## Quest journal UI: mirrors QuestManager.quests into Active / Completed tabs.

@onready var _active_list: VBoxContainer = $TabContainer/Active/ActiveList
@onready var _completed_list: VBoxContainer = $TabContainer/Completed/CompletedList


func _ready() -> void:
	QuestManager.quest_updated.connect(_on_quest_updated)
	_rebuild_all()


func _on_quest_updated(_id: String) -> void:
	_rebuild_all()


func _rebuild_all() -> void:
	_clear_children(_active_list)
	_clear_children(_completed_list)
	for quest_id in QuestManager.quests.keys():
		var q: Dictionary = QuestManager.quests[quest_id] as Dictionary
		var status := str(q.get("status", ""))
		if status != "active" and status != "completed":
			continue
		var label := Label.new()
		var title := _read_quest_title(str(quest_id))
		var prog: Dictionary = QuestManager.get_progress(str(quest_id))
		var done: int = int(prog.get("done", 0))
		var total: int = int(prog.get("total", 0))
		label.text = "%s (%d/%d)" % [title, done, total]
		if status == "active":
			_active_list.add_child(label)
		else:
			_completed_list.add_child(label)


func _clear_children(node: Node) -> void:
	while node.get_child_count() > 0:
		var c := node.get_child(0)
		node.remove_child(c)
		c.free()


func _read_quest_title(id: String) -> String:
	var path := "res://assets/quests/%s.json" % id
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return id
	var text := file.get_as_text()
	file.close()
	var parsed: Variant = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		return id
	var d := parsed as Dictionary
	var t := str(d.get("title", ""))
	return t if not t.is_empty() else id

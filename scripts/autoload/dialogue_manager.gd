extends Node


func show_dialogue(dialogue_id: String) -> void:
	if dialogue_id.is_empty():
		return
	var path := "res://assets/dialogue/%s.json" % dialogue_id
	if not FileAccess.file_exists(path):
		push_warning("DialogueManager: missing dialogue file %s" % path)
		return
	var raw := FileAccess.get_file_as_string(path)
	var parsed: Variant = JSON.parse_string(raw)
	if typeof(parsed) != TYPE_ARRAY:
		push_warning("DialogueManager: expected a JSON array in %s" % path)
		return
	_present_dialogue(parsed as Array)


func _present_dialogue(nodes: Array) -> void:
	var lines: PackedStringArray = []
	for item in nodes:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var d: Dictionary = item
		var speaker := str(d.get("speaker", ""))
		var text := str(d.get("text", ""))
		if speaker.is_empty():
			lines.append(text)
		else:
			lines.append("%s: %s" % [speaker, text])
	var dlg := AcceptDialog.new()
	dlg.name = "DialogueBootstrap"
	dlg.title = "Dialogue"
	dlg.dialog_text = "\n\n".join(lines)
	get_tree().root.add_child(dlg)
	dlg.popup_centered()
	dlg.confirmed.connect(dlg.queue_free)
	dlg.close_requested.connect(dlg.queue_free)

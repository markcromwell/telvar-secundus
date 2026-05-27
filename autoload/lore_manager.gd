extends Node
## Autoload: shows lore by id (JSON under res://assets/lore/<id>.json).


func show(lore_id: String) -> void:
	var path := "res://assets/lore/%s.json" % lore_id
	if not FileAccess.file_exists(path):
		push_error("LoreManager: missing lore file: %s" % path)
		return
	var text := FileAccess.get_file_as_string(path)
	if text.is_empty():
		push_error("LoreManager: empty lore file: %s" % path)
		return
	var parsed: Variant = JSON.parse_string(text)
	if parsed == null:
		push_error("LoreManager: invalid JSON: %s" % path)
		return
	# Full lore UI is owned by other specs; this validates and logs for now.
	print_debug("[LoreManager] show: ", lore_id)

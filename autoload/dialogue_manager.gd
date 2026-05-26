extends Node
## Autoload: starts dialogue by id (JSON under res://assets/dialogue/<id>.json).


func start(dialogue_id: String) -> void:
	var path := "res://assets/dialogue/%s.json" % dialogue_id
	if not FileAccess.file_exists(path):
		push_error("DialogueManager: missing dialogue file: %s" % path)
		return
	var text := FileAccess.get_file_as_string(path)
	if text.is_empty():
		push_error("DialogueManager: empty dialogue file: %s" % path)
		return
	var parsed: Variant = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("DialogueManager: invalid JSON (expected object): %s" % path)
		return
	# Full presentation UI is owned by other specs; this validates and logs for now.
	print_debug("[DialogueManager] start: ", dialogue_id, " nodes=", parsed.get("nodes", []).size())

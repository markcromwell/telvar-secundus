extends Node

## Autoload-friendly dialogue state and flag hooks. Call `show_dialogue` then drive
## the conversation with `get_current_node`, `select_choice`, and `try_advance_linear`.

var _flags: Dictionary = {}

var _dialogue_by_id: Dictionary = {}
var _active_npc_id: String = ""
var _current_node_id: String = ""

signal dialogue_started(npc_id: String)
signal dialogue_ended(npc_id: String)
signal dialogue_node_changed(node_id: String)
## Emitted when a choice grants a quest; HUD layers can show "New Quest!" for `duration`.
signal hud_toast_requested(message: String, duration: float)
## Mirrors journal-style tracking for UI that lists active story entries.
signal journal_quest_added(quest_id: String)
signal shop_open_requested
signal lore_unlock_requested(lore_id: String)

var _flag_in_text: RegEx


func _ready() -> void:
	_flag_in_text = RegEx.new()
	_flag_in_text.compile("\\[(quest_give|quest_complete|shop_open|lore_unlock)(?::([^\\]]+))?\\]")


func set_flag(key: String, value: Variant) -> void:
	_flags[key] = value


func get_flag(key: String) -> Variant:
	return _flags.get(key, null)


func show_dialogue(npc_id: String, dialogue_json: Variant) -> void:
	_dialogue_by_id.clear()
	_active_npc_id = npc_id
	_current_node_id = ""

	var arr: Array = _coerce_dialogue_array(dialogue_json)
	if arr.is_empty():
		push_error("DialogueManager: dialogue_json must be a non-empty JSON array (or parseable string).")
		return

	for item in arr:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var row: Dictionary = item
		if not row.has("id"):
			continue
		_dialogue_by_id[str(row["id"])] = row

	if _dialogue_by_id.has("start"):
		_current_node_id = "start"
	else:
		var first: Variant = arr[0]
		if typeof(first) == TYPE_DICTIONARY and first.has("id"):
			_current_node_id = str(first["id"])
		else:
			push_error("DialogueManager: could not determine starting dialogue node.")
			return

	dialogue_started.emit(_active_npc_id)
	dialogue_node_changed.emit(_current_node_id)


func get_current_node() -> Dictionary:
	if _current_node_id.is_empty() or not _dialogue_by_id.has(_current_node_id):
		return {}
	return (_dialogue_by_id[_current_node_id] as Dictionary).duplicate(true)


func select_choice(choice_index: int) -> void:
	var node := get_current_node()
	if node.is_empty():
		return
	var choices: Array = node.get("choices", [])
	if choice_index < 0 or choice_index >= choices.size():
		return
	if typeof(choices[choice_index]) != TYPE_DICTIONARY:
		return
	var choice: Dictionary = choices[choice_index]
	_process_choice_flags(choice)
	var nxt := str(choice.get("next", ""))
	if nxt.is_empty():
		_finish_dialogue()
	else:
		_current_node_id = nxt
		dialogue_node_changed.emit(_current_node_id)


func try_advance_linear() -> void:
	var node := get_current_node()
	if node.is_empty():
		return
	if not (node.get("choices", []) as Array).is_empty():
		return
	var nxt := str(node.get("next", ""))
	if nxt.is_empty():
		_finish_dialogue()
	else:
		_current_node_id = nxt
		dialogue_node_changed.emit(_current_node_id)


func _finish_dialogue() -> void:
	var ended_for := _active_npc_id
	_dialogue_by_id.clear()
	_current_node_id = ""
	_active_npc_id = ""
	dialogue_ended.emit(ended_for)


func _coerce_dialogue_array(dialogue_json: Variant) -> Array:
	if dialogue_json is Array:
		return dialogue_json
	if dialogue_json is String:
		var json := JSON.new()
		if json.parse(dialogue_json) != OK:
			push_error("DialogueManager: invalid JSON string for dialogue.")
			return []
		var data := json.get_data()
		if typeof(data) != TYPE_ARRAY:
			push_error("DialogueManager: dialogue JSON root must be an array.")
			return []
		return data
	push_error("DialogueManager: dialogue_json must be String or Array.")
	return []


func _process_choice_flags(choice: Dictionary) -> void:
	var tokens: Array[String] = []
	var raw_flags: Variant = choice.get("flags", [])
	if raw_flags is Array:
		for f in raw_flags:
			var norm := _normalize_flag_token(str(f))
			if not norm.is_empty():
				tokens.append(norm)
	for embedded in _flags_from_choice_text(str(choice.get("text", ""))):
		tokens.append(embedded)
	for t in tokens:
		_dispatch_dialogue_flag(t)


func _normalize_flag_token(raw: String) -> String:
	var s := raw.strip_edges()
	if s.length() >= 2 and s.begins_with("[") and s.ends_with("]"):
		s = s.substr(1, s.length() - 2).strip_edges()
	return s


func _flags_from_choice_text(text: String) -> Array[String]:
	var out: Array[String] = []
	var offset := 0
	while true:
		var m := _flag_in_text.search(text, offset)
		if m == null:
			break
		var kind := m.get_string(1)
		var arg := m.get_string(2)
		if arg.is_empty():
			out.append(kind)
		else:
			out.append("%s:%s" % [kind, arg])
		offset = m.get_end()
	return out


func _dispatch_dialogue_flag(token: String) -> void:
	if token.is_empty():
		return
	var parts := token.split(":", true, 1)
	var head := parts[0] if parts.size() > 0 else ""
	var tail := parts[1] if parts.size() > 1 else ""
	match head:
		"quest_give":
			if tail.is_empty():
				push_warning("DialogueManager: quest_give requires a quest id (quest_give:some_id).")
				return
			_apply_quest_give(tail)
		"quest_complete":
			if tail.is_empty():
				push_warning("DialogueManager: quest_complete requires a quest id.")
				return
			_apply_quest_complete(tail)
		"shop_open":
			shop_open_requested.emit()
		"lore_unlock":
			if tail.is_empty():
				push_warning("DialogueManager: lore_unlock requires a lore id.")
				return
			_apply_lore_unlock(tail)
		_:
			pass


func _apply_quest_give(quest_id: String) -> void:
	QuestManager.start_quest(quest_id)
	journal_quest_added.emit(quest_id)
	hud_toast_requested.emit("New Quest!", 2.0)


func _apply_quest_complete(quest_id: String) -> void:
	if not QuestManager.quests.has(quest_id):
		return
	var quest: Dictionary = QuestManager.quests[quest_id]
	var list: Array = quest.get("objectives", [])
	var pending: Array[String] = []
	for item in list:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var row: Dictionary = item
		if not row.get("complete", false):
			pending.append(str(row.get("id", "")))
	for obj_id in pending:
		if obj_id.is_empty():
			continue
		QuestManager.complete_objective(quest_id, obj_id)


func _apply_lore_unlock(lore_id: String) -> void:
	set_flag("lore_unlocked:" + lore_id, true)
	lore_unlock_requested.emit(lore_id)

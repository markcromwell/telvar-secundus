extends Control

## UI for one dialogue node: speaker, body text, and choice buttons.
## On choice, runs `_process_flags` for `flags` entries shaped like `[quest_give:id]`.

@onready var _name_label: Label = $VBoxContainer/NameLabel
@onready var _text_label: Label = $VBoxContainer/TextLabel
@onready var _choices_container: VBoxContainer = $VBoxContainer/ChoicesContainer

var _flag_regex: RegEx


func _ready() -> void:
	_flag_regex = RegEx.new()
	_flag_regex.compile(
		"\\[(quest_give|quest_complete|shop_open|lore_unlock)(?::([^\\]]+))?\\]"
	)


func populate(entry: Dictionary) -> void:
	for child in _choices_container.get_children():
		_choices_container.remove_child(child)
		child.queue_free()

	_name_label.text = str(entry.get("speaker", ""))
	_text_label.text = str(entry.get("text", ""))

	var choices: Array = entry.get("choices", [])
	for item in choices:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var choice: Dictionary = item
		var btn := Button.new()
		btn.text = str(choice.get("text", ""))
		btn.pressed.connect(_on_choice_button_pressed.bind(choice))
		_choices_container.add_child(btn)


func _on_choice_button_pressed(choice: Dictionary) -> void:
	_on_choice_selected(choice)


func _on_choice_selected(choice: Dictionary) -> void:
	_process_flags(choice)


func _process_flags(choice: Dictionary) -> void:
	if not choice.has("flags"):
		return
	var raw: Variant = choice.get("flags", [])
	if typeof(raw) != TYPE_ARRAY:
		return
	for flag_item in raw:
		_dispatch_flag_tokens(str(flag_item))


func _dispatch_flag_tokens(blob: String) -> void:
	var results := _flag_regex.search_all(blob)
	for m in results:
		var kind := m.get_string(1)
		var payload := m.get_string(2)
		match kind:
			"quest_give":
				var qid := payload.strip_edges()
				if qid.is_empty():
					continue
				QuestManager.start_quest(qid)
				DialogueManager._show_hud_notification("New Quest!")
			"quest_complete":
				var parts := payload.split(":", true, 1)
				if parts.size() < 2:
					continue
				QuestManager.complete_objective(parts[0].strip_edges(), parts[1].strip_edges())
			"shop_open":
				DialogueManager.set_flag("shop_open", true)
			"lore_unlock":
				DialogueManager.set_flag("lore_unlock", payload.strip_edges())

extends Area2D

## Lore shelf: random JSON entry on interact (ui_accept).

const LORE_PATH := "res://data/library_lore.json"

var _prompt: Label
var _player_inside := false
var _lore_entries: Array = []
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_prompt = _resolve_prompt()
	_rng.randomize()
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	_load_lore()


func _process(_delta: float) -> void:
	if not _player_inside:
		return
	if Input.is_action_just_pressed("ui_accept"):
		_show_random_lore()


func _on_body_entered(body: Node) -> void:
	if body.is_in_group("player"):
		_player_inside = true
		if _prompt:
			_prompt.visible = true
			_prompt.text = "Press E (Enter) to inspect shelf"


func _on_body_exited(body: Node) -> void:
	if body.is_in_group("player"):
		_player_inside = false
		if _prompt:
			_prompt.visible = false
			_prompt.text = ""


func _load_lore() -> void:
	if not FileAccess.file_exists(LORE_PATH):
		push_warning("Missing lore file: %s" % LORE_PATH)
		return
	var f := FileAccess.open(LORE_PATH, FileAccess.READ)
	if f == null:
		push_warning("Could not open lore file: %s" % LORE_PATH)
		return
	var parsed = JSON.parse_string(f.get_as_text())
	if typeof(parsed) == TYPE_ARRAY:
		_lore_entries = parsed
	else:
		push_warning("library_lore.json must be a JSON array")


func _show_random_lore() -> void:
	if _lore_entries.is_empty():
		_emit_popup("Empty shelf", "Dust and a scrap of ribbon — nothing readable here.")
		return
	var entry: Dictionary = _lore_entries[_rng.randi_range(0, _lore_entries.size() - 1)]
	var title: String = str(entry.get("title", "Lore"))
	var body: String = str(entry.get("body", ""))
	var lore_id: String = str(entry.get("id", "unknown"))
	_emit_popup(title, body)
	get_tree().call_group("inventory_hooks", "on_lore_inspected", lore_id)


func _emit_popup(title: String, body: String) -> void:
	var popup := get_tree().root.get_node_or_null("/root/LibraryLorePopup")
	if popup and popup.has_method("show_message"):
		popup.call("show_message", title, body, "")
		return
	var local_popup: Node = get_tree().current_scene.get_node_or_null("UI/LorePopup")
	if local_popup and local_popup.has_method("show_message"):
		local_popup.call("show_message", title, body, "")
		return
	print("[Library lore] ", title, " — ", body)


func _resolve_prompt() -> Label:
	var lib := get_tree().current_scene
	if lib:
		return lib.get_node_or_null("UI/PromptLabel") as Label
	return null

extends Area2D

@export var npc_id: String = ""
@export var portrait: Texture2D

var _player_in_range: bool = false


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	monitoring = true


func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("player"):
		_player_in_range = true


func _on_body_exited(body: Node2D) -> void:
	if body.is_in_group("player"):
		_player_in_range = false


func _process(_delta: float) -> void:
	if not _player_in_range:
		return
	if Input.is_action_just_pressed("interact"):
		_load_dialogue()


func _load_dialogue() -> void:
	if npc_id.is_empty():
		push_warning("NPC: npc_id is empty; cannot load dialogue")
		return
	var path := "res://assets/dialogue/%s.json" % npc_id
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		push_error("NPC: could not open dialogue file: %s" % path)
		return
	var text := file.get_as_text()
	var parsed = JSON.parse_string(text)
	if typeof(parsed) != TYPE_ARRAY:
		push_error("NPC: dialogue JSON must be a top-level array: %s" % path)
		return
	DialogueManager.show_dialogue(npc_id, parsed as Array, portrait)

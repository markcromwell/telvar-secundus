extends Node2D
## Veneficturis apprentice friend NPC (phase 2687). LPC-layout walk sheet + JSON dialogue.
## Dialogue data: res://data/dialogue/apprentice_room_friends.json (keys: daran, yessa, corvin).

const PHASE_ID := 2687
const FRAME_SIZE := 32
const WALK_FRAMES := 4

@export var npc_id: String = "daran"
@export_file("*.json") var dialogue_json_path: String = "res://data/dialogue/apprentice_room_friends.json"
@export var sprite_texture: Texture2D

@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite2D

var _npc_block: Dictionary = {}


func _ready() -> void:
	_setup_walk_animations()
	_load_dialogue()


func _setup_walk_animations() -> void:
	if sprite_texture == null:
		push_error("%s: sprite_texture is not set" % name)
		return
	var frames := SpriteFrames.new()
	var anim_names := ["walk_down", "walk_left", "walk_right", "walk_up"]
	for row in anim_names.size():
		var anim := anim_names[row]
		frames.add_animation(anim)
		frames.set_animation_speed(anim, 8.0)
		frames.set_animation_loop(anim, true)
		for col in WALK_FRAMES:
			var at := AtlasTexture.new()
			at.atlas = sprite_texture
			at.region = Rect2(col * FRAME_SIZE, row * FRAME_SIZE, FRAME_SIZE, FRAME_SIZE)
			frames.add_frame(anim, at)
	animated_sprite.sprite_frames = frames
	animated_sprite.play("walk_down")


func _load_dialogue() -> void:
	var f := FileAccess.open(dialogue_json_path, FileAccess.READ)
	if f == null:
		push_error("%s: cannot open dialogue JSON: %s" % [name, dialogue_json_path])
		return
	var text := f.get_as_text()
	var parsed = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("%s: dialogue JSON root must be an object" % name)
		return
	var root: Dictionary = parsed
	if not root.has("npcs"):
		push_error("%s: dialogue JSON missing 'npcs'" % name)
		return
	var npcs: Dictionary = root["npcs"]
	if not npcs.has(npc_id):
		push_error("%s: no dialogue block for npc_id=%s" % [name, npc_id])
		return
	_npc_block = npcs[npc_id]


func get_display_name() -> String:
	return String(_npc_block.get("display_name", npc_id))


func get_personality_notes() -> String:
	return String(_npc_block.get("personality_notes", ""))


func get_entry_node_id() -> String:
	return String(_npc_block.get("entry_node", ""))


func get_dialogue_nodes() -> Dictionary:
	var nodes = _npc_block.get("nodes", null)
	return nodes if typeof(nodes) == TYPE_DICTIONARY else {}


func get_npc_id() -> String:
	return npc_id

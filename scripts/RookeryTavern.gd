extends Node2D

## Interior: Rookery Tavern (12×10 tiles @ 16px, 2× display scale).

const OVERWORLD_SCENE := "res://scenes/Overworld.tscn"
const STONE_FOOTSTEP := "res://assets/audio/sfx/stone_footstep.wav"
const TERRAIN_TEX := "res://assets/tilesets/lpc_terrain.png"

const GRID_W := 12
const GRID_H := 10

const ATLAS_FLOOR := Vector2i(3, 0)
const ATLAS_WALL := Vector2i(4, 0)
const ATLAS_TABLE_A := Vector2i(0, 0)
const ATLAS_TABLE_B := Vector2i(1, 0)
const ATLAS_FIRE_A := Vector2i(2, 0)
const ATLAS_FIRE_B := Vector2i(3, 0)

@onready var _tile_map: TileMapLayer = $TileMap
@onready var _exit_door: Area2D = $ExitDoor
@onready var _player: CharacterBody2D = $Player
@onready var _fade_rect: ColorRect = $FadeLayer/FadeRect

var _source_id: int = 0
var _footstep_stream: AudioStream
var _footstep_players: Array[AudioStreamPlayer] = []
var _footstep_index: int = 0
var _footstep_cooldown: float = 0.0
var _exiting: bool = false


func _ready() -> void:
	_player.motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	_setup_portraits()
	_source_id = _build_tile_set()
	_paint_room()
	_exit_door.body_entered.connect(_on_exit_door_body_entered)
	_init_footsteps()


func _physics_process(delta: float) -> void:
	if _exiting:
		return
	var dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	_player.velocity = dir * 120.0
	_player.move_and_slide()
	_update_footsteps(delta)


func _build_tile_set() -> int:
	var tex := load(TERRAIN_TEX) as Texture2D
	var atlas := TileSetAtlasSource.new()
	atlas.texture = tex
	atlas.texture_region_size = Vector2i(16, 16)
	var tw := int(tex.get_width() / atlas.texture_region_size.x)
	var th := int(tex.get_height() / atlas.texture_region_size.y)
	for x in range(tw):
		for y in range(th):
			atlas.create_tile(Vector2i(x, y))
	var ts := TileSet.new()
	var sid: int = ts.add_source(atlas)
	_tile_map.tile_set = ts
	return sid


func _paint_room() -> void:
	for y in range(GRID_H):
		for x in range(GRID_W):
			var cell := Vector2i(x, y)
			var is_wall := false
			if y == 0 or x == 0 or x == GRID_W - 1:
				is_wall = true
			elif y == GRID_H - 1 and (x != 5 and x != 6):
				is_wall = true
			if is_wall:
				_tile_map.set_cell(cell, _source_id, ATLAS_WALL)
			else:
				_tile_map.set_cell(cell, _source_id, ATLAS_FLOOR)
	# Tables (long center table)
	_tile_map.set_cell(Vector2i(4, 6), _source_id, ATLAS_TABLE_A)
	_tile_map.set_cell(Vector2i(5, 6), _source_id, ATLAS_TABLE_B)
	_tile_map.set_cell(Vector2i(6, 6), _source_id, ATLAS_TABLE_A)
	# Fireplace cluster (north-west interior)
	_tile_map.set_cell(Vector2i(2, 2), _source_id, ATLAS_FIRE_A)
	_tile_map.set_cell(Vector2i(3, 2), _source_id, ATLAS_FIRE_B)
	_tile_map.set_cell(Vector2i(2, 3), _source_id, ATLAS_FIRE_B)
	_tile_map.set_cell(Vector2i(3, 3), _source_id, ATLAS_FIRE_A)


func _setup_portraits() -> void:
	var fig1: Node2D = $HoodedFigure1
	var fig2: Node2D = $HoodedFigure2
	fig1.get_node("Sprite2D").texture = load("res://assets/portraits/hooded_figure_1.png")
	fig2.get_node("Sprite2D").texture = load("res://assets/portraits/hooded_figure_2.png")


func _init_footsteps() -> void:
	_footstep_stream = load(STONE_FOOTSTEP) as AudioStream
	for _i in 2:
		var p := AudioStreamPlayer.new()
		p.name = "StoneFootstepPlayer%d" % i
		p.stream = _footstep_stream
		add_child(p)
		_footstep_players.append(p)


func _update_footsteps(delta: float) -> void:
	_footstep_cooldown = maxf(_footstep_cooldown - delta, 0.0)
	if _player.velocity.length_squared() < 25.0:
		return
	if _footstep_cooldown > 0.0:
		return
	_play_pooled_footstep()
	_footstep_cooldown = 0.22


func _play_pooled_footstep() -> void:
	if _footstep_players.is_empty():
		return
	var p: AudioStreamPlayer = _footstep_players[_footstep_index]
	_footstep_index = (_footstep_index + 1) % _footstep_players.size()
	if p.playing:
		p.stop()
	p.play()


func _on_exit_door_body_entered(body: Node) -> void:
	if _exiting:
		return
	if body != _player:
		return
	_exiting = true
	_player.velocity = Vector2.ZERO
	set_physics_process(false)
	var tw := create_tween()
	tw.tween_property(_fade_rect, "modulate:a", 1.0, 0.5)
	await tw.finished
	get_tree().change_scene_to_file(OVERWORLD_SCENE)

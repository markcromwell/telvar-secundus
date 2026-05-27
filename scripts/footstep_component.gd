class_name FootstepComponent
extends Node

## Plays periodic footstep SFX based on TileMap custom data `floor_type` ("wood" / "stone").
## Expects parent `CharacterBody2D`. Uses child `RayCast2D` and `AudioStreamPlayer`.

const DEFAULT_MOVE_THRESHOLD_PX: float = 10.0
const DEFAULT_STEP_INTERVAL_SEC: float = 0.35
const DEFAULT_RAY_LENGTH_PX: float = 56.0

const _WOOD_STREAM := preload("res://assets/audio/sfx/footstep_wood.ogg")
const _STONE_STREAM := preload("res://assets/audio/sfx/footstep_stone.ogg")

@export var move_speed_threshold: float = DEFAULT_MOVE_THRESHOLD_PX
@export var step_interval_sec: float = DEFAULT_STEP_INTERVAL_SEC
@export var ray_length_px: float = DEFAULT_RAY_LENGTH_PX

@onready var _body: CharacterBody2D = get_parent() as CharacterBody2D
@onready var _ray: RayCast2D = $RayCast2D
@onready var _player: AudioStreamPlayer = $AudioStreamPlayer

var _step_cooldown: float = 0.0


func _ready() -> void:
	if _body == null:
		push_warning("FootstepComponent: parent must be CharacterBody2D; disabling.")
		set_physics_process(false)
		return
	if _ray:
		_ray.target_position = Vector2(0.0, ray_length_px)
		_ray.collide_with_areas = false
		_ray.enabled = true
		_ray.add_exception(_body)
	if _player:
		_player.stream = _STONE_STREAM


func _physics_process(delta: float) -> void:
	if _body == null or _ray == null or _player == null:
		return
	if not is_instance_valid(_body):
		return
	if "can_move" in _body and not _body.can_move:
		return

	if _body.velocity.length() <= move_speed_threshold:
		_step_cooldown = 0.0
		return

	_ray.force_raycast_update()
	var floor_key := _read_floor_type_from_ray()
	if floor_key.is_empty():
		floor_key = "stone"
	_set_stream_for_floor(floor_key)

	_step_cooldown -= delta
	if _step_cooldown > 0.0:
		return
	_step_cooldown = step_interval_sec
	_player.play()


func _read_floor_type_from_ray() -> String:
	if not _ray.is_colliding():
		return ""
	var collider: Object = _ray.get_collider()
	var hit_point: Vector2 = _ray.get_collision_point()
	var node := collider as Node
	if node == null:
		return ""
	if node is TileMapLayer:
		return _floor_type_from_tile_map_layer(node as TileMapLayer, hit_point)
	if node is TileMap:
		return _floor_type_from_legacy_tile_map(node as TileMap, hit_point)
	var parent_tm := _find_parent_tile_map(node)
	if parent_tm:
		return _floor_type_from_legacy_tile_map(parent_tm, hit_point)
	return ""


func _floor_type_from_tile_map_layer(layer: TileMapLayer, hit_point: Vector2) -> String:
	var local := layer.to_local(hit_point)
	var coords := layer.local_to_map(local)
	return _floor_type_from_tile_data(layer.get_cell_tile_data(coords))


func _floor_type_from_legacy_tile_map(tile_map: TileMap, hit_point: Vector2) -> String:
	var local := tile_map.to_local(hit_point)
	var coords := tile_map.local_to_map(local)
	for layer_idx in range(tile_map.get_layers_count()):
		var tile_data: TileData = tile_map.get_cell_tile_data(layer_idx, coords)
		var ft := _floor_type_from_tile_data(tile_data)
		if not ft.is_empty():
			return ft
	return ""


func _floor_type_from_tile_data(tile_data: TileData) -> String:
	if tile_data == null:
		return ""
	var raw: Variant = tile_data.get_custom_data(&"floor_type")
	if raw == null:
		return ""
	var s := str(raw).strip_edges().to_lower()
	return s


func _find_parent_tile_map(node: Node) -> TileMap:
	var current: Node = node
	while current:
		if current is TileMap:
			return current as TileMap
		current = current.get_parent()
	return null


func _set_stream_for_floor(floor_key: String) -> void:
	var want_wood := floor_key == "wood"
	var stream: AudioStream = _WOOD_STREAM if want_wood else _STONE_STREAM
	if _player.stream != stream:
		_player.stream = stream

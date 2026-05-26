extends CharacterBody2D

## Top-down player with grid-aligned footstep SFX (one click every 32 rendered pixels).
## Footsteps route through the **SFXManager** autoload so they use the **SFX** bus.

const FOOTSTEP_DISTANCE_PX := 32.0

@export var speed: float = 64.0  ## pixels/sec (2 tiles at 32px)
@export var can_move: bool = true
## Optional layer painted with wood-floor tiles (planks). When unset, footsteps use stone.
@export var wood_floor_tiles: TileMapLayer
## Sample point offset from `global_position` (feet vs body center).
@export var footstep_sample_offset: Vector2 = Vector2(0, 8)
@export var footstep_stone: AudioStream
@export var footstep_wood: AudioStream

var _distance_since_footstep: float = 0.0


func _physics_process(_delta: float) -> void:
	if not can_move:
		velocity = Vector2.ZERO
		move_and_slide()
		return

	var dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	velocity = dir * speed
	var pos_before := global_position
	move_and_slide()
	var moved := pos_before.distance_to(global_position)
	if moved <= 0.0:
		return
	_distance_since_footstep += moved
	while _distance_since_footstep >= FOOTSTEP_DISTANCE_PX:
		_distance_since_footstep -= FOOTSTEP_DISTANCE_PX
		_play_footstep()


func _play_footstep() -> void:
	var mat := _footstep_material()
	var stream: AudioStream = footstep_stone if mat == "stone" else footstep_wood
	if stream == null and mat != "stone":
		stream = footstep_stone
	if stream == null:
		return
	SFXManager.play(stream)


func _footstep_material() -> String:
	if wood_floor_tiles == null:
		return "stone"
	var local := wood_floor_tiles.to_local(global_position + footstep_sample_offset)
	var coords := wood_floor_tiles.local_to_map(local)
	if wood_floor_tiles.get_cell_source_id(coords) != -1:
		return "wood"
	return "stone"

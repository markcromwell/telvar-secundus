extends Node2D

## Builds StaticBody2D colliders for the rope cordon (shelf rows use TileSet physics on shelf atlas tiles).
## TileSet collision on wall/shelf tiles covers perimeter and stacks; rope decor has no tile physics.

const MAP_WIDTH := 30
const MAP_HEIGHT := 20
const CELL := 16

const ROPE_TILE_X := 21
const INNER_TOP_TILE_Y := 1
const INNER_BOTTOM_TILE_Y := MAP_HEIGHT - 2
const ROPE_BARRIER_WIDTH := CELL


func _ready() -> void:
	_add_rope_barrier()


func _add_rope_barrier() -> void:
	var height := (INNER_BOTTOM_TILE_Y - INNER_TOP_TILE_Y + 1) * CELL
	var center := Vector2(
		ROPE_TILE_X * CELL + CELL / 2.0,
		INNER_TOP_TILE_Y * CELL + height / 2.0
	)
	var body := StaticBody2D.new()
	body.name = "rope_barrier"
	body.collision_layer = 1
	body.collision_mask = 1
	body.position = center
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(ROPE_BARRIER_WIDTH, height)
	shape.shape = rect
	body.add_child(shape)
	add_child(body)

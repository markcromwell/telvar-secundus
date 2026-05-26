extends Node2D

## Builds StaticBody2D colliders for the rope cordon (shelf rows use TileSet physics on shelf atlas tiles).
## TileSet collision on wall/shelf tiles covers perimeter and stacks; rope decor has no tile physics.

const MAP_WIDTH := 30
const MAP_HEIGHT := 20
const CELL := 16

const ROPE_TILE_X := 21


func _ready() -> void:
	_add_rope_barrier()


func _add_rope_barrier() -> void:
	var height := (MAP_HEIGHT - 4) * CELL
	var x := ROPE_TILE_X * CELL + CELL / 2.0
	var y := 2 * CELL + height / 2.0
	var body := StaticBody2D.new()
	body.name = "rope_barrier"
	body.collision_layer = 1
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(6, height)
	shape.position = Vector2(x, y)
	shape.shape = rect
	body.add_child(shape)
	add_child(body)

extends Node2D

## Builds StaticBody2D colliders for perimeter walls, shelf backs, and the rope cordon.
## TileSet collision is optional; this keeps the scene reliable without editor-generated physics.

const MAP_WIDTH := 30
const MAP_HEIGHT := 20
const CELL := 16

const ROPE_TILE_X := 21

## Must match `SHELF_ROWS` in library_tilemap.gd (aisle layout depends on both staying aligned).
const SHELF_ROWS := [4, 7, 10, 13, 16, 18]


func _ready() -> void:
	_add_shelf_row_colliders()
	_add_rope_barrier()


func _add_rect(r: Rect2, node_name: String) -> void:
	var body := StaticBody2D.new()
	body.name = node_name
	body.collision_layer = 1
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = r.size
	shape.position = r.position + r.size / 2.0
	shape.shape = rect
	body.add_child(shape)
	add_child(body)


func _add_shelf_row_colliders() -> void:
	for row_y in SHELF_ROWS:
		_add_rect(Rect2(2 * CELL, row_y * CELL, 6 * CELL, CELL), "shelf_row_%d_a" % row_y)
		_add_rect(Rect2(11 * CELL, row_y * CELL, 6 * CELL, CELL), "shelf_row_%d_b" % row_y)
		_add_rect(Rect2(20 * CELL, row_y * CELL, 6 * CELL, CELL), "shelf_row_%d_c" % row_y)


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

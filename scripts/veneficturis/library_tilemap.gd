extends TileMap

## Veneficturis Library floor grid (16×16 source tiles; project uses 2× content scale for crisp pixels).
const MAP_WIDTH := 30
const MAP_HEIGHT := 20

const SOURCE_ID := 0
const ATLAS_FLOOR := Vector2i(0, 0)
const ATLAS_WALL := Vector2i(1, 0)
const ATLAS_SHELF := Vector2i(2, 0)
const ATLAS_TABLE := Vector2i(3, 0)
const ATLAS_ROPE := Vector2i(4, 0)

const LAYER_FLOOR := 0
const LAYER_DECOR := 1

## Six horizontal shelf rows (y indices), leaving aisles between blocks.
const SHELF_ROWS := [4, 7, 10, 13, 16, 18]

## Horizontal shelf blocks (tile x indices). Must stay aligned with `library_physics.gd` shelf StaticBody2D rects.
const SHELF_SEGMENTS := [[2, 3, 4, 5, 6, 7], [11, 12, 13, 14, 15, 16], [20, 21, 22, 23, 24, 25]]

const _SHELF_INSPECT_SCRIPT := preload("res://scripts/veneficturis/shelf_inspect.gd")
const _CELL_PX := 16

func _ready() -> void:
	clear()
	_paint_floor()
	_paint_walls()
	_paint_shelves()
	_paint_reading_tables()
	_paint_rope_decor()
	_setup_shelf_inspection_zones()


func _paint_floor() -> void:
	for y in range(MAP_HEIGHT):
		for x in range(MAP_WIDTH):
			set_cell(LAYER_FLOOR, Vector2i(x, y), SOURCE_ID, ATLAS_FLOOR)


func _paint_walls() -> void:
	for x in range(MAP_WIDTH):
		set_cell(LAYER_DECOR, Vector2i(x, 0), SOURCE_ID, ATLAS_WALL)
		if x != MAP_WIDTH / 2 and x != MAP_WIDTH / 2 - 1:
			set_cell(LAYER_DECOR, Vector2i(x, MAP_HEIGHT - 1), SOURCE_ID, ATLAS_WALL)
	for y in range(MAP_HEIGHT):
		set_cell(LAYER_DECOR, Vector2i(0, y), SOURCE_ID, ATLAS_WALL)
		set_cell(LAYER_DECOR, Vector2i(MAP_WIDTH - 1, y), SOURCE_ID, ATLAS_WALL)


func _paint_shelves() -> void:
	for row_y in SHELF_ROWS:
		_paint_shelf_row(row_y)


func _paint_shelf_row(row_y: int) -> void:
	for seg in SHELF_SEGMENTS:
		for x in seg:
			set_cell(LAYER_DECOR, Vector2i(x, row_y), SOURCE_ID, ATLAS_SHELF)


func _setup_shelf_inspection_zones() -> void:
	var shelves: Node2D = get_parent().get_node_or_null("Shelves") as Node2D
	if shelves == null:
		push_warning("Veneficturis Library: no Shelves node; skipping shelf Area2D setup")
		return
	for child in shelves.get_children().duplicate():
		child.free()
	for row_y in SHELF_ROWS:
		for seg in SHELF_SEGMENTS:
			var x_lo: int = int(seg[0])
			var x_hi: int = int(seg[seg.size() - 1])
			var width_px := float((x_hi - x_lo + 1) * _CELL_PX)
			var cx := float((x_lo + x_hi + 1) * 0.5 * _CELL_PX)
			var cy := float(row_y * _CELL_PX + _CELL_PX * 0.5)
			var area := Area2D.new()
			area.name = "ShelfInspect_%d_%d" % [row_y, x_lo]
			area.collision_layer = 1
			area.collision_mask = 1
			area.position = Vector2(cx, cy)
			area.set_script(_SHELF_INSPECT_SCRIPT)
			var shape_node := CollisionShape2D.new()
			var rect_shape := RectangleShape2D.new()
			rect_shape.size = Vector2(width_px, float(_CELL_PX))
			shape_node.shape = rect_shape
			area.add_child(shape_node)
			shelves.add_child(area)


func _paint_reading_tables() -> void:
	var table_positions := [Vector2i(8, 17), Vector2i(15, 17), Vector2i(25, 17)]
	for p in table_positions:
		set_cell(LAYER_DECOR, p, SOURCE_ID, ATLAS_TABLE)


func _paint_rope_decor() -> void:
	var rope_x := 21
	for y in range(2, MAP_HEIGHT - 2):
		set_cell(LAYER_DECOR, Vector2i(rope_x, y), SOURCE_ID, ATLAS_ROPE)

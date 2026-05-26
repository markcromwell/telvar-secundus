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

func _ready() -> void:
	clear()
	_paint_floor()
	_paint_walls()
	_paint_shelves()
	_paint_reading_tables()
	_paint_rope_decor()


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
	var segments := [
		[2, 3, 4, 5, 6, 7],
		[11, 12, 13, 14, 15, 16],
		[20, 21, 22, 23, 24, 25],
	]
	for seg in segments:
		for x in seg:
			set_cell(LAYER_DECOR, Vector2i(x, row_y), SOURCE_ID, ATLAS_SHELF)


func _paint_reading_tables() -> void:
	var table_positions := [Vector2i(8, 17), Vector2i(15, 17), Vector2i(25, 17)]
	for p in table_positions:
		set_cell(LAYER_DECOR, p, SOURCE_ID, ATLAS_TABLE)


func _paint_rope_decor() -> void:
	var rope_x := 21
	for y in range(2, MAP_HEIGHT - 2):
		set_cell(LAYER_DECOR, Vector2i(rope_x, y), SOURCE_ID, ATLAS_ROPE)

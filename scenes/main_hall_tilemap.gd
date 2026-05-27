extends TileMap

## Veneficturis main hall hub: 15×12 floor with two south doorways to wings (LPC atlas).
const SOURCE: int = 0
const LAYER: int = 0

const FLOOR_STONE := Vector2i(1, 0)
const FLOOR_WOOD := Vector2i(3, 0)
const WALL := Vector2i(2, 0)


func _ready() -> void:
	_paint_main_hall()


func _cell(x: int, y: int, atlas: Vector2i) -> void:
	set_cell(LAYER, Vector2i(x, y), SOURCE, atlas)


func _fill_rect(x0: int, y0: int, x1: int, y1: int, atlas: Vector2i) -> void:
	for y in range(y0, y1 + 1):
		for x in range(x0, x1 + 1):
			_cell(x, y, atlas)


func _paint_main_hall() -> void:
	clear()
	_fill_rect(1, 1, 13, 10, FLOOR_STONE)
	# Aisle emphasis toward the south doors
	_fill_rect(2, 8, 12, 10, FLOOR_WOOD)

	# Perimeter walls with two openings on the south (Classroom west, Laboratory east)
	_fill_rect(0, 0, 14, 0, WALL)
	_fill_rect(0, 11, 14, 11, WALL)
	_fill_rect(0, 1, 0, 10, WALL)
	_fill_rect(14, 1, 14, 10, WALL)
	_cell(3, 11, FLOOR_WOOD)
	_cell(4, 11, FLOOR_WOOD)
	_cell(10, 11, FLOOR_WOOD)
	_cell(11, 11, FLOOR_WOOD)

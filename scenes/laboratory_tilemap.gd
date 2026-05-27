extends TileMap

## Veneficturis Laboratory: 15x12 room with benches, potion racks, and apparatus (LPC atlas).
const SOURCE: int = 0
const LAYER: int = 0

const FLOOR_STONE := Vector2i(1, 0)
const WALL := Vector2i(2, 0)
const BENCH := Vector2i(7, 0)
const POTION_RACK := Vector2i(8, 0)
const APPARATUS := Vector2i(9, 0)


func _ready() -> void:
	_paint_laboratory()


func _cell(x: int, y: int, atlas: Vector2i) -> void:
	set_cell(LAYER, Vector2i(x, y), SOURCE, atlas)


func _fill_rect(x0: int, y0: int, x1: int, y1: int, atlas: Vector2i) -> void:
	for y in range(y0, y1 + 1):
		for x in range(x0, x1 + 1):
			_cell(x, y, atlas)


func _paint_laboratory() -> void:
	clear()
	# Baseworking floor
	_fill_rect(1, 1, 13, 10, FLOOR_STONE)

	# Perimeter walls
	_fill_rect(0, 0, 14, 0, WALL)
	_fill_rect(0, 11, 14, 11, WALL)
	_fill_rect(0, 1, 0, 10, WALL)
	_fill_rect(14, 1, 14, 10, WALL)

	# Benches
	_fill_rect(3, 3, 11, 3, BENCH)
	_fill_rect(3, 6, 11, 6, BENCH)
	_fill_rect(3, 9, 11, 9, BENCH)

	# Apparatus on benches
	_cell(4, 3, APPARATUS)
	_cell(8, 3, APPARATUS)
	_cell(10, 3, APPARATUS)
	
	_cell(5, 6, APPARATUS)
	_cell(7, 6, APPARATUS)
	_cell(9, 6, APPARATUS)

	# Potion racks along the walls
	_cell(1, 1, POTION_RACK)
	_cell(2, 1, POTION_RACK)
	_cell(12, 1, POTION_RACK)
	_cell(13, 1, POTION_RACK)
	
	_cell(1, 10, POTION_RACK)
	_cell(2, 10, POTION_RACK)
	_cell(12, 10, POTION_RACK)
	_cell(13, 10, POTION_RACK)

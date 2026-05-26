extends TileMap

## Veneficturis practice hall: 15×12 tiered seating and training props (LPC atlas).
const SOURCE: int = 0
const LAYER: int = 0

const FLOOR_BOARD := Vector2i(0, 0)
const FLOOR_STONE := Vector2i(1, 0)
const WALL := Vector2i(2, 0)
const FLOOR_WOOD := Vector2i(3, 0)
const TRAIN_MAT := Vector2i(4, 0)
const TIER_STEP := Vector2i(5, 0)
const CHAIR := Vector2i(6, 0)
const BENCH := Vector2i(7, 0)
const EQUIP_RACK := Vector2i(8, 0)
const APPARATUS := Vector2i(9, 0)
const LECTERN := Vector2i(0, 1)


func _ready() -> void:
	_paint_classroom()


func _cell(x: int, y: int, atlas: Vector2i) -> void:
	set_cell(LAYER, Vector2i(x, y), SOURCE, atlas)


func _fill_rect(x0: int, y0: int, x1: int, y1: int, atlas: Vector2i) -> void:
	for y in range(y0, y1 + 1):
		for x in range(x0, x1 + 1):
			_cell(x, y, atlas)


func _paint_classroom() -> void:
	clear()
	# Baseworking floor (stone under risers; wood from the front aisle down)
	_fill_rect(1, 1, 13, 10, FLOOR_STONE)
	_fill_rect(2, 7, 12, 10, FLOOR_WOOD)

	# Perimeter walls
	_fill_rect(0, 0, 14, 0, WALL)
	_fill_rect(0, 11, 14, 11, WALL)
	_fill_rect(0, 1, 0, 10, WALL)
	_fill_rect(14, 1, 14, 10, WALL)

	# Front training floor: mats + apparatus bays
	_fill_rect(2, 8, 12, 9, TRAIN_MAT)
	_cell(3, 7, APPARATUS)
	_cell(7, 7, APPARATUS)
	_cell(11, 7, APPARATUS)
	_cell(2, 7, EQUIP_RACK)
	_cell(12, 7, EQUIP_RACK)

	# Lectern / instructor station (Myramar's drills)
	_cell(7, 9, LECTERN)
	_cell(6, 9, FLOOR_BOARD)
	_cell(8, 9, FLOOR_BOARD)

	# Tiered seating toward the north: three risers with benches + chairs
	# Tier 1 (back)
	_fill_rect(2, 2, 12, 2, TIER_STEP)
	_fill_rect(2, 1, 12, 1, BENCH)
	for x in range(3, 12, 2):
		_cell(x, 1, CHAIR)

	# Tier 2
	_fill_rect(2, 4, 12, 4, TIER_STEP)
	_fill_rect(2, 3, 12, 3, BENCH)
	for x in range(4, 11, 2):
		_cell(x, 3, CHAIR)

	# Tier 3 (closest to training floor)
	_fill_rect(2, 6, 12, 6, TIER_STEP)
	_fill_rect(2, 5, 12, 5, BENCH)
	for x in range(3, 12, 2):
		_cell(x, 5, CHAIR)

	# Side equipment along east/west aisles
	for y in range(3, 6):
		_cell(1, y, EQUIP_RACK)
		_cell(13, y, EQUIP_RACK)

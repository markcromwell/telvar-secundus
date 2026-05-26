extends Node2D

## Veneficturis Main Hall — phase 2620 tilemap bootstrap.
## 20×15 cells at 16×16 px tiles (project display uses 2× content scale).

const MAP_SIZE := Vector2i(20, 15)
const SOURCE_ID := 0

const ATLAS_FLOOR := Vector2i(0, 0)
const ATLAS_WALL := Vector2i(1, 0)
const ATLAS_ARCH := Vector2i(2, 0)
const ATLAS_DESK := Vector2i(3, 0)

@onready var _floor: TileMapLayer = $HallTileMap/Floor
@onready var _ceiling: TileMapLayer = $HallTileMap/CeilingDecor


func _ready() -> void:
	_floor.clear()
	_ceiling.clear()
	_paint_perimeter_and_floor()
	_paint_arched_ceiling_band()
	_place_reception_desk()


func _is_door_cell(p: Vector2i) -> bool:
	if p == Vector2i(10, 0):
		return true
	if p == Vector2i(10, MAP_SIZE.y - 1):
		return true
	if p == Vector2i(0, 7):
		return true
	if p == Vector2i(MAP_SIZE.x - 1, 7):
		return true
	return false


func _is_perimeter(p: Vector2i) -> bool:
	return p.x == 0 or p.y == 0 or p.x == MAP_SIZE.x - 1 or p.y == MAP_SIZE.y - 1


func _paint_perimeter_and_floor() -> void:
	for y in range(MAP_SIZE.y):
		for x in range(MAP_SIZE.x):
			var cell := Vector2i(x, y)
			if _is_perimeter(cell) and not _is_door_cell(cell):
				_floor.set_cell(cell, SOURCE_ID, ATLAS_WALL)
			else:
				_floor.set_cell(cell, SOURCE_ID, ATLAS_FLOOR)


func _paint_arched_ceiling_band() -> void:
	# Vaulted ceiling strip along the north interior (arched LPC detail layer).
	for y in range(1, 3):
		for x in range(1, MAP_SIZE.x - 1):
			_ceiling.set_cell(Vector2i(x, y), SOURCE_ID, ATLAS_ARCH)


func _place_reception_desk() -> void:
	# Reception counter south of center, facing the hall (does not cover the south door).
	for x in range(8, 12):
		_floor.set_cell(Vector2i(x, 13), SOURCE_ID, ATLAS_DESK)

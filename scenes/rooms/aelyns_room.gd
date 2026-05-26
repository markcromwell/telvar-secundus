extends Node2D
## Phase 2691 — Aelyn's quarters: cleared by apprentice runners — no kit, no furniture, only the floor note.

@onready var _floor: TileMapLayer = $Floor


func _ready() -> void:
	_paint_room()


func _paint_room() -> void:
	var width := 12
	var height := 10
	var door_x := width // 2
	for y in range(height):
		for x in range(width):
			var coords := Vector2i(x, y)
			var is_wall := x == 0 or x == width - 1 or y == 0 or y == height - 1
			if y == height - 1 and x == door_x:
				is_wall = false
			var atlas := Vector2i(1, 0) if is_wall else Vector2i(0, 0)
			_floor.set_cell(coords, 0, atlas)

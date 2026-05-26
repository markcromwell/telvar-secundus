extends Node2D

## Fills the child TileMap named "Floor" with a single atlas tile for the whole grid.
@export var cells_x: int = 24
@export var cells_y: int = 16

@onready var _floor: TileMap = $Floor


func _ready() -> void:
	for x in range(cells_x):
		for y in range(cells_y):
			_floor.set_cell(0, Vector2i(x, y), 0, Vector2i(0, 0))

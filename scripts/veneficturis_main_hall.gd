extends Node2D

## Veneficturis Main Hall — phase 2620 tilemap bootstrap.
## 20×15 cells at 16×16 px tiles (project display uses 2× content scale).

signal transition_requested(room_name: String)
signal dialogue_shown(text: String)

const MAP_SIZE := Vector2i(20, 15)
const SOURCE_ID := 0

const ATLAS_FLOOR := Vector2i(0, 0)
const ATLAS_WALL := Vector2i(1, 0)
const ATLAS_ARCH := Vector2i(2, 0)
const ATLAS_DESK := Vector2i(3, 0)

@onready var _floor: TileMapLayer = $HallTileMap/Floor
@onready var _ceiling: TileMapLayer = $HallTileMap/CeilingDecor

var has_shown_letter := false
var _door_blockers: Array[StaticBody2D] = []


func _ready() -> void:
	_floor.clear()
	_ceiling.clear()
	_paint_perimeter_and_floor()
	_paint_arched_ceiling_band()
	_place_reception_desk()
	_setup_doors()
	_setup_receptionist()


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

func _setup_doors() -> void:
	_create_door(Vector2i(10, 0), "Library")
	_create_door(Vector2i(10, MAP_SIZE.y - 1), "Tower")
	_create_door(Vector2i(0, 7), "Classroom")
	_create_door(Vector2i(MAP_SIZE.x - 1, 7), "Lab")


func _create_door(cell: Vector2i, room_name: String) -> void:
	var pos := Vector2(cell.x * 16 + 8, cell.y * 16 + 8)
	
	var area := Area2D.new()
	area.name = room_name + "DoorArea"
	var coll := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(16, 16)
	coll.shape = shape
	area.position = pos
	area.body_entered.connect(_on_door_body_entered.bind(room_name))
	add_child(area)
	
	var blocker := StaticBody2D.new()
	blocker.name = room_name + "Blocker"
	var b_coll := CollisionShape2D.new()
	var b_shape := RectangleShape2D.new()
	b_shape.size = Vector2(16, 16)
	b_coll.shape = b_shape
	blocker.position = pos
	add_child(blocker)
	_door_blockers.append(blocker)


func _on_door_body_entered(_body: Node2D, room_name: String) -> void:
	if has_shown_letter:
		transition_requested.emit(room_name)
	else:
		dialogue_shown.emit("Receptionist: Halt! Show your admission letter first.")


func _setup_receptionist() -> void:
	var npc := Area2D.new()
	npc.name = "ReceptionNPC"
	var coll := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(64, 32)
	coll.shape = shape
	# Place at reception desk (x: 8 to 11, y: 13). Center is 10*16
	npc.position = Vector2(10 * 16, 13 * 16)
	npc.body_entered.connect(_on_receptionist_body_entered)
	add_child(npc)


func _on_receptionist_body_entered(_body: Node2D) -> void:
	if not has_shown_letter:
		dialogue_shown.emit("Receptionist: Halt! Show your admission letter first.")


func show_letter() -> void:
	has_shown_letter = true
	dialogue_shown.emit("Receptionist: A letter from Myramar? Very well, proceed.")
	for blocker in _door_blockers:
		if is_instance_valid(blocker):
			blocker.queue_free()
	_door_blockers.clear()

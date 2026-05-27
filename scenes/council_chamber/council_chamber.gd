extends Node2D
## Council Chamber: 12×12 circular floor plan (LPC terrain), table, chairs,
## and Tower stairs transition trigger at the south landing.

const GRID_SIZE := 12
const TILE_LAYER := 0
const SOURCE_ID := 0
const TILE_PX := 16
const TILE_SCALE := 2.0

const ATLAS_FLOOR := Vector2i(0, 0)
const ATLAS_WALL := Vector2i(1, 0)
const ATLAS_TABLE := Vector2i(2, 0)
const ATLAS_CHAIR := Vector2i(3, 0)

## Squared radius for stone floor (center 5.5, 5.5 in cell space).
const FLOOR_R2 := 30.25
## South doorway cells for return to Tower stairs (y ≥ 10, x 5–6).
const STAIRS_DOOR_MIN := Vector2i(5, 10)
const STAIRS_DOOR_MAX := Vector2i(6, 11)
## South-west landing for Myramar's office (Act 2+).
const OFFICE_DOOR_MIN := Vector2i(2, 11)
const OFFICE_DOOR_MAX := Vector2i(3, 11)

@onready var _terrain: TileMap = $Terrain
@onready var _tower_stairs_exit: Area2D = $TowerStairsExit
@onready var _office_door: Area2D = $OfficeDoor


func _ready() -> void:
	_build_circle()
	_build_furniture()
	_place_tower_stairs_area()
	_place_office_door_area()
	_office_door.body_entered.connect(_on_office_door_body_entered)


func _build_circle() -> void:
	for x in GRID_SIZE:
		for y in GRID_SIZE:
			var dx := float(x) - 5.5
			var dy := float(y) - 5.5
			var dist_sq := dx * dx + dy * dy
			var is_floor := dist_sq <= FLOOR_R2 or _is_stairs_landing(x, y) or _is_office_landing(x, y)
			var atlas := ATLAS_FLOOR if is_floor else ATLAS_WALL
			_terrain.set_cell(TILE_LAYER, Vector2i(x, y), SOURCE_ID, atlas)


func _is_stairs_landing(x: int, y: int) -> bool:
	return x >= STAIRS_DOOR_MIN.x and x <= STAIRS_DOOR_MAX.x and y >= STAIRS_DOOR_MIN.y and y <= STAIRS_DOOR_MAX.y


func _is_office_landing(x: int, y: int) -> bool:
	return x >= OFFICE_DOOR_MIN.x and x <= OFFICE_DOOR_MAX.x and y >= OFFICE_DOOR_MIN.y and y <= OFFICE_DOOR_MAX.y


func _build_furniture() -> void:
	# Central council table (2×1 cells) and chairs on the long sides.
	_terrain.set_cell(TILE_LAYER, Vector2i(5, 5), SOURCE_ID, ATLAS_TABLE)
	_terrain.set_cell(TILE_LAYER, Vector2i(6, 5), SOURCE_ID, ATLAS_TABLE)
	_terrain.set_cell(TILE_LAYER, Vector2i(4, 5), SOURCE_ID, ATLAS_CHAIR)
	_terrain.set_cell(TILE_LAYER, Vector2i(7, 5), SOURCE_ID, ATLAS_CHAIR)
	_terrain.set_cell(TILE_LAYER, Vector2i(5, 4), SOURCE_ID, ATLAS_CHAIR)
	_terrain.set_cell(TILE_LAYER, Vector2i(6, 4), SOURCE_ID, ATLAS_CHAIR)


func _place_tower_stairs_area() -> void:
	# Center over the two south doorway floor tiles (cells 5–6, row 11).
	var cx := (float(STAIRS_DOOR_MIN.x) + float(STAIRS_DOOR_MAX.x) + 1.0) * 0.5
	var cy := float(STAIRS_DOOR_MAX.y) + 0.5
	var px := cx * TILE_PX * TILE_SCALE
	var py := cy * TILE_PX * TILE_SCALE
	_tower_stairs_exit.position = Vector2(px, py)


func _place_office_door_area() -> void:
	var cx := (float(OFFICE_DOOR_MIN.x) + float(OFFICE_DOOR_MAX.x) + 1.0) * 0.5
	var cy := float(OFFICE_DOOR_MAX.y) + 0.5
	var px := cx * TILE_PX * TILE_SCALE
	var py := cy * TILE_PX * TILE_SCALE
	_office_door.position = Vector2(px, py)


func _on_office_door_body_entered(body: Node) -> void:
	if not body.is_in_group("player"):
		return
	if int(DialogueManager.get_flag("act", 1)) >= 2:
		get_tree().change_scene_to_file("res://scenes/myramar_office/myramar_office.tscn")
	else:
		DialogueManager.show_message(
			"The mentor's office stays sealed until the story moves into Act II.",
			"Narrator",
		)

extends Node2D
## Myramar's office: 10×8 LPC room, desk / bookshelf / cabinet, mentor NPC,
## return door to the council chamber. Act 2+ only (otherwise player is sent back).

const OFFICE_W := 10
const OFFICE_H := 8
const TILE_LAYER := 0
const SOURCE_ID := 0
const TILE_PX := 16
const TILE_SCALE := 2.0

const ATLAS_FLOOR := Vector2i(0, 0)
const ATLAS_WALL := Vector2i(1, 0)
const ATLAS_DESK := Vector2i(4, 0)
const ATLAS_BOOKSHELF := Vector2i(5, 0)
const ATLAS_CABINET := Vector2i(6, 0)

const MYRAMAR_DIALOGUE := "res://assets/dialogue/myramar.json"

## South exit cells (two floor tiles).
const EXIT_MIN := Vector2i(4, OFFICE_H - 1)
const EXIT_MAX := Vector2i(5, OFFICE_H - 1)

@onready var _terrain: TileMap = $Terrain
@onready var _myramar_area: Area2D = $MyramarTalkArea
@onready var _desk_area: Area2D = $DeskInspectArea
@onready var _council_return: Area2D = $CouncilReturn

var _player_near_myramar := false
var _player_near_desk := false


func _ready() -> void:
	if int(DialogueManager.get_flag("act", 1)) < 2:
		DialogueManager.show_message(
			"The office door is warded shut until the academy moves you into Act II.",
			"Narrator",
			Callable(self, "_return_to_council"),
		)
		return
	_build_room()
	_place_exit_area()
	_myramar_area.body_entered.connect(_on_myramar_body_entered)
	_myramar_area.body_exited.connect(_on_myramar_body_exited)
	_desk_area.body_entered.connect(_on_desk_body_entered)
	_desk_area.body_exited.connect(_on_desk_body_exited)
	_council_return.body_entered.connect(_on_council_return_body_entered)


func _physics_process(_delta: float) -> void:
	if int(DialogueManager.get_flag("act", 1)) < 2:
		return
	if not Input.is_action_just_pressed("ui_accept"):
		return
	if _player_near_myramar:
		DialogueManager.show_dialogue("myramar", MYRAMAR_DIALOGUE, "start")
	elif _player_near_desk:
		if int(DialogueManager.get_flag("act", 1)) >= 2:
			DialogueManager.show_dialogue("myramar", MYRAMAR_DIALOGUE, "desk")
		else:
			DialogueManager.show_message(
				"You glance at the desk, but the papers feel… out of reach for now.",
				"Narrator",
			)


func _return_to_council() -> void:
	get_tree().change_scene_to_file("res://scenes/council_chamber/council_chamber.tscn")


func _build_room() -> void:
	for x in OFFICE_W:
		for y in OFFICE_H:
			var is_exit := y == OFFICE_H - 1 and x >= EXIT_MIN.x and x <= EXIT_MAX.x
			var wall := x == 0 or y == 0 or x == OFFICE_W - 1 or y == OFFICE_H - 1
			if wall and not is_exit:
				_terrain.set_cell(TILE_LAYER, Vector2i(x, y), SOURCE_ID, ATLAS_WALL)
			else:
				_terrain.set_cell(TILE_LAYER, Vector2i(x, y), SOURCE_ID, ATLAS_FLOOR)
	# North wall desk (two tiles), east bookshelf strip, west cabinet.
	_terrain.set_cell(TILE_LAYER, Vector2i(4, 1), SOURCE_ID, ATLAS_DESK)
	_terrain.set_cell(TILE_LAYER, Vector2i(5, 1), SOURCE_ID, ATLAS_DESK)
	for yy in range(2, 6):
		_terrain.set_cell(TILE_LAYER, Vector2i(OFFICE_W - 2, yy), SOURCE_ID, ATLAS_BOOKSHELF)
	_terrain.set_cell(TILE_LAYER, Vector2i(1, 3), SOURCE_ID, ATLAS_CABINET)
	_terrain.set_cell(TILE_LAYER, Vector2i(1, 4), SOURCE_ID, ATLAS_CABINET)


func _place_exit_area() -> void:
	var cx := (float(EXIT_MIN.x) + float(EXIT_MAX.x) + 1.0) * 0.5
	var cy := float(EXIT_MAX.y) + 0.5
	_council_return.position = Vector2(cx * TILE_PX * TILE_SCALE, cy * TILE_PX * TILE_SCALE)


func _on_myramar_body_entered(body: Node) -> void:
	if body.is_in_group("player"):
		_player_near_myramar = true


func _on_myramar_body_exited(body: Node) -> void:
	if body.is_in_group("player"):
		_player_near_myramar = false


func _on_desk_body_entered(body: Node) -> void:
	if body.is_in_group("player"):
		_player_near_desk = true


func _on_desk_body_exited(body: Node) -> void:
	if body.is_in_group("player"):
		_player_near_desk = false


func _on_council_return_body_entered(body: Node) -> void:
	if body.is_in_group("player"):
		get_tree().change_scene_to_file("res://scenes/council_chamber/council_chamber.tscn")

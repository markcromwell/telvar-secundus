extends Node2D

## Paints a small apprentice room when the scene loads.
##
## Why programmatic: avoiding hand-encoded Godot 4 TileMap tile_data
## packed arrays — the .tscn binary format for layer_0/tile_data is
## tedious to author without the Godot editor. _ready() paints in
## under a frame; player can walk immediately.
##
## Room layout (16-px tiles):
##   - 20 cols x 15 rows interior floor (320 x 240 px)
##   - solid walls around the perimeter via StaticBody2D + CollisionShape2D
##   - player spawns at the centre

const ROOM_COLS := 20
const ROOM_ROWS := 15
const TILE_SIZE := 16

@onready var tile_map: TileMap = $TileMap
@onready var player: CharacterBody2D = $Player


func _ready() -> void:
	_paint_floor()
	_build_walls()
	_centre_player()


func _paint_floor() -> void:
	# Atlas source 0 with atlas tile (0, 0) is the dark stone floor tile
	# registered in lpc_dark_stone_tileset.tres.
	for x in ROOM_COLS:
		for y in ROOM_ROWS:
			tile_map.set_cell(0, Vector2i(x, y), 0, Vector2i(0, 0))


func _build_walls() -> void:
	var walls := Node2D.new()
	walls.name = "Walls"
	add_child(walls)

	# Wall thickness 16 px; placed JUST OUTSIDE the painted room so the
	# player can walk on every floor tile but bounces off the edge.
	var thickness := 16.0
	var room_w := ROOM_COLS * TILE_SIZE
	var room_h := ROOM_ROWS * TILE_SIZE

	# top, bottom, left, right
	var specs := [
		{"pos": Vector2(room_w * 0.5, -thickness * 0.5),
		 "size": Vector2(room_w + thickness * 2, thickness)},
		{"pos": Vector2(room_w * 0.5, room_h + thickness * 0.5),
		 "size": Vector2(room_w + thickness * 2, thickness)},
		{"pos": Vector2(-thickness * 0.5, room_h * 0.5),
		 "size": Vector2(thickness, room_h)},
		{"pos": Vector2(room_w + thickness * 0.5, room_h * 0.5),
		 "size": Vector2(thickness, room_h)},
	]
	for spec in specs:
		var body := StaticBody2D.new()
		body.position = spec["pos"]
		var shape := CollisionShape2D.new()
		var rect := RectangleShape2D.new()
		rect.size = spec["size"]
		shape.shape = rect
		body.add_child(shape)
		# Visible wall — dark grey so the player can see the boundary.
		var visual := ColorRect.new()
		visual.color = Color(0.15, 0.13, 0.12, 1.0)
		visual.size = spec["size"]
		visual.position = -spec["size"] * 0.5
		body.add_child(visual)
		walls.add_child(body)


func _centre_player() -> void:
	var room_w := ROOM_COLS * TILE_SIZE
	var room_h := ROOM_ROWS * TILE_SIZE
	player.position = Vector2(room_w * 0.5, room_h * 0.5)

	# Player needs a CollisionShape2D so it actually collides with walls.
	if not player.has_node("CollisionShape2D"):
		var shape := CollisionShape2D.new()
		shape.name = "CollisionShape2D"
		var rect := RectangleShape2D.new()
		rect.size = Vector2(12, 12)
		shape.shape = rect
		player.add_child(shape)

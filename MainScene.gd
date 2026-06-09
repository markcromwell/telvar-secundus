extends Node2D

## Apprentice room: 30x20 dark-stone floor with collision walls and a
## visible player sprite.
##
## Why programmatic: avoids hand-encoded Godot 4 TileMap tile_data
## packed arrays — _ready() paints in under a frame.

const ROOM_COLS := 30
const ROOM_ROWS := 20
const TILE_SIZE := 16

@onready var tile_map: TileMap = $TileMap
@onready var player: CharacterBody2D = $Player


func _ready() -> void:
	_paint_floor()
	_build_walls()
	_setup_player()
	_start_music()


func _paint_floor() -> void:
	for x in ROOM_COLS:
		for y in ROOM_ROWS:
			tile_map.set_cell(0, Vector2i(x, y), 0, Vector2i(0, 0))


func _build_walls() -> void:
	var walls := Node2D.new()
	walls.name = "Walls"
	add_child(walls)

	var thickness := 16.0
	var room_w := ROOM_COLS * TILE_SIZE
	var room_h := ROOM_ROWS * TILE_SIZE

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
		var visual := ColorRect.new()
		# Warm stone wall colour so it reads as a built room not a void.
		visual.color = Color(0.35, 0.28, 0.20, 1.0)
		visual.size = spec["size"]
		visual.position = -spec["size"] * 0.5
		body.add_child(visual)
		walls.add_child(body)


func _setup_player() -> void:
	var room_w := ROOM_COLS * TILE_SIZE
	var room_h := ROOM_ROWS * TILE_SIZE
	player.position = Vector2(room_w * 0.5, room_h * 0.5)

	# Player needs a visible Sprite2D so the operator can see them.
	if not player.has_node("PlayerSprite"):
		var sprite := Sprite2D.new()
		sprite.name = "PlayerSprite"
		var tex := load("res://assets/sprites/myramar_placeholder.png")
		if tex:
			sprite.texture = tex
			# Scale down — placeholders may be much larger than 16px.
			if tex.get_width() > 32:
				sprite.scale = Vector2(0.25, 0.25)
		player.add_child(sprite)

	# Player needs collision so they bounce off walls.
	if not player.has_node("CollisionShape2D"):
		var shape := CollisionShape2D.new()
		shape.name = "CollisionShape2D"
		var rect := RectangleShape2D.new()
		rect.size = Vector2(12, 12)
		shape.shape = rect
		player.add_child(shape)


func _start_music() -> void:
	# Audio that survives the browser autoplay policy: start AFTER scene
	# load, because by the time MainScene loads the user has already
	# clicked "New Game" on the menu.
	var stream := load("res://audio/music/music_loop_maldita.ogg") as AudioStreamOggVorbis
	if stream == null:
		return
	stream.loop = true
	var ap := AudioStreamPlayer.new()
	ap.name = "GameMusic"
	ap.stream = stream
	ap.bus = "Music"
	ap.volume_db = -8.0
	ap.autoplay = false
	add_child(ap)
	ap.play()

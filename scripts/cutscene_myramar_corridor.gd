extends Node2D
## Final corridor beat: Myramar line, then hand off to scrolling credits and end screen scenes.

const DIALOGUE_LINE := "And so it begins."

@onready var _tile_map: TileMap = $CorridorFloor
@onready var _myramar_sprite: Sprite2D = $Myramar/Sprite2D
@onready var _ui_layer: CanvasLayer = $UILayer

var _dialogue_label: Label


func _ready() -> void:
	_setup_corridor_visuals()
	_setup_dialogue_ui()
	_run_sequence()


func _setup_corridor_visuals() -> void:
	var tex: Texture2D = load("res://assets/tilesets/lpc_terrain.png")
	var tile_set := TileSet.new()
	var atlas := TileSetAtlasSource.new()
	atlas.texture = tex
	atlas.texture_region_size = Vector2i(16, 16)
	var source_id := tile_set.add_source(atlas)
	_tile_map.tile_set = tile_set
	for x in range(-8, 48):
		for y in range(-4, 14):
			var ax := abs(x) % 4
			var ay := abs(y) % 2
			_tile_map.set_cell(0, Vector2i(x, y), source_id, Vector2i(ax, ay))
	_myramar_sprite.texture = tex
	_myramar_sprite.region_enabled = true
	_myramar_sprite.region_rect = Rect2(0, 0, 16, 32)
	_myramar_sprite.centered = true


func _setup_dialogue_ui() -> void:
	_dialogue_label = Label.new()
	_dialogue_label.text = DIALOGUE_LINE
	_dialogue_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_dialogue_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_dialogue_label.add_theme_font_size_override("font_size", 28)
	var dwrap := MarginContainer.new()
	dwrap.set_anchors_preset(Control.PRESET_FULL_RECT)
	dwrap.add_child(_dialogue_label)
	_dialogue_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	_ui_layer.add_child(dwrap)
	dwrap.name = "DialogueWrap"
	_dialogue_label.visible = true


func _run_sequence() -> void:
	await get_tree().create_timer(3.5).timeout
	if is_instance_valid(_dialogue_label.get_parent()):
		_dialogue_label.get_parent().queue_free()
	GameSession.credits_exit_to_main_menu = false
	get_tree().change_scene_to_file("res://scenes/credits_roll.tscn")

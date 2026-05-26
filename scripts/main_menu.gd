extends Control
## Title menu: New Game, Load Game (embedded load screen), Quit.


const WORLD_SCENE := "res://scenes/world.tscn"
const LOAD_SCENE := "res://scenes/load_screen.tscn"

@onready var _main_buttons: Control = $MainPanel
@onready var _load_layer: Control = $LoadLayer
@onready var _load_host: Control = $LoadLayer/LoadLayerVBox/LoadHost

var _load_screen_instance: Control


func _ready() -> void:
	_load_layer.visible = false
	get_tree().paused = false


func _on_new_game_pressed() -> void:
	var err: Error = get_tree().change_scene_to_file(WORLD_SCENE)
	if err != OK:
		push_error("MainMenu: failed to open world: %d" % err)


func _on_load_game_pressed() -> void:
	_main_buttons.visible = false
	_load_layer.visible = true
	if _load_screen_instance == null:
		var ps: PackedScene = load(LOAD_SCENE) as PackedScene
		_load_screen_instance = ps.instantiate() as Control
		_load_host.add_child(_load_screen_instance)
	else:
		_load_screen_instance.visible = true


func _on_load_back_pressed() -> void:
	_load_layer.visible = false
	_main_buttons.visible = true
	if _load_screen_instance:
		_load_screen_instance.visible = false


func _on_quit_pressed() -> void:
	get_tree().quit()

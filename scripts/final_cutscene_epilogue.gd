extends Control
## Phase 2716 — Final epilogue: dawn over Secundus, timed text panels via AnimationPlayer.
## Phase 2717 — On completion, persist NG+ unlock to the active save slot, then show end UI.
## Skip actions are swallowed until the full epilogue animation has finished.

const PANEL_HOLD_SECONDS: float = 4.0
const FADE_IN_SECONDS: float = 1.0
const FADE_OUT_SECONDS: float = 1.0
const MAIN_MENU_SCENE: String = "res://scenes/main_menu.tscn"

@onready var _anim: AnimationPlayer = $AnimationPlayer
@onready var _canvas: CanvasLayer = $CanvasLayer
@onready var _fade: ColorRect = $CanvasLayer/FadeOverlay
@onready var _end_screen: CanvasLayer = $EndScreen
@onready var _main_menu_button: Button = $EndScreen/VBox/MainMenuButton

var _labels: Array[Label] = []
var _epilogue_complete: bool = false


func _ready() -> void:
	set_process_unhandled_input(true)
	_labels = [
		_canvas.get_node("LabelPanel1") as Label,
		_canvas.get_node("LabelPanel2") as Label,
		_canvas.get_node("LabelPanel3") as Label,
		_canvas.get_node("LabelPanel4") as Label,
	]
	_build_epilogue_animation()
	_anim.animation_finished.connect(_on_epilogue_animation_finished)
	_anim.play(&"final_cut/epilogue")


func _build_epilogue_animation() -> void:
	var anim := Animation.new()
	anim.loop_mode = Animation.LOOP_NONE

	var n: int = _labels.size()
	var panels_end: float = FADE_IN_SECONDS + float(n) * PANEL_HOLD_SECONDS
	anim.length = panels_end + FADE_OUT_SECONDS

	# Full-screen fade overlay (black): opaque → clear during intro, clear → opaque at end.
	var fade_track: int = anim.add_track(Animation.TYPE_VALUE)
	anim.track_set_path(fade_track, _fade_path())
	anim.track_set_interpolation_type(fade_track, Animation.INTERPOLATION_LINEAR)
	anim.value_track_set_update_mode(fade_track, Animation.UPDATE_CONTINUOUS)
	anim.track_insert_key(fade_track, 0.0, Color(0.0, 0.0, 0.0, 1.0))
	anim.track_insert_key(fade_track, FADE_IN_SECONDS, Color(0.0, 0.0, 0.0, 0.0))
	anim.track_insert_key(fade_track, panels_end, Color(0.0, 0.0, 0.0, 0.0))
	anim.track_insert_key(fade_track, panels_end + FADE_OUT_SECONDS, Color(0.0, 0.0, 0.0, 1.0))

	for i in n:
		var label: Label = _labels[i]
		var tr: int = anim.add_track(Animation.TYPE_VALUE)
		anim.track_set_path(tr, _label_visible_path(label))
		anim.track_set_interpolation_type(tr, Animation.INTERPOLATION_NEAREST)
		anim.value_track_set_update_mode(tr, Animation.UPDATE_DISCRETE)
		var t_on: float = FADE_IN_SECONDS + float(i) * PANEL_HOLD_SECONDS
		var t_off: float = FADE_IN_SECONDS + float(i + 1) * PANEL_HOLD_SECONDS
		anim.track_insert_key(tr, 0.0, false)
		anim.track_insert_key(tr, t_on, true)
		anim.track_insert_key(tr, t_off, false)

	var lib := AnimationLibrary.new()
	lib.add_animation(&"epilogue", anim)
	const LIB_NAME := &"final_cut"
	if _anim.has_animation_library(LIB_NAME):
		_anim.remove_animation_library(LIB_NAME)
	_anim.add_animation_library(LIB_NAME, lib)


func _fade_path() -> NodePath:
	return NodePath(str(get_path_to(_fade)) + ":color")


func _label_visible_path(label: Label) -> NodePath:
	return NodePath(str(get_path_to(label)) + ":visible")


func _on_epilogue_animation_finished(_anim_name: StringName) -> void:
	Inventory.unlock_ng_plus_for_active_slot()
	_epilogue_complete = true
	_end_screen.visible = true
	_main_menu_button.call_deferred(&"grab_focus")


func _unhandled_input(event: InputEvent) -> void:
	if not event.is_pressed():
		return
	if not _epilogue_complete:
		if event.is_action_pressed(&"ui_cancel") or event.is_action_pressed(&"ui_accept"):
			get_viewport().set_input_as_handled()


func _on_main_menu_pressed() -> void:
	if ResourceLoader.exists(MAIN_MENU_SCENE):
		get_tree().change_scene_to_file(MAIN_MENU_SCENE)

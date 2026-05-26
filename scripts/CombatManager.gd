extends Node

## Autoload: owns the combat UI layer. Call start_combat / end_combat from gameplay.

const COMBAT_UI_SCENE := preload("res://scenes/CombatUI.tscn")

var _combat_ui: CanvasLayer


func start_combat() -> void:
	if _combat_ui != null and is_instance_valid(_combat_ui):
		return
	_combat_ui = COMBAT_UI_SCENE.instantiate() as CanvasLayer
	get_tree().root.add_child(_combat_ui)
	if _combat_ui.has_method("show_combat"):
		_combat_ui.show_combat()


func end_combat(_victory: bool) -> void:
	if _combat_ui == null or not is_instance_valid(_combat_ui):
		_combat_ui = null
		return
	var ui := _combat_ui
	_combat_ui = null
	if ui.has_method("remove_combat_ui"):
		ui.remove_combat_ui()
	else:
		ui.queue_free()

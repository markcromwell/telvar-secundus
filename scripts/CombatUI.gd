extends CanvasLayer

## Full-screen dark tint and future combat HUD. Shown while a combat encounter is active.

@onready var _overlay: ColorRect = $DarkOverlay


func _ready() -> void:
	layer = 80
	hide_combat()


func show_combat() -> void:
	visible = true
	if is_instance_valid(_overlay):
		_overlay.visible = true


func hide_combat() -> void:
	visible = false
	if is_instance_valid(_overlay):
		_overlay.visible = false


func remove_combat_ui() -> void:
	hide_combat()
	queue_free()

extends Node2D

## Interior of the Cathedral of Aten: exit uses FadeTransition; call play_footstep for stone SFX.

@export var exit_target_scene: String = ""


func _ready() -> void:
	$ExitDoor.body_entered.connect(_on_exit_door_body_entered)
	_paint_interior_tiles()


func _paint_interior_tiles() -> void:
	var tm: TileMap = $TileMap
	const LAYER := 0
	const SOURCE := 0
	const VAULT_STONE := Vector2i(0, 0)
	const STAINED_GLASS := Vector2i(1, 0)
	const WARM_GLASS := Vector2i(0, 1)
	const FLOOR_STONE := Vector2i(1, 1)
	for x in range(-2, 36):
		for y in range(-2, 28):
			var c := Vector2i(x, y)
			var atlas: Vector2i
			if y < 0:
				atlas = VAULT_STONE
			elif y < 6:
				atlas = STAINED_GLASS if (x + y) % 2 == 0 else WARM_GLASS
			elif y < 8:
				atlas = VAULT_STONE if (x % 4) < 2 else WARM_GLASS
			else:
				atlas = FLOOR_STONE
			tm.set_cell(LAYER, c, SOURCE, atlas)


func _on_exit_door_body_entered(body: Node2D) -> void:
	if not body.is_in_group("player") and not (body is CharacterBody2D):
		return
	if exit_target_scene.is_empty():
		push_warning("CathedralOfAten: exit_target_scene is not set")
		return
	FadeTransition.fade_to(exit_target_scene)


func play_footstep() -> void:
	AudioManager.play_footstep_stone()

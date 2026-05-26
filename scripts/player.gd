extends CharacterBody2D
## Player spawn appearance: NG+ dark robe when the active slot has ``game_complete`` set.
## Expects optional ``AnimatedSprite2D`` (animations ``default`` / ``dark_robe``) or ``Sprite2D`` fallback.

@onready var _animated: AnimatedSprite2D = get_node_or_null("AnimatedSprite2D")
@onready var _sprite: Sprite2D = get_node_or_null("Sprite2D")


func _ready() -> void:
	_apply_save_appearance()


func _apply_save_appearance() -> void:
	var slot: int = ActiveSaveSlot.slot
	if not SaveSystem.is_slot_valid(slot):
		slot = SaveSystem.AUTOSAVE_SLOT
	var data: Dictionary = SaveSystem.load_from_slot(slot)
	var completed: bool = false
	if data.has("game_complete"):
		var gc: Variant = data["game_complete"]
		completed = typeof(gc) == TYPE_BOOL and bool(gc)
	if completed:
		_set_dark_robe_variant()
	else:
		_set_default_robe_variant()


func _set_default_robe_variant() -> void:
	if _animated != null:
		if _animated.sprite_frames != null and _animated.sprite_frames.has_animation("default"):
			_animated.animation = "default"
			_animated.play()
		_animated.modulate = Color.WHITE
	if _sprite != null:
		_sprite.modulate = Color.WHITE


func _set_dark_robe_variant() -> void:
	if _animated != null and _animated.sprite_frames != null and _animated.sprite_frames.has_animation("dark_robe"):
		_animated.animation = "dark_robe"
		_animated.play()
		_animated.modulate = Color.WHITE
	elif _animated != null:
		_animated.modulate = Color(0.42, 0.42, 0.52, 1.0)
	elif _sprite != null:
		_sprite.modulate = Color(0.42, 0.42, 0.52, 1.0)

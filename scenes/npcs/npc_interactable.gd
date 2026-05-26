extends StaticBody2D

## Dialogue JSON stem under `res://assets/dialogue/<dialogue_id>.json`.
@export var dialogue_id: String = ""


func _ready() -> void:
	var sprite := get_node_or_null("AnimatedSprite2D") as AnimatedSprite2D
	if sprite == null:
		return
	if sprite.sprite_frames != null and sprite.sprite_frames.get_animation_names().size() > 0:
		return
	var tex := PlaceholderTexture2D.new()
	tex.size = Vector2i(16, 32)
	var sf := SpriteFrames.new()
	sf.add_animation("default")
	sf.add_frame("default", tex)
	sprite.sprite_frames = sf
	sprite.play(&"default")

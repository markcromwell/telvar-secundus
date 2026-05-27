extends StaticBody2D

@export var dialogue_id: String = "npc"


func _ready() -> void:
	var anim := get_node_or_null("AnimatedSprite2D") as AnimatedSprite2D
	if anim == null or anim.sprite_frames != null:
		return
	var img := Image.create(16, 32, false, Image.FORMAT_RGBA8)
	img.fill(Color(0.45, 0.42, 0.5))
	var tex := ImageTexture.create_from_image(img)
	var fr := SpriteFrames.new()
	fr.add_animation("default")
	fr.add_frame("default", tex)
	anim.sprite_frames = fr
	anim.play("default")

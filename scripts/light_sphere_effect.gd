extends Node2D

## Visual for Light Sphere: radial PointLight2D sized to `RADIUS_TILES` world tiles.

const DURATION_SEC := 30.0
const RADIUS_TILES := 5
const TILE_WORLD_PX := 16

@onready var _light: PointLight2D = $PointLight2D


func _ready() -> void:
	var radius_px: float = float(RADIUS_TILES * TILE_WORLD_PX)
	_configure_light(radius_px)

	var expire := Timer.new()
	expire.one_shot = true
	expire.wait_time = DURATION_SEC
	add_child(expire)
	expire.timeout.connect(queue_free)
	expire.start()


func _configure_light(radius_px: float) -> void:
	var side := int(round(radius_px * 2.0))
	side = maxi(side, 2)

	var grad := Gradient.new()
	grad.colors = PackedColorArray([Color(1, 1, 1, 1), Color(1, 1, 1, 0)])
	grad.offsets = PackedFloat32Array([0.0, 1.0])

	var tex := GradientTexture2D.new()
	tex.gradient = grad
	tex.width = side
	tex.height = side
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(0.5, 0.0)

	_light.texture = tex
	_light.texture_scale = 1.0
	_light.offset = Vector2(-radius_px, -radius_px)
	_light.energy = 1.0

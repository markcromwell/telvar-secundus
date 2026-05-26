extends CanvasLayer

## Renders a small SubViewport overview plus overlay dots for `GameManager.KEY_LOCATIONS`.
## Location keys: Emporium, Temple, Cathedral, King's Keep, Veneficturis (see GameManager).

const _GM: GDScript = preload("res://scripts/GameManager.gd")

const MAP_SIZE := Vector2(160.0, 90.0)
const DOT_SIZE := Vector2(6.0, 6.0)

@onready var _subviewport: SubViewport = $SubViewportContainer/SubViewport
@onready var _camera: Camera2D = $SubViewportContainer/SubViewport/MinimapCamera
@onready var _markers: Control = $MarkersOverlay

var _world_bounds: Rect2


func _ready() -> void:
	var cmap: Dictionary = _GM.get_script_constant_map()
	var locations: Dictionary = cmap.get("KEY_LOCATIONS", {}) as Dictionary
	_world_bounds = _bounds_from_key_locations(locations)
	_configure_camera()
	call_deferred("_attach_shared_world")
	_place_key_location_markers(locations)


func _attach_shared_world() -> void:
	var vp := get_viewport()
	if vp and is_instance_valid(_subviewport):
		_subviewport.world_2d = vp.world_2d


func _bounds_from_key_locations(locations: Dictionary) -> Rect2:
	if locations.is_empty():
		return Rect2(Vector2.ZERO, MAP_SIZE)
	var mn := Vector2(INF, INF)
	var mx := Vector2(-INF, -INF)
	for p in locations.values():
		if p is Vector2:
			var v: Vector2 = p
			mn.x = minf(mn.x, v.x)
			mn.y = minf(mn.y, v.y)
			mx.x = maxf(mx.x, v.x)
			mx.y = maxf(mx.y, v.y)
	const margin := 80.0
	return Rect2(
		mn.x - margin,
		mn.y - margin,
		(mx.x - mn.x) + 2.0 * margin,
		(mx.y - mn.y) + 2.0 * margin
	)


func _configure_camera() -> void:
	_camera.enabled = true
	_camera.position = _world_bounds.get_center()
	var zx: float = _subviewport.size.x / maxf(_world_bounds.size.x, 1.0)
	var zy: float = _subviewport.size.y / maxf(_world_bounds.size.y, 1.0)
	var z: float = minf(zx, zy)
	_camera.zoom = Vector2(z, z)


func _place_key_location_markers(locations: Dictionary) -> void:
	for c in _markers.get_children():
		c.queue_free()
	for loc_key in locations.keys():
		var world_pos: Vector2 = locations[loc_key] as Vector2
		var rel := Vector2(
			(world_pos.x - _world_bounds.position.x) / maxf(_world_bounds.size.x, 1.0),
			(world_pos.y - _world_bounds.position.y) / maxf(_world_bounds.size.y, 1.0)
		)
		rel.x = clampf(rel.x, 0.0, 1.0)
		rel.y = clampf(rel.y, 0.0, 1.0)
		var center := Vector2(rel.x * MAP_SIZE.x, rel.y * MAP_SIZE.y)
		_add_marker(str(loc_key), center)


func _add_marker(full_name: String, center_px: Vector2) -> void:
	var wrap := Control.new()
	wrap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	wrap.z_index = 20
	wrap.position = center_px - DOT_SIZE * 0.5

	var dot := ColorRect.new()
	dot.size = DOT_SIZE
	dot.color = Color(0.95, 0.75, 0.15, 1.0)
	dot.z_index = 21
	wrap.add_child(dot)

	var label := Label.new()
	label.text = _label_for_location(full_name)
	label.add_theme_font_size_override("font_size", 9)
	label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
	label.add_theme_constant_override("outline_size", 3)
	label.position = Vector2(DOT_SIZE.x + 2.0, -1.0)
	label.z_index = 22
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	wrap.add_child(label)

	_markers.add_child(wrap)


func _label_for_location(full_name: String) -> String:
	# Short labels for the five KEY_LOCATIONS entries (Emporium, Temple, Cathedral, Keep, Veneficturis).
	if full_name.findn("emporium") != -1:
		return "Emporium"
	if full_name.findn("temple") != -1:
		return "Temple"
	if full_name.findn("cathedral") != -1:
		return "Cathedral"
	if full_name.findn("keep") != -1:
		return "Keep"
	if full_name.findn("veneficturis") != -1:
		return "Veneficturis"
	return full_name

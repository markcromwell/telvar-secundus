## Fills the OverworldMap TileMap from DistrictBounds (runtime; keeps .tscn free of huge cell blobs).
extends Object
class_name OverworldTilePopulator

const _WALL_ATLAS := Vector2i(0, 1)


static func populate(tilemap: TileMap) -> void:
	for layer in range(tilemap.get_layers_count()):
		tilemap.clear_layer(layer)
	for d in DistrictBounds.DISTRICTS:
		_paint_district(tilemap, d)


static func _paint_district(tilemap: TileMap, d: Dictionary) -> void:
	var layer: int = d["layer"]
	var source_id: int = d["source_id"]
	var floor_atlas: Vector2i = d["floor_atlas"]
	var r: Rect2i = d["rect"]
	var map_w := DistrictBounds.MAP_SIZE.x
	var map_h := DistrictBounds.MAP_SIZE.y
	for y in range(r.position.y, r.end.y):
		for x in range(r.position.x, r.end.x):
			var cell := Vector2i(x, y)
			var on_world_edge := (
				x == 0 or y == 0 or x == map_w - 1 or y == map_h - 1
			)
			var atlas := _WALL_ATLAS if on_world_edge else _jitter_floor(
				floor_atlas, x, y, d["id"]
			)
			tilemap.set_cell(layer, cell, source_id, atlas)

## Slight visual variety while keeping each district readable.
static func _jitter_floor(base: Vector2i, x: int, y: int, district_id: String) -> Vector2i:
	var h := hash(district_id) + x * 92837111 + y * 689287499
	var roll := int(abs(h)) % 5
	if roll == 0:
		return Vector2i(1, 0)
	if roll == 1:
		return Vector2i(2, 0)
	return base

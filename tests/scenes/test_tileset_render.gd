extends TileMap

const _EXPECTED_ATLAS = [
	Vector2i(0, 0), # stone_floor
	Vector2i(1, 0), # grass
	Vector2i(2, 0), # dirt
	Vector2i(0, 1), # wall
]

const _EXPECTED_NAMES = ["stone_floor", "grass", "dirt", "wall"]


func _ready() -> void:
	assert(tile_set != null, "TileMap.tile_set must reference lpc_terrain.tres")
	assert(tile_set.tile_size == Vector2i(32, 32), "TileSet tile_size must be 32x32 display cells")

	var src := tile_set.get_source(0) as TileSetAtlasSource
	assert(src != null, "source 0 must be a TileSetAtlasSource")

	var tiles := src.get_tiles()
	for atlas_coords in _EXPECTED_ATLAS:
		assert(atlas_coords in tiles, "atlas tile missing at %s" % str(atlas_coords))

	for i in _EXPECTED_ATLAS.size():
		var td := src.get_tile_data(_EXPECTED_ATLAS[i], 0)
		assert(td != null)
		assert(str(td.get_custom_data("tile_name")) == _EXPECTED_NAMES[i])

	# Pixel-art import: flags/filter=false in companion .import (Godot 4 has no Texture2D.flags).
	var tex := src.texture
	assert(tex != null)
	var import_path := String(tex.resource_path) + ".import"
	assert(FileAccess.file_exists(import_path), "missing import sidecar: %s" % import_path)
	var body := FileAccess.get_file_as_string(import_path)
	assert("flags/filter=false" in body, "texture import must disable filtering for LPC art")

	# Nearest filtering on this map so scaled tiles stay crisp regardless of project defaults.
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	assert(texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST)

	for i in _EXPECTED_ATLAS.size():
		set_cell(0, Vector2i(i, 0), 0, _EXPECTED_ATLAS[i])

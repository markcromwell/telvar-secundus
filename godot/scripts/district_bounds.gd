## Canonical Secundus overworld districts: 160×90 logical tiles (16×16 art at 2× scale).
## Spatial rules: Veneficturis north of Old City; Severen River is the southernmost band (y ≥ 80).
## Edit rects here — tile painting reads this data at runtime (see overworld_tile_populator.gd).
extends Object
class_name DistrictBounds

const MAP_SIZE := Vector2i(160, 90)

## Inclusive row indices (for documentation / external checks).
const VENEFICTURIS_ROW_MAX := 14
const OLD_CITY_ROW_MIN := 15
const OLD_CITY_ROW_MAX := 35
const SEVEREN_RIVER_ROW_MIN := 80

## Twelve districts: unique `id`, TileMap `layer` (theme layer), `source_id` (TileSet source),
## world `rect`, and default floor atlas coords. Walls use atlas (0, 1) on map perimeter only.
const DISTRICTS: Array[Dictionary] = [
	{
		"id": "veneficturis",
		"display_name": "Veneficturis",
		"layer": 1,
		"source_id": 1,
		"rect": Rect2i(0, 0, 160, 15),
		"floor_atlas": Vector2i(0, 0),
	},
	{
		"id": "old_city",
		"display_name": "Old City",
		"layer": 0,
		"source_id": 0,
		"rect": Rect2i(0, 15, 160, 21),
		"floor_atlas": Vector2i(0, 0),
	},
	{
		"id": "mercator_ward",
		"display_name": "Mercator Ward",
		"layer": 0,
		"source_id": 0,
		"rect": Rect2i(0, 36, 53, 15),
		"floor_atlas": Vector2i(1, 0),
	},
	{
		"id": "aspirant_commons",
		"display_name": "Aspirant Commons",
		"layer": 1,
		"source_id": 1,
		"rect": Rect2i(53, 36, 53, 15),
		"floor_atlas": Vector2i(0, 0),
	},
	{
		"id": "red_quarter",
		"display_name": "Red Quarter",
		"layer": 2,
		"source_id": 2,
		"rect": Rect2i(106, 36, 54, 15),
		"floor_atlas": Vector2i(0, 0),
	},
	{
		"id": "eastmarket",
		"display_name": "Eastmarket",
		"layer": 0,
		"source_id": 0,
		"rect": Rect2i(0, 51, 53, 15),
		"floor_atlas": Vector2i(2, 0),
	},
	{
		"id": "foundry_deep",
		"display_name": "Foundry Deep",
		"layer": 2,
		"source_id": 2,
		"rect": Rect2i(53, 51, 53, 15),
		"floor_atlas": Vector2i(1, 0),
	},
	{
		"id": "crystal_promenade",
		"display_name": "Crystal Promenade",
		"layer": 1,
		"source_id": 1,
		"rect": Rect2i(106, 51, 54, 15),
		"floor_atlas": Vector2i(1, 0),
	},
	{
		"id": "undercroft",
		"display_name": "Undercroft",
		"layer": 2,
		"source_id": 2,
		"rect": Rect2i(0, 66, 53, 14),
		"floor_atlas": Vector2i(2, 0),
	},
	{
		"id": "harborfront_north",
		"display_name": "Harborfront North",
		"layer": 3,
		"source_id": 3,
		"rect": Rect2i(53, 66, 53, 14),
		"floor_atlas": Vector2i(0, 0),
	},
	{
		"id": "severen_quays",
		"display_name": "Severen Quays",
		"layer": 3,
		"source_id": 3,
		"rect": Rect2i(106, 66, 54, 14),
		"floor_atlas": Vector2i(1, 0),
	},
	{
		"id": "severen_river",
		"display_name": "Severen River",
		"layer": 3,
		"source_id": 3,
		"rect": Rect2i(0, 80, 160, 10),
		"floor_atlas": Vector2i(2, 0),
	},
]

static func district_count() -> int:
	return DISTRICTS.size()


static func assert_partition_covers_map() -> void:
	## Dev-only sanity check; optional call from tests / debug.
	var covered: Dictionary = {}
	for d in DISTRICTS:
		var r: Rect2i = d["rect"]
		for y in range(r.position.y, r.end.y):
			for x in range(r.position.x, r.end.x):
				var k := Vector2i(x, y)
				assert(not covered.has(k), "Overlapping districts at %s" % k)
				covered[k] = true
	assert(covered.size() == MAP_SIZE.x * MAP_SIZE.y, "District rects must tile the full map")

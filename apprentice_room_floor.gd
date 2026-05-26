extends TileMapLayer
## Veneficturis apprentice room floor: exactly 8×6 tiles when populated.
## Fills from the LPC dark-stone atlas if the layer has no tiles yet (CI-friendly).
## NPC positions for this room are applied from Game Data Resources (phase 2688).

const ROOM_WIDTH_TILES := 8
const ROOM_HEIGHT_TILES := 6
const SOURCE_ID := 0
const ATLAS_COORDS := Vector2i(0, 0)
const GAME_DATA_PATH := "res://data/game_data_resources.json"
const LOCATION_ID := "veneficturis_apprentice_room"


func _ready() -> void:
	if tile_set == null:
		push_error("ApprenticeRoom/Floor: TileSet is not assigned")
		return
	var used := get_used_rect()
	if used.size.x <= 0 or used.size.y <= 0:
		for x in range(ROOM_WIDTH_TILES):
			for y in range(ROOM_HEIGHT_TILES):
				set_cell(Vector2i(x, y), SOURCE_ID, ATLAS_COORDS, 0)
	_apply_npc_spawns_from_game_data()


func _apply_npc_spawns_from_game_data() -> void:
	var f := FileAccess.open(GAME_DATA_PATH, FileAccess.READ)
	if f == null:
		push_warning("ApprenticeRoom/Floor: cannot open game data: %s" % GAME_DATA_PATH)
		return
	var parsed = JSON.parse_string(f.get_as_text())
	if typeof(parsed) != TYPE_DICTIONARY:
		push_warning("ApprenticeRoom/Floor: game data root must be an object")
		return
	var root: Dictionary = parsed
	var locs: Variant = root.get("locations", null)
	if typeof(locs) != TYPE_DICTIONARY:
		push_warning("ApprenticeRoom/Floor: game data missing 'locations'")
		return
	var loc: Variant = locs.get(LOCATION_ID, null)
	if typeof(loc) != TYPE_DICTIONARY:
		push_warning("ApprenticeRoom/Floor: game data missing location %s" % LOCATION_ID)
		return
	var loc_dict: Dictionary = loc
	var spawns: Variant = loc_dict.get("npc_spawns", null)
	if typeof(spawns) != TYPE_DICTIONARY:
		push_warning("ApprenticeRoom/Floor: location %s missing npc_spawns" % LOCATION_ID)
		return
	var parent := get_parent()
	if parent == null:
		return
	var half := Vector2(tile_set.tile_size) * 0.5
	for npc_key in spawns:
		var spawn: Variant = spawns[npc_key]
		if typeof(spawn) != TYPE_DICTIONARY:
			continue
		var tile_raw: Variant = spawn.get("tile", null)
		if typeof(tile_raw) != TYPE_ARRAY or tile_raw.size() < 2:
			continue
		var tx := int(tile_raw[0])
		var ty := int(tile_raw[1])
		if tx < 0 or ty < 0 or tx >= ROOM_WIDTH_TILES or ty >= ROOM_HEIGHT_TILES:
			push_warning("ApprenticeRoom/Floor: npc %s tile out of bounds" % npc_key)
			continue
		var npc_name := "Npc%s" % String(npc_key).capitalize()
		if not parent.has_node(StringName(npc_name)):
			push_warning("ApprenticeRoom/Floor: no scene child %s" % npc_name)
			continue
		var npc := parent.get_node(StringName(npc_name)) as Node2D
		if npc == null:
			continue
		var local_center := map_to_local(Vector2i(tx, ty)) + half
		npc.position = local_center

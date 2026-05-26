extends TileMapLayer
## Veneficturis apprentice room floor: exactly 8×6 tiles when populated.
## Fills from the LPC dark-stone atlas if the layer has no tiles yet (CI-friendly).

const ROOM_WIDTH_TILES := 8
const ROOM_HEIGHT_TILES := 6
const SOURCE_ID := 0
const ATLAS_COORDS := Vector2i(0, 0)


func _ready() -> void:
	if tile_set == null:
		push_error("ApprenticeRoom/Floor: TileSet is not assigned")
		return
	var used := get_used_rect()
	if used.size.x > 0 and used.size.y > 0:
		return
	for x in range(ROOM_WIDTH_TILES):
		for y in range(ROOM_HEIGHT_TILES):
			set_cell(Vector2i(x, y), SOURCE_ID, ATLAS_COORDS, 0)

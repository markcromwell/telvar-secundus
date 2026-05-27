extends Node2D

## Builds a 160×90 LPC terrain map at runtime for fast HTML5 first paint.
## Visible columns paint in _ready(); the rest stream in _process() with
## viewport-first scheduling. After the full map exists, tile writes should go
## through _occlusion_allows_cell() so dynamic updates stay view-bound.

const MAP_SIZE := Vector2i(160, 90)
const TILE_PX := 16
const SOURCE_ID := 0
const LAYER_FLOOR := 0
const LAYER_WALLS := 1

const ATLAS_FLOOR_A := Vector2i(0, 0)
const ATLAS_FLOOR_B := Vector2i(1, 0)
const ATLAS_FLOOR_C := Vector2i(2, 0)
const ATLAS_WALL := Vector2i(3, 0)

@onready var _tile_map: TileMap = $TileMap
@onready var _camera: Camera2D = $Camera2D

var _pending_columns: Array[int] = []
var _map_fully_initialized: bool = false


func _ready() -> void:
	_ensure_tilemap_layers()
	_center_camera_on_map()

	var vis := _viewport_world_rect().grow(float(TILE_PX * 2))
	for x in range(MAP_SIZE.x):
		if _column_intersects_world_rect(x, vis):
			_fill_column(x)
		else:
			_pending_columns.append(x)

	if not _pending_columns.is_empty():
		# Defer turning on _process so first-frame _ready work stays light (no huge idle queue).
		call_deferred("_start_column_stream")
	else:
		_map_fully_initialized = true


func _process(_delta: float) -> void:
	if _pending_columns.is_empty():
		_map_fully_initialized = true
		set_process(false)
		return

	var vis := _viewport_world_rect().grow(float(TILE_PX * 2))
	var picked_idx := -1
	for idx in range(_pending_columns.size()):
		var x: int = _pending_columns[idx]
		if _column_intersects_world_rect(x, vis):
			picked_idx = idx
			break

	if picked_idx >= 0:
		var col: int = _pending_columns[picked_idx]
		_pending_columns.remove_at(picked_idx)
		_fill_column(col)
	else:
		# Still outside the viewport footprint — keep streaming so the full map exists.
		var col2: int = _pending_columns.pop_front()
		_fill_column(col2)


func _start_column_stream() -> void:
	if not _pending_columns.is_empty():
		set_process(true)


func _ensure_tilemap_layers() -> void:
	if _tile_map.get_layers_count() < 2:
		_tile_map.add_layer(1)
	_tile_map.set_layer_name(LAYER_FLOOR, "floor")
	_tile_map.set_layer_name(LAYER_WALLS, "walls")


func _center_camera_on_map() -> void:
	var cx := float(MAP_SIZE.x * TILE_PX) * 0.5
	var cy := float(MAP_SIZE.y * TILE_PX) * 0.5
	_camera.position = Vector2(cx, cy)


func _viewport_world_rect() -> Rect2:
	var half := get_viewport().get_visible_rect().size / (2.0 * _camera.zoom)
	var center := _camera.get_screen_center_position()
	return Rect2(center - half, half * 2.0)


func _column_intersects_world_rect(col_x: int, r: Rect2) -> bool:
	var x0 := float(col_x * TILE_PX)
	var x1 := x0 + float(TILE_PX)
	return r.position.x < x1 and r.end.x > x0


func _cell_world_rect(tile: Vector2i) -> Rect2:
	var p := Vector2(tile) * float(TILE_PX)
	return Rect2(p, Vector2(float(TILE_PX), float(TILE_PX)))


func _occlusion_allows_cell(tile: Vector2i) -> bool:
	if not _map_fully_initialized:
		return true
	var r := _viewport_world_rect().grow(float(TILE_PX))
	return r.intersects(_cell_world_rect(tile))


func _fill_column(col_x: int) -> void:
	for y in range(MAP_SIZE.y):
		var coords := Vector2i(col_x, y)
		if not _occlusion_allows_cell(coords):
			continue
		var wall := _is_wall_tile(col_x, y)
		var floor_atlas := _floor_atlas_for(col_x, y)
		_tile_map.set_cell(LAYER_FLOOR, coords, SOURCE_ID, floor_atlas)
		if wall:
			_tile_map.set_cell(LAYER_WALLS, coords, SOURCE_ID, ATLAS_WALL)
		else:
			_tile_map.erase_cell(LAYER_WALLS, coords)


func _floor_atlas_for(col_x: int, row_y: int) -> Vector2i:
	var s := (col_x + row_y * 3) % 3
	match s:
		0:
			return ATLAS_FLOOR_A
		1:
			return ATLAS_FLOOR_B
		_:
			return ATLAS_FLOOR_C


func _is_wall_tile(col_x: int, row_y: int) -> bool:
	if col_x == 0 or row_y == 0:
		return true
	if col_x == MAP_SIZE.x - 1 or row_y == MAP_SIZE.y - 1:
		return true
	# Sparse interior blocks — keeps the interior traversable.
	if col_x % 11 == 5 and row_y % 9 == 4 and col_x > 3 and col_x < MAP_SIZE.x - 4:
		return true
	if col_x % 13 == 8 and row_y % 7 == 2 and row_y > 3 and row_y < MAP_SIZE.y - 4:
		return true
	return false

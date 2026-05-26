extends Node2D

@onready var tile_map = $TileMap

const LAYER_GROUND = 0
const LAYER_WALLS = 1

const TILE_SOURCE = 0

const ATLAS_GRASS = Vector2i(0, 0)
const ATLAS_COBBLESTONE = Vector2i(1, 0)
const ATLAS_DARK_STONE = Vector2i(2, 0)
const ATLAS_DIRT = Vector2i(3, 0)
const ATLAS_DOCK = Vector2i(4, 0)
const ATLAS_WATER = Vector2i(5, 0)
const ATLAS_CLIFF = Vector2i(6, 0)
const ATLAS_FLOOR = Vector2i(7, 0)

const ATLAS_WALLS = {
	"wall_brick": Vector2i(0, 1),
	"wall_stone": Vector2i(1, 1),
	"dark_stone": Vector2i(2, 1),
	"dock": Vector2i(3, 1),
	"stone_keep": Vector2i(4, 1)
}

func _ready():
	tile_map.set_layer_z_index(LAYER_WALLS, 1)
	place_terrain()
	place_buildings()
	place_special_zones()

func place_terrain():
	for x in range(160):
		for y in range(90):
			var atlas_coord = ATLAS_GRASS
			
			if (x >= 20 and x <= 45 and y >= 35 and y <= 55) or (x >= 70 and x <= 100 and y >= 20 and y <= 40):
				atlas_coord = ATLAS_COBBLESTONE
			elif (x >= 72 and x <= 92 and y >= 2 and y <= 18) or (x >= 15 and x <= 30 and y >= 45 and y <= 55):
				atlas_coord = ATLAS_DARK_STONE
			elif x >= 110 and x <= 130 and y >= 60 and y <= 80:
				atlas_coord = ATLAS_DIRT
			elif y >= 82 and y <= 89:
				atlas_coord = ATLAS_DOCK
				
			tile_map.set_cell(LAYER_GROUND, Vector2i(x, y), TILE_SOURCE, atlas_coord)

func place_buildings():
	var buildings = BuildingRegistry.get_buildings()
	for b in buildings:
		var tx = b["tile_x"]
		var ty = b["tile_y"]
		var tw = b["width"]
		var th = b["height"]
		var theme = b["tile_theme"]
		
		var wall_coord = ATLAS_WALLS.get(theme, ATLAS_WALLS["wall_brick"])
		
		for ix in range(tw):
			for iy in range(th):
				var is_perimeter = (ix == 0 or ix == tw - 1 or iy == 0 or iy == th - 1)
				if is_perimeter:
					tile_map.set_cell(LAYER_WALLS, Vector2i(tx + ix, ty + iy), TILE_SOURCE, wall_coord)
				else:
					tile_map.set_cell(LAYER_GROUND, Vector2i(tx + ix, ty + iy), TILE_SOURCE, ATLAS_FLOOR)

func place_special_zones():
	var v_x = 74
	var v_y = 6
	for offset_x in [0, 6, 12]:
		for ix in range(4):
			for iy in range(8):
				var is_perimeter = (ix == 0 or ix == 4 - 1 or iy == 0 or iy == 8 - 1)
				if is_perimeter:
					tile_map.set_cell(LAYER_WALLS, Vector2i(v_x + offset_x + ix, v_y + iy), TILE_SOURCE, ATLAS_WALLS["dark_stone"])
	
	for h_x in range(160):
		for h_y in range(85, 90):
			if h_y == 89:
				tile_map.set_cell(LAYER_GROUND, Vector2i(h_x, h_y), TILE_SOURCE, ATLAS_WATER)
			else:
				tile_map.set_cell(LAYER_GROUND, Vector2i(h_x, h_y), TILE_SOURCE, ATLAS_DOCK)
				
	for rh_x in range(55, 76):
		for rh_y in range(10, 23):
			var is_border = (rh_x == 55 or rh_x == 75 or rh_y == 10 or rh_y == 22)
			if is_border:
				tile_map.set_cell(LAYER_GROUND, Vector2i(rh_x, rh_y), TILE_SOURCE, ATLAS_CLIFF)
				
	var kk_x = 60
	var kk_y = 10
	for k_x in range(10):
		for k_y in range(12):
			tile_map.set_cell(LAYER_WALLS, Vector2i(kk_x + k_x, kk_y + k_y), TILE_SOURCE, ATLAS_WALLS["stone_keep"])

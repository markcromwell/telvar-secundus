## Pure-data registry of city building footprints (tile coords, 16x16 LPC grid).
## No rendering — consumers map tile_theme to wall/roof layers as needed.
class_name BuildingRegistry
extends RefCounted


static func get_buildings() -> Array:
	return [
		# --- Key landmarks (spec positions) ---
		{"label": "Orsson's Emporium", "tile_x": 30, "tile_y": 45, "width": 4, "height": 3, "tile_theme": "wall_brick"},
		{"label": "Paladin Temple", "tile_x": 80, "tile_y": 30, "width": 6, "height": 8, "tile_theme": "wall_stone"},
		{"label": "Cathedral of Aten", "tile_x": 90, "tile_y": 25, "width": 8, "height": 10, "tile_theme": "wall_stone"},
		{"label": "King's Keep", "tile_x": 60, "tile_y": 15, "width": 10, "height": 12, "tile_theme": "wall_stone"},
		{"label": "Veneficturis West Spire", "tile_x": 78, "tile_y": 6, "width": 3, "height": 14, "tile_theme": "dark_stone"},
		{"label": "Veneficturis Central Tower", "tile_x": 82, "tile_y": 6, "width": 4, "height": 15, "tile_theme": "dark_stone"},
		{"label": "Veneficturis East Spire", "tile_x": 87, "tile_y": 6, "width": 3, "height": 14, "tile_theme": "dark_stone"},
		{"label": "Rookery Tavern", "tile_x": 20, "tile_y": 50, "width": 4, "height": 4, "tile_theme": "wall_brick"},
		# --- Harbor (dock) ---
		{"label": "Harbor Customs House", "tile_x": 42, "tile_y": 62, "width": 6, "height": 4, "tile_theme": "dock"},
		{"label": "Harbor Longshoremen's Hall", "tile_x": 50, "tile_y": 62, "width": 5, "height": 5, "tile_theme": "dock"},
		{"label": "Harbor Ropewalk", "tile_x": 58, "tile_y": 64, "width": 8, "height": 3, "tile_theme": "dock"},
		{"label": "Harbor Pilot's Lodge", "tile_x": 68, "tile_y": 62, "width": 4, "height": 4, "tile_theme": "dock"},
		{"label": "Harbor Net Mender's Shed", "tile_x": 36, "tile_y": 66, "width": 4, "height": 3, "tile_theme": "dock"},
		# --- Reagent's Hill (elevated stone / keep silhouette cluster) ---
		{"label": "Reagent's Hill Gatehouse", "tile_x": 48, "tile_y": 8, "width": 5, "height": 4, "tile_theme": "stone_keep"},
		{"label": "Reagent's Hill Alchemist Barn", "tile_x": 44, "tile_y": 12, "width": 6, "height": 5, "tile_theme": "stone_keep"},
		{"label": "Reagent's Hill Signal Bastion", "tile_x": 52, "tile_y": 10, "width": 4, "height": 6, "tile_theme": "stone_keep"},
		{"label": "Reagent's Hill Storehouse", "tile_x": 40, "tile_y": 6, "width": 5, "height": 4, "tile_theme": "stone_keep"},
		# --- Merchant & craft quarters ---
		{"label": "Copper Lane Chandlery", "tile_x": 24, "tile_y": 44, "width": 4, "height": 3, "tile_theme": "wall_brick"},
		{"label": "Scale House Weighing Hall", "tile_x": 38, "tile_y": 42, "width": 5, "height": 4, "tile_theme": "wall_brick"},
		{"label": "Guild Row Tallow Works", "tile_x": 26, "tile_y": 40, "width": 5, "height": 3, "tile_theme": "wall_brick"},
		{"label": "East Bazaar Cloth Hall", "tile_x": 34, "tile_y": 38, "width": 6, "height": 4, "tile_theme": "wall_brick"},
		{"label": "Merchant Counting House", "tile_x": 22, "tile_y": 46, "width": 5, "height": 3, "tile_theme": "wall_brick"},
		# --- Old City ---
		{"label": "Old Cobbles Smithy", "tile_x": 14, "tile_y": 48, "width": 4, "height": 4, "tile_theme": "wall_stone"},
		{"label": "Burgher Tenement North", "tile_x": 10, "tile_y": 52, "width": 6, "height": 4, "tile_theme": "wall_stone"},
		{"label": "Burgher Tenement South", "tile_x": 10, "tile_y": 56, "width": 6, "height": 4, "tile_theme": "wall_stone"},
		{"label": "Old City Scrivener's Shop", "tile_x": 18, "tile_y": 54, "width": 4, "height": 3, "tile_theme": "wall_stone"},
		{"label": "Creakstairs Inn", "tile_x": 28, "tile_y": 52, "width": 5, "height": 4, "tile_theme": "wall_brick"},
		# --- Temple district surrounds ---
		{"label": "Acolyte Dormitory", "tile_x": 72, "tile_y": 28, "width": 5, "height": 5, "tile_theme": "wall_stone"},
		{"label": "Reliquary Workshop", "tile_x": 100, "tile_y": 24, "width": 5, "height": 4, "tile_theme": "wall_stone"},
		{"label": "Bellfounder's Yard", "tile_x": 78, "tile_y": 22, "width": 6, "height": 4, "tile_theme": "wall_stone"},
		{"label": "Sanctuary Guest Hall", "tile_x": 88, "tile_y": 36, "width": 6, "height": 5, "tile_theme": "wall_stone"},
		# --- Pallium civic ---
		{"label": "Pallium Archive Annex", "tile_x": 52, "tile_y": 18, "width": 5, "height": 4, "tile_theme": "wall_stone"},
		{"label": "Crown Solicitor's Office", "tile_x": 48, "tile_y": 22, "width": 5, "height": 4, "tile_theme": "wall_stone"},
		{"label": "Royal Guard Barracks", "tile_x": 74, "tile_y": 16, "width": 8, "height": 5, "tile_theme": "wall_stone"},
		{"label": "Herald's Colonnade", "tile_x": 58, "tile_y": 28, "width": 7, "height": 4, "tile_theme": "wall_stone"},
		# --- North wards & academy outskirts ---
		{"label": "North Watchtower", "tile_x": 70, "tile_y": 10, "width": 4, "height": 5, "tile_theme": "wall_stone"},
		{"label": "Apprentice Lodgings East", "tile_x": 94, "tile_y": 10, "width": 6, "height": 4, "tile_theme": "wall_brick"},
		{"label": "Apprentice Lodgings West", "tile_x": 70, "tile_y": 6, "width": 5, "height": 4, "tile_theme": "wall_brick"},
		{"label": "Astrolabe Court Greenhouse", "tile_x": 100, "tile_y": 8, "width": 5, "height": 5, "tile_theme": "wall_brick"},
		# --- Riverfront & mixed ---
		{"label": "Millrace Granary", "tile_x": 8, "tile_y": 36, "width": 7, "height": 5, "tile_theme": "wall_brick"},
		{"label": "Quayside Cooperage", "tile_x": 18, "tile_y": 60, "width": 5, "height": 4, "tile_theme": "wall_brick"},
		{"label": "River Gate Tollhouse", "tile_x": 6, "tile_y": 44, "width": 4, "height": 5, "tile_theme": "wall_stone"},
		{"label": "Lower Docks Fishmonger", "tile_x": 30, "tile_y": 62, "width": 5, "height": 3, "tile_theme": "dock"},
		{"label": "Canal Workshed", "tile_x": 12, "tile_y": 40, "width": 6, "height": 3, "tile_theme": "wall_stone"},
		{"label": "South Postern Guardroom", "tile_x": 90, "tile_y": 58, "width": 4, "height": 4, "tile_theme": "wall_stone"},
		{"label": "East Market Porters' Den", "tile_x": 100, "tile_y": 46, "width": 5, "height": 4, "tile_theme": "wall_brick"},
		{"label": "Lampwright's Shop", "tile_x": 40, "tile_y": 52, "width": 4, "height": 3, "tile_theme": "wall_brick"},
		{"label": "Physicker's Hall", "tile_x": 62, "tile_y": 40, "width": 6, "height": 5, "tile_theme": "wall_stone"},
		{"label": "Carters' Guild Hall", "tile_x": 72, "tile_y": 44, "width": 7, "height": 4, "tile_theme": "wall_brick"},
		{"label": "Silversmith Row", "tile_x": 46, "tile_y": 34, "width": 8, "height": 3, "tile_theme": "wall_brick"},
		{"label": "Weaver's Loft", "tile_x": 56, "tile_y": 36, "width": 5, "height": 4, "tile_theme": "wall_brick"},
		{"label": "Tannery Compound", "tile_x": 4, "tile_y": 52, "width": 5, "height": 6, "tile_theme": "wall_brick"},
		{"label": "Charcoal Yard Office", "tile_x": 2, "tile_y": 60, "width": 4, "height": 3, "tile_theme": "wall_stone"},
		{"label": "North Cobbler's", "tile_x": 104, "tile_y": 14, "width": 4, "height": 3, "tile_theme": "wall_brick"},
		{"label": "Stable Mews Central", "tile_x": 34, "tile_y": 30, "width": 6, "height": 4, "tile_theme": "wall_brick"},
	]

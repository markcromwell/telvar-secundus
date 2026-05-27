extends GdUnitTestSuite


func test_building_count_at_least_40() -> void:
	var buildings: Array = BuildingRegistry.get_buildings()
	assert_that(buildings.size()).is_greater_equal(40)


func test_key_landmarks_present() -> void:
	var buildings: Array = BuildingRegistry.get_buildings()
	var labels: Dictionary = {}
	for b in buildings:
		labels[str(b.get("label", ""))] = true
	assert_that(labels.has("Orsson's Emporium")).is_true()
	assert_that(labels.has("Paladin Temple")).is_true()
	assert_that(labels.has("Cathedral of Aten")).is_true()
	assert_that(labels.has("King's Keep")).is_true()
	var ven_ok := false
	for label in labels:
		if str(label).contains("Veneficturis"):
			ven_ok = true
			break
	assert_bool(ven_ok).is_true()


func test_harbor_uses_dock_tiles() -> void:
	var buildings: Array = BuildingRegistry.get_buildings()
	var dock_ok := false
	for b in buildings:
		if str(b.get("tile_theme", "")) == "dock":
			dock_ok = true
			break
	assert_bool(dock_ok).is_true()


func test_veneficturis_uses_dark_stone() -> void:
	var buildings: Array = BuildingRegistry.get_buildings()
	var ok := false
	for b in buildings:
		if str(b.get("tile_theme", "")) == "dark_stone" and str(b.get("label", "")).contains("Veneficturis"):
			ok = true
			break
	assert_bool(ok).is_true()

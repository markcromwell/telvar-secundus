extends GdUnitTestSuite
## GdUnit4 coverage for [member SaveManager] JSON metadata and restore (phase 2725).


const FIXTURE_PATH := "res://fixtures/save_valid_v1.json"

const _PlayerWorld := preload("res://scripts/player_world.gd")
const _SaveTestInventory := preload("res://tests/gdunit/save_test_inventory.gd")
const _SaveTestQuestState := preload("res://tests/gdunit/save_test_quest_state.gd")
const _SaveTestFlags := preload("res://tests/gdunit/save_test_flags.gd")


func before_test() -> void:
	_cleanup_slots()
	SaveManager._pending_restore = {}
	for c in get_children():
		remove_child(c)
		c.free()


func after_test() -> void:
	_cleanup_slots()
	SaveManager._pending_restore = {}
	for c in get_children():
		remove_child(c)
		c.free()


func _cleanup_slots() -> void:
	for i in range(SaveManager.SLOT_COUNT):
		var rel := SaveManager.get_slot_path(i)
		if not FileAccess.file_exists(rel):
			continue
		var abs_path := ProjectSettings.globalize_path(rel)
		@warning_ignore("return_value_discarded")
		DirAccess.remove_absolute(abs_path)


func _fixture_dict() -> Dictionary:
	var text := FileAccess.get_file_as_string(FIXTURE_PATH)
	assert_str(text).is_not_empty()
	var parsed: Variant = JSON.parse_string(text)
	assert_bool(parsed is Dictionary).is_true()
	return parsed


func _write_slot_document(slot_index: int, data: Dictionary) -> void:
	var path := SaveManager.get_slot_path(slot_index)
	var f := FileAccess.open(path, FileAccess.WRITE)
	assert_object(f).is_not_null()
	f.store_string(JSON.stringify(data, "\t"))
	f.close()


func _write_raw_slot(slot_index: int, content: String) -> void:
	var path := SaveManager.get_slot_path(slot_index)
	var f := FileAccess.open(path, FileAccess.WRITE)
	assert_object(f).is_not_null()
	f.store_string(content)
	f.close()


func test_read_slot_metadata_parses_timestamp_act_quest() -> void:
	var data := _fixture_dict()
	var err := SaveManager.write_save_dict(0, data)
	assert_int(err).is_equal(OK)
	var meta := SaveManager.read_slot_metadata(0)
	assert_bool(bool(meta["empty"])).is_false()
	assert_int(int(meta["timestamp_unix"])).is_equal(1714147200)
	assert_int(int(meta["act_number"])).is_equal(2)
	assert_str(str(meta["current_quest_name"])).is_equal("Veneficturis Orientation")
	assert_str(str(meta.get("error", ""))).is_empty()


func test_read_slot_metadata_empty_missing_file() -> void:
	var meta := SaveManager.read_slot_metadata(1)
	assert_bool(bool(meta["empty"])).is_true()
	assert_int(int(meta["timestamp_unix"])).is_equal(0)
	assert_int(int(meta["act_number"])).is_equal(0)
	assert_str(str(meta["current_quest_name"])).is_empty()
	assert_str(str(meta.get("error", ""))).is_empty()


func test_read_slot_metadata_corrupted_json_sets_error() -> void:
	_write_raw_slot(2, "{ not valid json")
	var meta := SaveManager.read_slot_metadata(2)
	assert_bool(bool(meta["empty"])).is_true()
	assert_str(str(meta["error"])).is_equal("invalid_json")


func test_read_save_dict_corrupted_returns_empty_without_crash() -> void:
	_write_raw_slot(3, "null")
	var data := SaveManager.read_save_dict(3)
	assert_dict(data).is_empty()


func test_restore_from_slot_invalid_player_shape_returns_error() -> void:
	var bad := {
		"format_version": 1,
		"scene_path": "",
		"player": [],
	}
	_write_slot_document(0, bad)
	var err := SaveManager.restore_from_slot(0)
	assert_int(err).is_equal(ERR_INVALID_DATA)


func test_restore_applies_player_inventory_quest_flags() -> void:
	var player := _PlayerWorld.new()
	var inv: Node = _SaveTestInventory.new()
	var qs: Node = _SaveTestQuestState.new()
	var fg: Node = _SaveTestFlags.new()
	add_child(player)
	add_child(inv)
	add_child(qs)
	add_child(fg)

	var data := _fixture_dict()
	data["scene_path"] = ""
	var werr := SaveManager.write_save_dict(0, data)
	assert_int(werr).is_equal(OK)

	var rerr := SaveManager.restore_from_slot(0)
	assert_int(rerr).is_equal(OK)
	await await_idle_frame()

	assert_vector(player.global_position).is_equal(Vector2(128.5, 256.0))
	assert_int(player.hp).is_equal(18)
	assert_int(player.max_hp).is_equal(24)

	assert_array(inv.last_items).has_size(1)
	assert_dict(inv.last_items[0] as Dictionary).contains_keys("id", "qty")

	assert_dict(qs.last_state).contains_keys("main")
	assert_str(str(qs.last_state.get("main", ""))).is_equal("orientation_started")

	assert_dict(fg.last_flags).contains_keys("met_myramar")
	assert_bool(bool(fg.last_flags.get("met_myramar", false))).is_true()

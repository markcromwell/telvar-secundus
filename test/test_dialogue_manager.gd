extends GdUnitTestSuite
## GdUnit4: DialogueManager flags, JSON load into _dialogues, and bracket flag parsing.

const _DM_SCRIPT := preload("res://scripts/DialogueManager.gd")


func _spawn_manager() -> Node:
	var dm: Node = _DM_SCRIPT.new()
	add_child(auto_free(dm))
	await get_tree().process_frame
	return dm


func test_flag_roundtrip_set_then_get_returns_same_value() -> void:
	var dm := await _spawn_manager()
	dm.set_flag("round_trip_key", 42)
	assert_int(dm.get_flag("round_trip_key")).is_equal(42)


func test_get_flag_missing_key_returns_default() -> void:
	var dm := await _spawn_manager()
	assert_that(dm.get_flag("nonexistent_key_for_default_test", "fallback")).is_equal("fallback")


func test_dialogues_contains_myramar_after_load() -> void:
	var dm := await _spawn_manager()
	assert_bool(dm._dialogues.has("myramar")).is_true()


func test_myramar_graph_is_dictionary_with_start_node() -> void:
	var dm := await _spawn_manager()
	var myramar: Variant = dm._dialogues.get("myramar")
	assert_bool(myramar is Dictionary).is_true()
	var graph := myramar as Dictionary
	assert_bool(graph.has("start")).is_true()


func test_quest_give_flag_present_in_parsed_flags_array() -> void:
	var dm := await _spawn_manager()
	var graph: Dictionary = dm._dialogues["myramar"] as Dictionary
	var node_2: Dictionary = graph["node_2"] as Dictionary
	var flags: Array = node_2.get("flags", []) as Array
	assert_bool("quest_give" in flags).is_true()

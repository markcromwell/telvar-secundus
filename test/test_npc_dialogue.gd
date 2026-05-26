extends GdUnitTestSuite

## DialogueManager autoload + assets/dialogue/myramar.json (GdUnit4).


func before_test() -> void:
	DialogueManager.hide_dialogue()


func after_test() -> void:
	DialogueManager.hide_dialogue()


func test_flag_round_trip() -> void:
	var key := "phase2518_flag_round_trip"
	var value := {"answer": 42}
	DialogueManager.set_flag(key, value)
	assert_that(DialogueManager.get_flag(key)).is_equal(value)


func test_is_dialogue_active_starts_false_when_idle() -> void:
	assert_bool(DialogueManager.is_dialogue_active).is_false()


func test_myramar_json_start_node_has_speaker_key() -> void:
	var path := "res://assets/dialogue/myramar.json"
	assert_that(FileAccess.file_exists(path)).is_true()
	var raw := FileAccess.get_file_as_string(path)
	var parsed = JSON.parse_string(raw)
	assert_that(parsed is Array).is_true()
	var found := false
	for item: Variant in parsed as Array:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var row: Dictionary = item
		if str(row.get("id", "")) != "start":
			continue
		assert_that(row.has("speaker")).is_true()
		found = true
	assert_that(found).is_true()


func test_second_show_dialogue_while_active_does_not_double_open() -> void:
	var sample: Array = [
		{"id": "start", "text": "Hello.", "speaker": "NPC", "next": ""},
	]
	DialogueManager.show_dialogue("npc_a", sample)
	assert_bool(DialogueManager.is_dialogue_active).is_true()
	DialogueManager.show_dialogue("npc_b", sample)
	assert_bool(DialogueManager.is_dialogue_active).is_true()

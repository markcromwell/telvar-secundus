## Unit tests for DialogueManager flags and DialogueBox speaker binding (GdUnit4).
extends GdUnitTestSuite

const MINIMAL_DIALOGUE: Array = [
	{
		"id": "start",
		"text": "Hello.",
		"speaker": "Test Speaker",
		"next": "",
	},
]


func test_set_flag_get_flag_round_trip_returns_stored_value() -> void:
	var dm: Node = _spawn_dialogue_manager()
	dm.set_flag("k_dialogue_roundtrip", 42)
	assert_int(dm.get_flag("k_dialogue_roundtrip")).is_equal(42)
	dm.queue_free()


func test_get_flag_returns_null_default_for_unset_key() -> void:
	var dm: Node = _spawn_dialogue_manager()
	assert_bool(dm.get_flag("no_such_flag_key_dialogue_test") == null).is_true()
	dm.queue_free()


func test_show_dialogue_does_not_crash_with_minimal_single_entry_json() -> void:
	var dm: Node = _spawn_dialogue_manager()
	dm.show_dialogue("npc_test", MINIMAL_DIALOGUE)
	var ui_layer: CanvasLayer = dm.get_child(0) as CanvasLayer
	var box: Control = ui_layer.get_child(0) as Control
	assert_bool(box.visible).is_true()
	dm.queue_free()


func test_dialogue_box_show_dialogue_sets_name_label_text_to_entry_speaker() -> void:
	var box: Control = load("res://scenes/DialogueBox.tscn").instantiate() as Control
	add_child(box)
	var name_label: Label = box.get_node("PanelContainer/VBoxContainer/HBoxContainer/NameLabel") as Label
	box.show_dialogue(
		{
			"text": "Line",
			"speaker": "Drill Sergeant",
			"choices": [],
		}
	)
	assert_str(name_label.text).is_equal("Drill Sergeant")
	box.queue_free()


func _spawn_dialogue_manager() -> Node:
	var script: GDScript = load("res://scripts/DialogueManager.gd") as GDScript
	var dm: Node = script.new() as Node
	add_child(dm)
	return dm

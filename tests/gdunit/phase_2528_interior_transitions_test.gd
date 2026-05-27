extends GdUnitTestSuite

## Phase 2528 — interior wiring, fade timing, spawn markers, footstep streams (GDUnit4).

const MAIN_SCENE := "res://scenes/MainScene.tscn"
const ENTRANCE_NAMES := [
	"EntranceOrssonEmporium",
	"EntrancePaladinTemple",
	"EntranceCathedralOfAten",
	"EntranceRookeryTavern",
]

const INTERIOR_SCENES := [
	"res://scenes/interiors/interior_emporium.tscn",
	"res://scenes/interiors/interior_paladin_temple.tscn",
	"res://scenes/interiors/interior_cathedral_aten.tscn",
	"res://scenes/interiors/interior_rookery_tavern.tscn",
]

const WOOD_STREAM := preload("res://assets/audio/sfx/footstep_wood.ogg")
const STONE_STREAM := preload("res://assets/audio/sfx/footstep_stone.ogg")


func test_main_scene_has_four_entrances_with_target_and_spawn_id() -> void:
	var main: Node = load(MAIN_SCENE).instantiate()
	auto_free(main)
	for node_name in ENTRANCE_NAMES:
		var gate := main.get_node(node_name) as EntranceTrigger
		assert_that(gate).is_not_null()
		assert_that(gate.target_scene).is_not_empty()
		assert_that(gate.spawn_point_id).is_not_empty()
		assert_that(ResourceLoader.exists(gate.target_scene)).is_true()


func test_each_interior_player_aligns_spawn_marker_within_one_pixel() -> void:
	for path in INTERIOR_SCENES:
		var runner := scene_runner(path)
		await await_idle_frame()
		await await_idle_frame()
		var root := runner.scene() as Node2D
		var spawn := root.get_node("SpawnPoint") as Marker2D
		var player := root.get_node("Player") as Node2D
		assert_that(spawn.global_position.distance_to(player.global_position)).is_less_equal(1.0)


func test_interior_scene_resource_loads_under_one_second_wall_time() -> void:
	for path in INTERIOR_SCENES:
		var t0 := Time.get_ticks_usec()
		var packed := load(path)
		var seconds := float(Time.get_ticks_usec() - t0) / 1_000_000.0
		assert_that(seconds).is_less(1.0)
		assert_that(packed).is_not_null()


func test_fade_tween_duration_is_three_hundred_ms() -> void:
	var src := FileAccess.get_file_as_string("res://autoloads/TransitionManager.gd")
	var hits := 0
	for line in src.split("\n"):
		var s := line.strip_edges()
		if s.begins_with("#"):
			continue
		if s.contains("tween_property(color_rect") and s.contains("0.3)"):
			hits += 1
	assert_that(hits).is_greater_equal(2)


func test_return_to_overworld_assigns_stored_position_to_player() -> void:
	var src := FileAccess.get_file_as_string("res://autoloads/TransitionManager.gd")
	assert_that(src).contains("player.global_position = return_position")


func test_emporium_footstep_resolves_to_wood_stream() -> void:
	await _assert_footstep_stream_for(
		"res://scenes/interiors/interior_emporium.tscn", WOOD_STREAM)


func test_paladin_temple_footstep_resolves_to_stone_stream() -> void:
	await _assert_footstep_stream_for(
		"res://scenes/interiors/interior_paladin_temple.tscn", STONE_STREAM)


func _assert_footstep_stream_for(interior_path: String, want: Resource) -> void:
	var runner := scene_runner(interior_path)
	await await_idle_frame()
	await await_idle_frame()
	var root := runner.scene() as Node2D
	var player := root.get_node("Player") as CharacterBody2D
	player.velocity = Vector2(120.0, 0.0)
	var audio: AudioStreamPlayer = root.get_node("Player/FootstepComponent/AudioStreamPlayer")
	for _i in 24:
		await get_tree().physics_frame
	var stream: Resource = audio.stream
	assert_that(stream).is_equal(want)

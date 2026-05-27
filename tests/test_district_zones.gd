# GdUnit4 — district triggers, HUD timing, district metadata, Merchant↔Temple path.
extends GdUnitTestSuite

const OVERWORLD := "res://scenes/overworld/Overworld.tscn"
const HUD_SCENE := "res://HUD.tscn"


func _make_probe_body() -> CharacterBody2D:
	var body := CharacterBody2D.new()
	body.collision_layer = 1
	body.collision_mask = 0
	var cs := CollisionShape2D.new()
	var circ := CircleShape2D.new()
	circ.radius = 12.0
	cs.shape = circ
	body.add_child(cs)
	return body


func _await_physics_frames(count: int) -> void:
	for _i in count:
		await get_tree().physics_frame


func _assert_zone_signal_on_enter(
	_runner: GdUnitSceneRunner,
	zone: DistrictZone,
	probe: CharacterBody2D,
	outside: Vector2,
	inside: Vector2,
	expected_name: String
) -> void:
	var received: Array[String] = []
	zone.district_entered.connect(func(n: String) -> void: received.append(n))
	probe.global_position = outside
	await _await_physics_frames(3)
	probe.global_position = inside
	await _await_physics_frames(20)
	assert_int(received.size()).is_greater(0)
	assert_str(received.back()).is_equal(expected_name)


func test_district_zone_emits_district_entered_golden_bell_merchant_temple() -> void:
	var runner: GdUnitSceneRunner = scene_runner(OVERWORLD)
	var ow: Node = runner.scene()
	var probe: CharacterBody2D = auto_free(_make_probe_body()) as CharacterBody2D
	ow.add_child(probe)

	var golden: DistrictZone = ow.get_node("GoldenBell") as DistrictZone
	var merchant: DistrictZone = ow.get_node("MerchantDistrict") as DistrictZone
	var temple: DistrictZone = ow.get_node("TempleDistrict") as DistrictZone

	await _assert_zone_signal_on_enter(runner, golden, probe, Vector2(2600, 480), Vector2(800, 480), "Golden Bell")
	await _assert_zone_signal_on_enter(runner, merchant, probe, Vector2(5300, 480), Vector2(4000, 480), "Merchant District")
	await _assert_zone_signal_on_enter(runner, temple, probe, Vector2(600, 480), Vector2(1400, 480), "Temple District")


func test_hud_show_district_name_hides_after_simulated_time() -> void:
	var runner: GdUnitSceneRunner = scene_runner(HUD_SCENE)
	var hud: Node = runner.scene()
	var label: Label = hud.get_node("DistrictLabel") as Label

	hud.show_district_name("Temple District")
	assert_bool(label.visible).is_true()
	assert_str(label.text).is_equal("Temple District")

	var hold_timer: Timer = hud.get_node("DistrictHoldTimer") as Timer
	await runner.simulate_until_object_signal(hold_timer, "timeout")
	# Tween fade-out (0.5s) + callback — advance with scene_runner until hidden (bounded).
	var steps := 0
	while label.visible and steps < 600:
		await runner.simulate_frames(2)
		steps += 1

	assert_bool(label.visible).is_false()


func test_all_overworld_district_names_nonempty_and_unique() -> void:
	var runner: GdUnitSceneRunner = scene_runner(OVERWORLD)
	var ow: Node = runner.scene()
	var names: PackedStringArray = PackedStringArray()
	for child in ow.get_children():
		if child is DistrictZone:
			var dz: DistrictZone = child as DistrictZone
			assert_str(dz.district_name).is_not_empty()
			names.append(dz.district_name)
	assert_int(names.size()).is_equal(12)
	var seen: Dictionary = {}
	for n: String in names:
		assert_bool(seen.has(n)).is_false()
		seen[n] = true


func _is_allowed_building_collider(collider: Object) -> bool:
	return collider != null and collider.is_in_group("building_footprint_collision")


func test_merchant_to_temple_walk_timing_and_no_phantom_collisions() -> void:
	var runner: GdUnitSceneRunner = scene_runner(OVERWORLD)
	var ow: Node = runner.scene()
	var player: CharacterBody2D = ow.get_node("Player") as CharacterBody2D
	var merchant: Node2D = ow.get_node("MerchantDistrict") as Node2D
	var temple: Node2D = ow.get_node("TempleDistrict") as Node2D

	var start: Vector2 = merchant.global_position
	var goal_x: float = temple.global_position.x
	player.global_position = start
	player.velocity = Vector2.ZERO
	# TileMap / static gameplay bodies are expected on layer 1 (district Area2Ds use layer 8 and are not solid to CharacterBody2D).
	player.collision_mask = 1

	runner.simulate_action_press("ui_left")
	await runner.await_input_processed()

	var elapsed := 0.0
	var max_steps := 7200
	for _i in max_steps:
		await get_tree().physics_frame
		elapsed += get_physics_process_delta_time()

		for si in player.get_slide_collision_count():
			var col := player.get_slide_collision(si)
			var hit := col.get_collider()
			if not _is_allowed_building_collider(hit):
				fail("Phantom / non-building collider on Merchant→Temple path: %s" % hit)

		if player.global_position.x <= goal_x + 2.0:
			break

	runner.simulate_action_release("ui_left")
	assert_float(player.global_position.x).is_less_equal(goal_x + 8.0)

	assert_float(elapsed).is_between(19.0, 21.0)

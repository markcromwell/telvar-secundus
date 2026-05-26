extends Node

## Bridges main-scene UI (owned by other phases) to combat state: wires Attack and
## applies 2–6 physical damage at range 1 with floating damage text.

const MELEE_RANGE_TILES: int = 1


func _ready() -> void:
	# Autoload runs before the main scene is current_scene; wait one frame to wire UI.
	await get_tree().process_frame
	_try_wire_attack_button()


func _try_wire_attack_button() -> void:
	var scene_root: Node = get_tree().current_scene
	if scene_root == null:
		return
	var attack_btn: Node = scene_root.find_child("Attack", true, false)
	if attack_btn is Button:
		var b: Button = attack_btn as Button
		if not b.pressed.is_connected(_on_attack_pressed):
			b.pressed.connect(_on_attack_pressed)


func _on_attack_pressed() -> void:
	if not CombatManager.is_player_turn():
		return
	if CombatManager.enemy_hp <= 0:
		return
	if not _is_target_in_melee_range():
		return

	var damage: int = randi_range(2, 6)
	CombatManager.enemy_hp = maxi(0, CombatManager.enemy_hp - damage)
	_refresh_enemy_hp_bar()
	_spawn_damage_float(damage)
	CombatManager.begin_enemy_turn()


func _is_target_in_melee_range() -> bool:
	# No tactical grid in this bootstrap scene; treat combat as adjacent (range 1).
	return MELEE_RANGE_TILES >= 1


func _refresh_enemy_hp_bar() -> void:
	var scene_root: Node = get_tree().current_scene
	if scene_root == null:
		return
	var bar: Node = scene_root.find_child("EnemyHPBar", true, false)
	if bar is ProgressBar:
		var pb: ProgressBar = bar as ProgressBar
		pb.max_value = float(CombatManager.enemy_max_hp)
		pb.value = float(CombatManager.enemy_hp)


func _spawn_damage_float(amount: int) -> void:
	var scene_root: Node = get_tree().current_scene
	if scene_root == null:
		return
	var host: Control = scene_root.get_node_or_null("Root") as Control
	if host == null:
		host = scene_root as Control

	var label := Label.new()
	label.text = "-%d" % amount
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_color_override("font_color", Color(1.0, 0.35, 0.12))
	label.add_theme_color_override("font_outline_color", Color(0, 0, 0))
	label.add_theme_constant_override("outline_size", 5)

	host.add_child(label)

	var enemy_bar: Node = scene_root.find_child("EnemyHPBar", true, false)
	if enemy_bar is Control:
		var c: Control = enemy_bar as Control
		label.global_position = c.global_position + Vector2(-8.0, -36.0)
	else:
		label.global_position = Vector2(180.0, 56.0)

	var tw := create_tween()
	var end_pos: Vector2 = label.global_position + Vector2(0.0, -44.0)
	tw.set_parallel(true)
	tw.tween_property(label, "global_position", end_pos, 0.65).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw.tween_property(
		label,
		"modulate",
		Color(label.modulate.r, label.modulate.g, label.modulate.b, 0.0),
		0.65,
	)
	tw.chain()
	tw.tween_callback(label.queue_free)

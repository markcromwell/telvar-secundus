class_name BanishmentSpell
extends RefCounted

## Red-rank Banishment: 20 MP. Short arc in front of the caster hits `enemies`:
## knockback + stun (`apply_stun`). Bodies in group `shades` also take 15 bonus damage (`take_damage`).

const SPELL_ID := "banishment"
const MANA_COST := 20
const SHADE_BONUS_DAMAGE := 15
const STUN_SEC := 2.0
const REACH_TILES := 5
const SWATH_TILES := 2
const TILE_WORLD_PX := 16
const KNOCKBACK_SPEED := 280.0


static func cast_wave(world_parent: Node2D, caster: Node2D, aim_direction: Vector2, mana: ManaComponent) -> bool:
	if world_parent == null or caster == null or mana == null:
		return false

	var space := world_parent.get_world_2d().direct_space_state
	if space == null:
		return false

	if not mana.use_mana(MANA_COST):
		return false

	var dir := aim_direction
	if dir.length_squared() < 0.0001:
		dir = Vector2.RIGHT
	dir = dir.normalized()

	var reach := float(REACH_TILES * TILE_WORLD_PX)
	var width := float(SWATH_TILES * TILE_WORLD_PX)
	var rect := RectangleShape2D.new()
	rect.size = Vector2(reach, width)

	var center := caster.global_position + dir * (reach * 0.5)
	var xf := Transform2D(dir.angle(), center)

	var params := PhysicsShapeQueryParameters2D.new()
	params.shape = rect
	params.transform = xf
	params.collide_with_areas = true
	params.collide_with_bodies = true
	params.collision_mask = 0xFFFFFFFF
	if caster is CollisionObject2D:
		params.exclude = [(caster as CollisionObject2D).get_rid()]

	var hits: Array = space.intersect_shape(params, 32)
	var seen: Dictionary = {}
	for item in hits:
		var col = item.get("collider")
		if col == null or not (col is Node2D):
			continue
		var body := col as Node2D
		if not body.is_in_group("enemies"):
			continue
		var iid := body.get_instance_id()
		if seen.has(iid):
			continue
		seen[iid] = true

		var knock := dir * KNOCKBACK_SPEED
		_apply_knockback(body, knock)
		if body.has_method("apply_stun"):
			body.call("apply_stun", STUN_SEC)
		if body.is_in_group("shades") and body.has_method("take_damage"):
			body.call("take_damage", SHADE_BONUS_DAMAGE)

	return true


static func _apply_knockback(body: Node2D, impulse: Vector2) -> void:
	if body is CharacterBody2D:
		(body as CharacterBody2D).velocity += impulse
	elif body is RigidBody2D:
		(body as RigidBody2D).apply_central_impulse(impulse)

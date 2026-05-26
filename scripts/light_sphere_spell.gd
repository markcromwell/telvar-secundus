class_name LightSphereSpell
extends RefCounted

## Red-rank Light Sphere: 5 MP, 5-tile radius (16px/tile world units), 30s duration.

const SPELL_ID := "light_sphere"
const MANA_COST := 5
const DURATION_SEC := 30.0
const RADIUS_TILES := 5
const TILE_WORLD_PX := 16

const _EFFECT_SCENE := preload("res://scenes/effects/light_sphere.tscn")


static func cast_at(world_parent: Node, global_position: Vector2, mana: ManaComponent) -> bool:
	if world_parent == null or mana == null:
		return false
	if not mana.use_mana(MANA_COST):
		return false
	var inst: Node2D = _EFFECT_SCENE.instantiate() as Node2D
	world_parent.add_child(inst)
	inst.global_position = global_position
	return true

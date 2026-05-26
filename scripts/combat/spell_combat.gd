class_name SpellCombat
extends RefCounted
## Combat resolution for spells (phase 2680: Banishment).

const BANISHMENT_SPELL_ID := "banishment"
const BANISHMENT_PUSH_TILES := 3
const BANISHMENT_STUN_TURNS := 1
const BANISHMENT_SHADE_DAMAGE := 15

## Loot rolled when a Thug is defeated (combat victory).
const THUG_VICTORY_COPPER_MIN := 1
const THUG_VICTORY_COPPER_MAX := 3


static func roll_thug_victory_copper() -> int:
	return randi_range(THUG_VICTORY_COPPER_MIN, THUG_VICTORY_COPPER_MAX)


static func resolve_banishment(target_kind: String) -> Dictionary:
	"""Return structured combat outcome for Banishment.

	``target_kind`` is a loose id such as ``"thug"`` or ``"shade"`` (case-insensitive).
	"""
	var kind := target_kind.strip_edges().to_lower()
	var out := {
		"pushed_tiles": 0,
		"stun_turns": 0,
		"damage": 0,
	}
	if kind == "thug":
		out.pushed_tiles = BANISHMENT_PUSH_TILES
		out.stun_turns = BANISHMENT_STUN_TURNS
	elif kind == "shade":
		out.damage = BANISHMENT_SHADE_DAMAGE
	return out


static func apply_spell(spell: Spell, target_kind: String) -> Dictionary:
	if spell == null:
		return {}
	if spell.spell_id == BANISHMENT_SPELL_ID or spell.effect == BANISHMENT_SPELL_ID:
		return resolve_banishment(target_kind)
	return {}

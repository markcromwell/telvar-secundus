## Data-driven enemy templates and spell metadata for Telvar Secundus combat.
## Used by [Enemy] to initialize stats and by [EnemyAI] to validate casts.
class_name EnemyDefinitions
extends RefCounted

const ENEMY_ROOKERY_THUG := "rookery_thug"
const ENEMY_CORRUPTED_APPRENTICE := "corrupted_apprentice"
const ENEMY_SHADE := "shade"

const SPELL_FIRE_DART := "fire_dart"

## Red-rank style fire dart used by the Corrupted Apprentice.
static var _spells: Dictionary = {
	SPELL_FIRE_DART: {
		"name": "Fire Dart",
		"mana_cost": 3,
		"damage_min": 4,
		"damage_max": 9,
	},
}

static func all_enemy_ids() -> PackedStringArray:
	return PackedStringArray([
		ENEMY_ROOKERY_THUG,
		ENEMY_CORRUPTED_APPRENTICE,
		ENEMY_SHADE,
	])


static func get_enemy_definition(enemy_id: String) -> Dictionary:
	match enemy_id:
		ENEMY_ROOKERY_THUG:
			return {
				"id": ENEMY_ROOKERY_THUG,
				"display_name": "Rookery Thug",
				"max_hp": 28,
				"atk": 6,
				"physical_immune": false,
				"max_mana": 0,
				"spells": [],
			}
		ENEMY_CORRUPTED_APPRENTICE:
			return {
				"id": ENEMY_CORRUPTED_APPRENTICE,
				"display_name": "Corrupted Apprentice",
				"max_hp": 16,
				"atk": 3,
				"physical_immune": false,
				"max_mana": 12,
				"spells": [SPELL_FIRE_DART],
			}
		ENEMY_SHADE:
			return {
				"id": ENEMY_SHADE,
				"display_name": "Shade",
				"max_hp": 20,
				"atk": 5,
				"physical_immune": true,
				"max_mana": 0,
				"spells": [],
			}
		_:
			return {}


static func get_spell_definition(spell_id: String) -> Dictionary:
	if _spells.has(spell_id):
		return _spells[spell_id]
	return {}


static func get_spell_mana_cost(spell_id: String) -> int:
	var spell := get_spell_definition(spell_id)
	return int(spell.get("mana_cost", 999))


static func roll_spell_damage(spell_id: String, rng: RandomNumberGenerator) -> int:
	var spell := get_spell_definition(spell_id)
	var lo := int(spell.get("damage_min", 0))
	var hi := int(spell.get("damage_max", lo))
	if hi < lo:
		return lo
	return rng.randi_range(lo, hi)

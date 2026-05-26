extends Node
## Tracks known spells and mana (combat regen hooks can call regen_mana).

const BANISHMENT_PATH := "res://resources/spells/banishment.tres"

## Lore catalog for the spell panel (not learned until added to known_spells elsewhere).
const LEARNABLE_CATALOG: Array[Dictionary] = [
	{"spell_id": "ember", "spell_name": "Ember", "mana_cost": 5},
	{"spell_id": "shield_light", "spell_name": "Shield Light", "mana_cost": 3},
	{"spell_id": "reveal", "spell_name": "Reveal", "mana_cost": 2},
]

var known_spells: Dictionary = {}  # spell_id -> Spell
var mana_current: int = 10
var mana_max: int = 10


func _ready() -> void:
	_register_builtin_spells()


func _register_builtin_spells() -> void:
	if ResourceLoader.exists(BANISHMENT_PATH):
		var loaded := load(BANISHMENT_PATH)
		if loaded is Spell:
			var s: Spell = loaded
			known_spells[s.spell_id] = s


func knows_spell(spell_id: String) -> bool:
	return known_spells.has(spell_id)


func get_spell(spell_id: String) -> Spell:
	return known_spells.get(spell_id) as Spell


func get_learnable_display_lines() -> PackedStringArray:
	var lines: PackedStringArray = []
	for row in LEARNABLE_CATALOG:
		var sid: String = str(row.get("spell_id", ""))
		if sid.is_empty() or knows_spell(sid):
			continue
		var nm: String = str(row.get("spell_name", sid))
		var cost: int = int(row.get("mana_cost", 0))
		lines.append("%s — %d MP" % [nm, cost])
	return lines


func spend_mana(cost: int) -> bool:
	if cost < 0:
		return false
	if mana_current < cost:
		return false
	mana_current -= cost
	return true


func regen_mana_combat_tick() -> void:
	mana_current = mini(mana_current + 1, mana_max)

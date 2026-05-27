## Base enemy node: HP, ATK, optional mana + known spells, physical immunity for Shade.
class_name Enemy
extends Node2D

const MSG_NO_EFFECT := "No effect"

@export var definition_id: String = ""

var display_name: String = ""
var max_hp: int = 1
var current_hp: int = 1
var atk: int = 1
var physical_immune: bool = false
var max_mana: int = 0
var current_mana: int = 0
var known_spell_ids: Array[String] = []

var _rng: RandomNumberGenerator = RandomNumberGenerator.new()


func _ready() -> void:
	_rng.randomize()
	if definition_id != "":
		load_from_definition_id(definition_id)


func load_from_definition_id(id: String) -> bool:
	var d := EnemyDefinitions.get_enemy_definition(id)
	if d.is_empty():
		push_warning("Enemy: unknown definition_id %s" % id)
		return false
	definition_id = id
	display_name = str(d.get("display_name", id))
	max_hp = int(d.get("max_hp", 1))
	current_hp = max_hp
	atk = int(d.get("atk", 1))
	physical_immune = bool(d.get("physical_immune", false))
	max_mana = int(d.get("max_mana", 0))
	current_mana = max_mana
	known_spell_ids.clear()
	var spells: Variant = d.get("spells", [])
	if spells is Array:
		for s in spells:
			known_spell_ids.append(str(s))
	return true


func is_alive() -> bool:
	return current_hp > 0


## Combat hook: regen 1 mana per turn up to max (Secundus combat pacing).
func on_combat_turn_start() -> void:
	if max_mana <= 0:
		return
	current_mana = mini(current_mana + 1, max_mana)


func can_cast(spell_id: String) -> bool:
	if not is_alive():
		return false
	if spell_id not in known_spell_ids:
		return false
	var cost := EnemyDefinitions.get_spell_mana_cost(spell_id)
	return current_mana >= cost


func spend_mana_for(spell_id: String) -> bool:
	if not can_cast(spell_id):
		return false
	var cost := EnemyDefinitions.get_spell_mana_cost(spell_id)
	current_mana -= cost
	return true


## Returns applied damage and a floating combat label (e.g. physical immunity).
func apply_incoming_damage(raw_amount: int, is_physical: bool) -> Dictionary:
	if raw_amount < 0:
		raw_amount = 0
	if is_physical and physical_immune:
		return {"damage_applied": 0, "message": MSG_NO_EFFECT}
	var applied := mini(raw_amount, current_hp)
	current_hp -= applied
	return {"damage_applied": applied, "message": ""}


## Basic melee the Thug (and others without spells) use when AI picks attack.
func roll_basic_attack_damage() -> int:
	return maxi(atk, 1)


## Spell damage when AI picks cast (e.g. Fire Dart for the Apprentice).
func roll_spell_damage(spell_id: String) -> int:
	return EnemyDefinitions.roll_spell_damage(spell_id, _rng)

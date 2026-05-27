class_name Spell
extends Resource

@export var spell_id: String
@export var name: String
@export var mana_cost: int
@export var damage: int
@export var effect: String

func _init(p_spell_id: String = "", p_name: String = "", p_mana_cost: int = 0, p_damage: int = 0, p_effect: String = ""):
	spell_id = p_spell_id
	name = p_name
	mana_cost = p_mana_cost
	damage = p_damage
	effect = p_effect

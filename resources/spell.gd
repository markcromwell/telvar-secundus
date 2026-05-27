class_name Spell
extends Resource

## Red-rank and learned spells (spec: spell_id, name, mana_cost, damage, effect).

@export var spell_id: String = ""
@export var spell_name: String = ""
@export var mana_cost: int = 0
@export var damage: int = 0
## Free-form effect tag used by combat (e.g. "banishment", "ember").
@export var effect: String = ""

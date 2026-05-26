extends Node

## Tracks spell casting against a registered player (caster). Uses Player.spend_mana — do not modify Player.gd from here.

var _caster: Node = null


func set_caster(caster: Node) -> void:
	_caster = caster


func cast_spell(spell: Spell) -> bool:
	if spell == null or not is_instance_valid(_caster):
		return false
	if not _caster.has_method("spend_mana"):
		return false
	var cost: float = maxf(0.0, spell.mana_cost)
	var current: float = float(_caster.get("mana"))
	if current < cost:
		return false
	return bool(_caster.call("spend_mana", cost))

## Simple enemy turn AI: cast any affordable known spell, otherwise basic attack.
class_name EnemyAI
extends RefCounted

const ACTION_ATTACK := "attack"
const ACTION_CAST := "cast"
const ACTION_WAIT := "wait"


static func choose_action(enemy: Enemy) -> Dictionary:
	if enemy == null or not enemy.is_alive():
		return {"action": ACTION_WAIT}
	for spell_id in enemy.known_spell_ids:
		if enemy.can_cast(spell_id):
			return {"action": ACTION_CAST, "spell_id": spell_id}
	return {"action": ACTION_ATTACK}


static func describe_action(decision: Dictionary) -> String:
	var action := str(decision.get("action", ACTION_WAIT))
	match action:
		ACTION_CAST:
			var sid := str(decision.get("spell_id", ""))
			var spell := EnemyDefinitions.get_spell_definition(sid)
			var nm := str(spell.get("name", sid))
			return "cast:%s" % nm
		ACTION_ATTACK:
			return "attack"
		_:
			return ACTION_WAIT

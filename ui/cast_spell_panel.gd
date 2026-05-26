extends Control
## S-key spell panel: lists known spells with mana costs (Banishment included via SpellBook).


func toggle_visible() -> void:
	visible = not visible


func get_known_spell_lines() -> PackedStringArray:
	var lines: PackedStringArray = []
	for spell_id in SpellBook.known_spells.keys():
		var s: Spell = SpellBook.known_spells[spell_id] as Spell
		if s:
			lines.append("%s — %d MP" % [s.spell_name, s.mana_cost])
	return lines

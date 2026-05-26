extends Node

const DEFAULT_SPELL_PATHS: PackedStringArray = [
	"res://resources/spells/ember.tres",
	"res://resources/spells/shield_light.tres",
	"res://resources/spells/reveal.tres",
]

var known_spells: Array[Spell] = []


func _ready() -> void:
	known_spells.clear()
	for path in DEFAULT_SPELL_PATHS:
		var loaded = load(path)
		if loaded is Spell:
			known_spells.append(loaded)


func learn_spell(spell: Spell) -> void:
	if spell == null:
		return
	for existing in known_spells:
		if existing != null and existing.spell_id == spell.spell_id:
			return
	known_spells.append(spell)


func forget_spell(spell_id: String) -> void:
	var next: Array[Spell] = []
	for s in known_spells:
		if s != null and s.spell_id != spell_id:
			next.append(s)
	known_spells = next


func get_spell_by_id(spell_id: String) -> Spell:
	for s in known_spells:
		if s != null and s.spell_id == spell_id:
			return s
	return null

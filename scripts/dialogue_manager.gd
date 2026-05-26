extends Node

## Dialogue flags and coordination with lore unlocks via [method set_flag].

var _flags: Dictionary = {}

## Maps dialogue [method set_flag] keys to lore entry IDs in [code]assets/lore/lore_entries.json[/code].
const LORE_FLAGS: Dictionary = {
	"lore_wizard_ranks": "wizard_ranks",
	"lore_secundus_overview": "secundus_overview",
	"lore_twelve_districts": "twelve_districts",
	"lore_veneficturis_academy": "veneficturis_academy",
	"lore_mentor_myramar": "mentor_myramar",
	"lore_test_of_fire": "test_of_fire",
	"lore_telvar_orson": "telvar_orson",
	"lore_child_in_secundus": "child_in_secundus",
	"lore_rutilus_ring": "rutilus_ring",
	"lore_academy_daily_life": "academy_daily_life",
}


func set_flag(key: String, value) -> void:
	_flags[key] = value
	if LORE_FLAGS.has(key) and value:
		LoreManager.unlock(LORE_FLAGS[key])


func get_flag(key: String) -> Variant:
	return _flags.get(key)

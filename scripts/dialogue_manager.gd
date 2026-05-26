extends Node

## Dialogue branching flags; lore-related keys unlock entries via LoreManager.

var _flags: Dictionary = {}

## Maps dialogue flag keys to lore entry IDs (see assets/lore/lore_entries.json).
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


func get_flag(key: String):
	return _flags.get(key)

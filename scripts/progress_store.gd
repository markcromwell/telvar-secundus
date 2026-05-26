extends Node
## Persists story flags under user:// (HTML5 and desktop export compatible).

const PROGRESS_PATH := "user://telvar_progress.cfg"
const SECTION := "progress"


func mark_game_complete() -> void:
	var cf := ConfigFile.new()
	cf.load(PROGRESS_PATH)
	cf.set_value(SECTION, "game_complete", true)
	var err := cf.save(PROGRESS_PATH)
	if err != OK:
		push_warning("ProgressStore: could not save game_complete (%s)" % err)


func is_game_complete() -> bool:
	var cf := ConfigFile.new()
	if cf.load(PROGRESS_PATH) != OK:
		return false
	return bool(cf.get_value(SECTION, "game_complete", false))

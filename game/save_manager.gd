## SaveManager — FileAccess-backed save/load for manual slots (1–3) and autosave.
##
## All JSON IO goes through [SaveDataSchema] (merge defaults, stringify, parse). Gameplay code
## should call SaveManager rather than opening [FileAccess] directly so paths and error handling stay uniform.
##
## user:// paths (HTML5-safe):
##   user://save_slot_1.json … user://save_slot_3.json
##   user://save_autosave.json
##
## Loading: if a file is missing, unreadable, empty, or invalid JSON, load_slot / load_autosave
## return a full document merged with SaveDataSchema defaults (same behavior as SaveDataSchema.read_slot / read_autosave).
class_name SaveManager
extends RefCounted


## Returns `true` if a save file exists for this slot (does not validate JSON).
static func slot_file_exists(slot: int) -> bool:
	assert(slot >= 1 and slot <= 3)
	return FileAccess.file_exists(SaveDataSchema.user_slot_path(slot))


## Returns `true` if the autosave file exists (does not validate JSON).
static func autosave_file_exists() -> bool:
	return FileAccess.file_exists(SaveDataSchema.user_autosave_path())


## Writes merged JSON to `user://save_slot_N.json`. Returns `false` if FileAccess could not write.
static func save_slot(slot: int, state: Dictionary) -> bool:
	assert(slot >= 1 and slot <= 3)
	return SaveDataSchema.write_slot(slot, state)


## Writes merged JSON to `user://save_autosave.json`. Returns `false` if FileAccess could not write.
static func save_autosave(state: Dictionary) -> bool:
	return SaveDataSchema.write_autosave(state)


## Loads from slot file; on missing/invalid file returns defaults (SaveDataSchema.read_slot).
static func load_slot(slot: int) -> Dictionary:
	assert(slot >= 1 and slot <= 3)
	return SaveDataSchema.read_slot(slot)


## Loads autosave; on missing/invalid file returns defaults (SaveDataSchema.read_autosave).
static func load_autosave() -> Dictionary:
	return SaveDataSchema.read_autosave()

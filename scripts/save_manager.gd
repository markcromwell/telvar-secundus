extends Node
## Autoload: read/write JSON saves for 3 manual slots + 1 autosave, metadata for load UI,
## and world restore (scene, position, quests, inventory, HP, flags).
##
## Save consumers: nodes in group [code]save_consumer[/code] may implement
## [code]func apply_save_data(data: Dictionary) -> void[/code] and receive the full save dict.
## Recommended targets also register: [code]game_player[/code], [code]game_inventory[/code],
## [code]game_quest_state[/code], [code]game_flags[/code] for direct field application.

const SAVE_FORMAT_VERSION := 1
const SLOT_COUNT := 4

const _KEY_VERSION := "format_version"
const _KEY_TIMESTAMP_UNIX := "timestamp_unix"
const _KEY_ACT := "act_number"
const _KEY_QUEST := "current_quest_name"
const _KEY_SCENE := "scene_path"
const _KEY_PLAYER := "player"
const _KEY_INVENTORY := "inventory"
const _KEY_QUEST_STATE := "quest_state"
const _KEY_FLAGS := "flags"

var _pending_restore: Dictionary = {}


func _ready() -> void:
	if not get_tree().scene_changed.is_connected(_on_scene_tree_scene_changed):
		get_tree().scene_changed.connect(_on_scene_tree_scene_changed)


func _on_scene_tree_scene_changed() -> void:
	if _pending_restore.is_empty():
		return
	call_deferred("_apply_pending_restore")


## Returns [code]user://[/code] path for slot index 0..2 (manual) or 3 (autosave).
func get_slot_path(slot_index: int) -> String:
	assert(slot_index >= 0 and slot_index < SLOT_COUNT)
	if slot_index < 3:
		return "user://save_manual_%d.json" % (slot_index + 1)
	return "user://save_autosave.json"


## Metadata for load UI: [code]empty[/code], [code]timestamp_unix[/code], [code]act_number[/code],
## [code]current_quest_name[/code], optional [code]error[/code] (non-empty on parse/validation issues).
func read_slot_metadata(slot_index: int) -> Dictionary:
	var path := get_slot_path(slot_index)
	var out := {
		"empty": true,
		"timestamp_unix": 0,
		"act_number": 0,
		"current_quest_name": "",
		"error": "",
	}
	if not FileAccess.file_exists(path):
		return out
	var text := FileAccess.get_file_as_string(path)
	if text.is_empty():
		out["error"] = "empty_file"
		return out
	var parsed: Variant = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		out["error"] = "invalid_json"
		return out
	var data: Dictionary = parsed
	var ver: int = int(data.get(_KEY_VERSION, 0))
	if ver != SAVE_FORMAT_VERSION:
		out["error"] = "bad_format_version"
		return out
	out["empty"] = false
	out["timestamp_unix"] = int(data.get(_KEY_TIMESTAMP_UNIX, 0))
	out["act_number"] = int(data.get(_KEY_ACT, 0))
	out["current_quest_name"] = str(data.get(_KEY_QUEST, ""))
	return out


## Full save document as a Dictionary, or empty if missing/invalid.
func read_save_dict(slot_index: int) -> Dictionary:
	var path := get_slot_path(slot_index)
	if not FileAccess.file_exists(path):
		return {}
	var text := FileAccess.get_file_as_string(path)
	if text.is_empty():
		return {}
	var parsed: Variant = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		return {}
	var data: Dictionary = parsed
	if int(data.get(_KEY_VERSION, 0)) != SAVE_FORMAT_VERSION:
		return {}
	return data


func write_save_dict(slot_index: int, data: Dictionary) -> Error:
	var path := get_slot_path(slot_index)
	data[_KEY_VERSION] = SAVE_FORMAT_VERSION
	var json_text := JSON.stringify(data, "\t")
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		return FileAccess.get_open_error()
	f.store_string(json_text)
	f.close()
	return OK


## Validates shape, sets [member _pending_restore], optionally changes scene, then applies state
## (deferred after scene change when a [code]res://[/code] scene_path is used).
func restore_from_slot(slot_index: int) -> Error:
	var data := read_save_dict(slot_index)
	if data.is_empty():
		return ERR_FILE_NOT_FOUND
	if not _validate_save_for_restore(data):
		return ERR_INVALID_DATA
	_pending_restore = data.duplicate(true)
	var scene_path := str(data.get(_KEY_SCENE, ""))
	if scene_path != "" and ResourceLoader.exists(scene_path):
		var err: Error = get_tree().change_scene_to_file(scene_path)
		if err != OK:
			_pending_restore = {}
		return err
	call_deferred("_apply_pending_restore")
	return OK


func _apply_pending_restore() -> void:
	if _pending_restore.is_empty():
		return
	var data := _pending_restore
	_pending_restore = {}
	_apply_restore_data(data)
	# Menus often pause the SceneTree; clear so the loaded level can process/move immediately.
	get_tree().paused = false


func _validate_save_for_restore(data: Dictionary) -> bool:
	if int(data.get(_KEY_VERSION, 0)) != SAVE_FORMAT_VERSION:
		return false
	# Optional sections default when absent; types must be acceptable if present.
	if data.has(_KEY_PLAYER) and typeof(data[_KEY_PLAYER]) != TYPE_DICTIONARY:
		return false
	if data.has(_KEY_INVENTORY) and typeof(data[_KEY_INVENTORY]) != TYPE_ARRAY:
		return false
	if data.has(_KEY_QUEST_STATE) and typeof(data[_KEY_QUEST_STATE]) != TYPE_DICTIONARY:
		return false
	if data.has(_KEY_FLAGS) and typeof(data[_KEY_FLAGS]) != TYPE_DICTIONARY:
		return false
	return true


func _apply_restore_data(data: Dictionary) -> void:
	_apply_to_player(data)
	_apply_to_inventory(data)
	_apply_to_quest_state(data)
	_apply_to_flags(data)
	get_tree().call_group_flags(
		SceneTree.GROUP_CALL_DEFERRED,
		&"save_consumer",
		&"apply_save_data",
		data
	)


func _apply_to_player(data: Dictionary) -> void:
	var player := get_tree().get_first_node_in_group("game_player")
	if player == null:
		return
	var p: Dictionary = data.get(_KEY_PLAYER, {}) as Dictionary
	if p.is_empty():
		return
	if p.has("position"):
		var pos_val: Variant = p["position"]
		if typeof(pos_val) == TYPE_DICTIONARY:
			var d: Dictionary = pos_val
			if player is Node2D:
				(player as Node2D).global_position = Vector2(
					float(d.get("x", 0.0)),
					float(d.get("y", 0.0))
				)
			elif player is Node3D:
				(player as Node3D).global_position = Vector3(
					float(d.get("x", 0.0)),
					float(d.get("y", 0.0)),
					float(d.get("z", 0.0))
				)
	if player.has_method("set_hp_from_save"):
		player.call("set_hp_from_save", int(p.get("hp", 0)), int(p.get("max_hp", 0)))
	elif "hp" in player and "max_hp" in player:
		player.set("max_hp", int(p.get("max_hp", int(player.get("max_hp")))))
		player.set("hp", clampi(int(p.get("hp", 0)), 0, int(player.get("max_hp"))))


func _apply_to_inventory(data: Dictionary) -> void:
	var inv := get_tree().get_first_node_in_group("game_inventory")
	if inv == null:
		return
	var items: Array = data.get(_KEY_INVENTORY, []) as Array
	if inv.has_method("restore_inventory_from_save"):
		inv.call("restore_inventory_from_save", items)
	elif inv.has_method("apply_save_data"):
		inv.call("apply_save_data", data)


func _apply_to_quest_state(data: Dictionary) -> void:
	var qs := get_tree().get_first_node_in_group("game_quest_state")
	if qs == null:
		return
	var qdict: Dictionary = data.get(_KEY_QUEST_STATE, {}) as Dictionary
	if qs.has_method("restore_quest_state_from_save"):
		qs.call("restore_quest_state_from_save", qdict)
	elif qs.has_method("apply_save_data"):
		qs.call("apply_save_data", data)


func _apply_to_flags(data: Dictionary) -> void:
	var fg := get_tree().get_first_node_in_group("game_flags")
	if fg == null:
		return
	var flags: Dictionary = data.get(_KEY_FLAGS, {}) as Dictionary
	if fg.has_method("restore_flags_from_save"):
		fg.call("restore_flags_from_save", flags)
	elif fg.has_method("apply_save_data"):
		fg.call("apply_save_data", data)

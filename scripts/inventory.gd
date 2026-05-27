extends Node
## Minimal inventory for bootstrap; per-slot JSON under user:// for NG+ (phase 2717).

const SEALED_WINGS_KEY_ID := &"sealed_wings_key"
const SAVE_SLOT_COUNT: int = 3
const SLOT_SAVE_KEY_NG_PLUS := "ng_plus_unlocked"

var _items: Dictionary = {}  # StringName -> int count
var _active_slot: int = 0


func set_item_count(id: StringName, count: int) -> void:
	if count <= 0:
		_items.erase(id)
	else:
		_items[id] = count


func get_item_count(id: StringName) -> int:
	return int(_items.get(id, 0))


func try_consume_sealed_wings_key() -> bool:
	if get_item_count(SEALED_WINGS_KEY_ID) < 1:
		return false
	var n := get_item_count(SEALED_WINGS_KEY_ID) - 1
	set_item_count(SEALED_WINGS_KEY_ID, n)
	return true


func get_active_slot() -> int:
	return _active_slot


func set_active_slot(slot_index: int) -> void:
	_active_slot = clampi(slot_index, 0, SAVE_SLOT_COUNT - 1)


func _slot_save_path(slot_index: int) -> String:
	return "user://slot_%d.save.json" % slot_index


func _read_slot_dict(slot_index: int) -> Dictionary:
	var path := _slot_save_path(slot_index)
	if not FileAccess.file_exists(path):
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var txt := f.get_as_text()
	f.close()
	var parsed: Variant = JSON.parse_string(txt)
	if typeof(parsed) != TYPE_DICTIONARY:
		return {}
	return parsed as Dictionary


func _write_slot_dict(slot_index: int, data: Dictionary) -> void:
	var path := _slot_save_path(slot_index)
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		push_warning("Inventory: could not write slot file: %s" % path)
		return
	f.store_string(JSON.stringify(data))
	f.close()


func unlock_ng_plus_for_active_slot() -> void:
	var data := _read_slot_dict(_active_slot)
	data[SLOT_SAVE_KEY_NG_PLUS] = true
	_write_slot_dict(_active_slot, data)


func is_ng_plus_unlocked(slot_index: int = -1) -> bool:
	var s: int = _active_slot if slot_index < 0 else clampi(slot_index, 0, SAVE_SLOT_COUNT - 1)
	var data := _read_slot_dict(s)
	return bool(data.get(SLOT_SAVE_KEY_NG_PLUS, false))

extends Node
## Minimal inventory for bootstrap; expand with save slots / NG+ in later specs.

const SEALED_WINGS_KEY_ID := &"sealed_wings_key"

var _items: Dictionary = {}  # StringName -> int count


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

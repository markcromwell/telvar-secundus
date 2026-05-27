extends Node
## Runtime item stacks (item id -> count). Used by world interactables such as SealedDoor.

var _counts: Dictionary = {}


func has_item(item_id: StringName, min_amount: int = 1) -> bool:
	return _counts.get(item_id, 0) >= min_amount


func get_count(item_id: StringName) -> int:
	return int(_counts.get(item_id, 0))


func add_item(item_id: StringName, amount: int = 1) -> void:
	if amount <= 0:
		return
	_counts[item_id] = get_count(item_id) + amount


func remove_item(item_id: StringName, amount: int = 1) -> bool:
	if not has_item(item_id, amount):
		return false
	var next: int = get_count(item_id) - amount
	if next <= 0:
		_counts.erase(item_id)
	else:
		_counts[item_id] = next
	return true


func clear() -> void:
	_counts.clear()

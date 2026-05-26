extends RefCounted
class_name Inventory

## Owned item instances (resources), in pickup order.
var items: Array[Item] = []


func add_item(item: Item) -> void:
	if item == null:
		push_warning("Inventory.add_item: ignored null item")
		return
	items.append(item)


func has_item_id(item_id: String) -> bool:
	for it in items:
		if it != null and it.id == item_id:
			return true
	return false


func count_item_id(item_id: String) -> int:
	var n := 0
	for it in items:
		if it != null and it.id == item_id:
			n += 1
	return n

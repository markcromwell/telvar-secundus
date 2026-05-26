extends Node
## Minimal inventory for quest items (e.g. assessment band).

var items: Array[String] = []


func add_item(item_id: String) -> void:
	if item_id.is_empty():
		return
	if item_id in items:
		return
	items.append(item_id)


func has_item(item_id: String) -> bool:
	return item_id in items

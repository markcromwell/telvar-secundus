extends Node
## Minimal inventory autoload. Other specs may replace or extend this API.

var _items: Array[String] = []


func add_item(item_id: String) -> void:
	if item_id not in _items:
		_items.append(item_id)


func has_item(item_id: String) -> bool:
	return item_id in _items


func get_items() -> Array[String]:
	return _items.duplicate()

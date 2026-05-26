extends Resource
class_name ItemTable

@export var items: Dictionary = {}

func get_item(item_id: StringName) -> ItemData:
	return items.get(item_id)

func has_item(item_id: StringName) -> bool:
	return items.has(item_id)

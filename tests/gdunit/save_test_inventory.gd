extends Node
## Test double: minimal [code]game_inventory[/code] consumer for SaveManager restore.


var last_items: Array = []


func _ready() -> void:
	add_to_group(&"game_inventory")


func restore_inventory_from_save(items: Array) -> void:
	last_items = items.duplicate()

extends Node

const ITEM_TABLE_PATH := "res://resources/items/item_table.tres"

var item_table: ItemTable

func _ready() -> void:
	load_items()

func load_items() -> void:
	item_table = load(ITEM_TABLE_PATH) as ItemTable
	if item_table == null:
		push_error("Unable to load item table: %s" % ITEM_TABLE_PATH)

func get_item(item_id: StringName) -> ItemData:
	if item_table == null:
		load_items()
	return item_table.get_item(item_id) if item_table != null else null

func has_item(item_id: StringName) -> bool:
	if item_table == null:
		load_items()
	return item_table.has_item(item_id) if item_table != null else false

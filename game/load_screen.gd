extends Control
## Load-game UI: lists `user://save_*.json` (including autosave) and restores the saved scene.

@onready var _save_list: ItemList = $SaveList


func _ready() -> void:
	_refresh_list()
	_save_list.item_activated.connect(_on_item_activated)


func _refresh_list() -> void:
	_save_list.clear()
	for path in SaveManager.list_user_save_paths():
		var idx := _save_list.add_item(SaveManager.get_slot_display_name(path))
		_save_list.set_item_metadata(idx, path)


func _on_item_activated(index: int) -> void:
	var path: Variant = _save_list.get_item_metadata(index)
	if typeof(path) != TYPE_STRING:
		return
	var err := SaveManager.load_save_from_path(path)
	if err != OK:
		# Load UI only; avoid visible toasts. Silent failure keeps the list open.
		pass

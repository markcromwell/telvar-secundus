extends Node
## Central hook for scene changes. Emits ``scene_changed`` after navigation.
## Autosave (slot 0) runs on each emission by merging into the existing autosave payload.

signal scene_changed(previous_scene: String, new_scene: String)


func _ready() -> void:
	scene_changed.connect(_on_scene_changed)


func notify_scene_changed(previous_scene: String, new_scene: String) -> void:
	scene_changed.emit(previous_scene, new_scene)


func _on_scene_changed(previous_scene: String, new_scene: String) -> void:
	var data: Dictionary = SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT)
	data["current_scene"] = new_scene
	if not SaveSystem.save_to_slot(SaveSystem.AUTOSAVE_SLOT, data):
		push_warning("Autosave failed: %s" % SaveSystem.last_save_error)

extends Node
## Canonical scene changes: silently autosaves to user://save_autosave.json, then loads the next scene.
## Route all scene switches through this autoload so autosave runs every time.


func change_scene_to_file(path: String) -> Error:
	SaveManager.autosave_silent()
	return get_tree().change_scene_to_file(path)


func change_scene_to_packed(scene: PackedScene) -> Error:
	SaveManager.autosave_silent()
	return get_tree().change_scene_to_packed(scene)

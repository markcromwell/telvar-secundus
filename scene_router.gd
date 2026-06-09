extends Node
class_name SceneRouter

## Owns the active WorldRoot scene and swaps it on door / district transitions.
##
## [method swap_to] always frees the outgoing WorldRoot child *before* instancing
## the replacement so two heavy scenes never coexist in memory (resource-leak
## mitigation). Instantiation is retried up to [constant MAX_INSTANTIATE_ATTEMPTS]
## times, and a missing or unloadable target falls back to
## [constant FALLBACK_SCENE] rather than leaving WorldRoot blank or crashing.
##
## Door and DistrictZone nodes anywhere inside the active scene are wired up
## automatically: ``door_entered(target_scene)`` triggers a swap, and
## ``district_entered(name)`` is forwarded to ambient audio (and optionally a
## mapped scene). Listeners can observe [signal scene_changed] and
## [signal transition_error] for logging / smoke-test assertions.

## Emitted after WorldRoot's active child changes. Carries the new scene's name.
signal scene_changed(scene_name: String)
## Emitted when a transition fails or falls back. For logging / debugging.
signal transition_error(target_scene: String, message: String)

## Scene used when a requested target is missing or fails to load.
const FALLBACK_SCENE := "res://apprentice_room.tscn"
## How many times to retry load + instantiate before giving up on a target.
const MAX_INSTANTIATE_ATTEMPTS := 3

## WorldRoot node whose single child is the active scene. May be set in the
## editor via this NodePath or programmatically via [method set_world_root].
@export var world_root_path: NodePath
## Optional district-name -> scene-path map for DistrictZone transitions.
@export var district_scenes: Dictionary = {}

var _world_root: Node = null
var _active_scene: Node = null
var _active_scene_path: String = ""


func _ready() -> void:
	if _world_root == null and not world_root_path.is_empty():
		set_world_root(get_node_or_null(world_root_path))


## Assigns the WorldRoot container and adopts any scene already parented under
## it (e.g. a boot scene placed in the editor) so its triggers get wired up.
func set_world_root(node: Node) -> void:
	_world_root = node
	if _world_root == null:
		return
	for child in _world_root.get_children():
		_active_scene = child
		_active_scene_path = child.scene_file_path
		_connect_scene_signals(child)
		break


## Swaps WorldRoot's active child to the scene at ``scene_path``. Frees the
## outgoing child first, retries instancing, and falls back to
## [constant FALLBACK_SCENE] on failure. Returns true on success.
func swap_to(scene_path: String) -> bool:
	if _world_root == null:
		_report_error(scene_path, "WorldRoot is not set; cannot swap")
		return false

	# Resource-leak mitigation: free the outgoing scene before instancing the
	# replacement so two heavy scenes never coexist in memory.
	_free_active_scene()

	var loaded_path := scene_path
	var instance := _instantiate_with_retry(scene_path)
	if instance == null and scene_path != FALLBACK_SCENE:
		_report_error(scene_path, "load failed; falling back to %s" % FALLBACK_SCENE)
		loaded_path = FALLBACK_SCENE
		instance = _instantiate_with_retry(FALLBACK_SCENE)
	if instance == null:
		_report_error(loaded_path, "scene load failed and fallback unavailable")
		return false

	_world_root.add_child(instance)
	_active_scene = instance
	_active_scene_path = loaded_path
	_connect_scene_signals(instance)
	scene_changed.emit(get_active_scene_name())
	return true


## Name of the currently active WorldRoot scene, or "" if none.
func get_active_scene_name() -> String:
	if is_instance_valid(_active_scene):
		return _active_scene.name
	return ""


## res:// path of the currently active WorldRoot scene, or "" if unknown.
func get_active_scene_path() -> String:
	return _active_scene_path


func _free_active_scene() -> void:
	if is_instance_valid(_active_scene):
		# Detach immediately so the old scene never coexists in-tree with the
		# new one (queue_free alone defers removal to end of frame).
		var parent := _active_scene.get_parent()
		if parent != null:
			parent.remove_child(_active_scene)
		_active_scene.queue_free()
	_active_scene = null
	_active_scene_path = ""


func _instantiate_with_retry(scene_path: String) -> Node:
	if scene_path.is_empty():
		return null
	if not ResourceLoader.exists(scene_path):
		push_warning("SceneRouter: scene resource does not exist: %s" % scene_path)
		return null
	for attempt in range(MAX_INSTANTIATE_ATTEMPTS):
		var packed := load(scene_path) as PackedScene
		if packed != null:
			var instance := packed.instantiate()
			if instance != null:
				return instance
		push_warning("SceneRouter: instantiate attempt %d/%d failed for %s" % [
			attempt + 1, MAX_INSTANTIATE_ATTEMPTS, scene_path
		])
	return null


## Recursively wires Door / DistrictZone triggers within a freshly added scene.
func _connect_scene_signals(node: Node) -> void:
	if node.has_signal("door_entered"):
		var door_cb := Callable(self, "_on_door_entered")
		if not node.is_connected("door_entered", door_cb):
			node.connect("door_entered", door_cb)
	if node.has_signal("district_entered"):
		var district_cb := Callable(self, "_on_district_entered")
		if not node.is_connected("district_entered", district_cb):
			node.connect("district_entered", district_cb)
	for child in node.get_children():
		_connect_scene_signals(child)


func _on_door_entered(target_scene: String) -> void:
	# An unconfigured door must not swap (and thus free) the current scene.
	if target_scene.is_empty():
		_report_error(target_scene, "door has no target_scene configured; ignoring")
		return
	swap_to(target_scene)


func _on_district_entered(district_name: String) -> void:
	# Ambient music follows the district (AudioManager autoload, if registered).
	var audio := get_node_or_null("/root/AudioManager")
	if audio != null and audio.has_method("set_current_district"):
		audio.set_current_district(district_name)
	# Route to a mapped scene if one is configured for this district.
	var target: String = district_scenes.get(district_name, "")
	if not target.is_empty():
		swap_to(target)


func _report_error(target_scene: String, message: String) -> void:
	push_warning("SceneRouter: %s (%s)" % [message, target_scene])
	transition_error.emit(target_scene, message)

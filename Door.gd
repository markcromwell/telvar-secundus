extends Area2D
class_name Door

## Door / scene-transition trigger.
##
## On body entry the door emits ``door_entered(target_scene)`` for the
## SceneRouter to consume (swapping WorldRoot to the interior), and plays its
## creak SFX via the **SFXManager** autoload (**SFX** bus) -- the original
## creak-only behavior is preserved in [method on_transition].

## Emitted when a body walks onto the door. ``target_scene`` is the res:// path
## the SceneRouter should swap WorldRoot to (may be empty if unconfigured).
signal door_entered(target_scene: String)

## Scene this door leads to. SceneRouter swaps WorldRoot to this on entry.
@export_file("*.tscn") var target_scene: String = ""
@export var creak_sound: AudioStream


func _ready() -> void:
	# Detect bodies walking onto the door; mirrors DistrictZone's trigger setup.
	monitoring = true
	monitorable = false
	if not body_entered.is_connected(_on_body_entered):
		body_entered.connect(_on_body_entered)


func _on_body_entered(_body: Node2D) -> void:
	on_transition()
	door_entered.emit(target_scene)


## Plays the door creak SFX via the SFXManager autoload (SFX bus).
func on_transition() -> void:
	if creak_sound == null:
		return
	SFXManager.play(creak_sound)

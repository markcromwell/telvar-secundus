extends Node

## Spell cast SFX: **shimmer** when set, otherwise **whoosh**. Routed through **SFXManager** (**SFX** bus).

@export var shimmer_sound: AudioStream
@export var whoosh_sound: AudioStream


func play_cast_sfx() -> void:
	var stream: AudioStream = shimmer_sound if shimmer_sound != null else whoosh_sound
	if stream == null:
		return
	SFXManager.play(stream)

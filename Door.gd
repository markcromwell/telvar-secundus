extends Node

## Door / room transition: creak SFX via **SFXManager** autoload (**SFX** bus).

@export var creak_sound: AudioStream


func on_transition() -> void:
	if creak_sound == null:
		return
	SFXManager.play(creak_sound)

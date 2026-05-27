extends Area2D

## Combat hit feedback: plays **hit** SFX via **SFXManager** (**SFX** bus) when damage is applied.

@export var hit_sound: AudioStream


func apply_damage(_target: Node, _amount: int) -> void:
	if hit_sound != null:
		SFXManager.play(hit_sound)

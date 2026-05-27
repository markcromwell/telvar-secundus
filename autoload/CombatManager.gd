extends Node
## Autoload: forwards combat lifecycle to AudioManager (phase 2742).
## Start: 0.5s ambient fade-out then battle theme. Victory: sting then ambient fade-in.
## Flee / non-victory exit: duck combat and resume ambient without sting.

@export var battle_theme: AudioStream
@export var victory_sting: AudioStream


func on_combat_started(battle_stream_override: AudioStream = null) -> void:
	var stream: AudioStream = battle_stream_override if battle_stream_override != null else battle_theme
	if stream == null:
		return
	AudioManager.enter_combat(stream)


func on_combat_victory(sting_stream_override: AudioStream = null) -> void:
	var sting: AudioStream = sting_stream_override if sting_stream_override != null else victory_sting
	if sting != null:
		AudioManager.play_victory_sting(sting)
	else:
		AudioManager.exit_combat_resume_ambient_only()


func on_combat_ended_without_victory() -> void:
	AudioManager.exit_combat_resume_ambient_only()

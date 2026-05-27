extends Node

## Lightweight SFX routing (extend when new clips are added).

const SFX := {
	"footstep_stone": preload("res://assets/audio/sfx/footstep_stone.wav"),
}

var _sfx_player: AudioStreamPlayer


func _ready() -> void:
	_sfx_player = AudioStreamPlayer.new()
	add_child(_sfx_player)


func _play_sfx(key: String) -> void:
	var stream: AudioStream = SFX.get(key, null)
	if stream == null:
		push_warning("AudioManager: unknown sfx %s" % key)
		return
	_sfx_player.stream = stream
	_sfx_player.play()


func play_footstep_stone() -> void:
	_play_sfx("footstep_stone")

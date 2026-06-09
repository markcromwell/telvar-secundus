extends Node
## Autoload: ambient ↔ combat music and victory sting (phase 2741).
## Combat enter: 0.5s ambient fade-out, then battle theme. Victory: sting (~2s), then ambient fade-in.

signal ambient_started(location: String)

const FADE_OUT_AMBIENT_SEC := 0.5
const FADE_IN_AMBIENT_SEC := 0.5
const COMBAT_DUCK_SEC := 0.2
const VICTORY_STING_SEC := 2.0
const SILENT_DB := -80.0

const AMBIENT_STREAMS := {
	"apprentice_room": "res://assets/audio/ambient_merchant_medieval.wav",
	"merchant_district": "res://assets/audio/ambient_merchant_medieval.wav",
	"veneficturis": "res://assets/audio/ambient_veneficturis_dark.wav",
	"rookery": "res://assets/audio/ambient_rookery_tension.wav",
}

@onready var ambient_player: AudioStreamPlayer = $AmbientPlayer
@onready var combat_player: AudioStreamPlayer = $CombatPlayer
@onready var sting_player: AudioStreamPlayer = $VictoryStingPlayer

var _ambient_resume_stream: AudioStream
var _transition_tween: Tween


func _kill_transition_tween() -> void:
	if _transition_tween != null and is_instance_valid(_transition_tween):
		_transition_tween.kill()
	_transition_tween = null


func fade_out_ambient(duration_sec: float = FADE_OUT_AMBIENT_SEC) -> Tween:
	"""Tween ambient volume to silence over ``duration_sec`` (default 0.5s). Await ``finished`` on the returned tween if needed."""
	_kill_transition_tween()
	_transition_tween = create_tween()
	_transition_tween.tween_property(ambient_player, "volume_db", SILENT_DB, duration_sec)
	return _transition_tween


func play_ambient(stream: AudioStream, from_silent: bool = false) -> void:
	_kill_transition_tween()
	ambient_player.stream = stream
	_ambient_resume_stream = stream
	if from_silent:
		ambient_player.volume_db = SILENT_DB
		ambient_player.play()
		_transition_tween = create_tween()
		_transition_tween.tween_property(ambient_player, "volume_db", 0.0, FADE_IN_AMBIENT_SEC)
	else:
		ambient_player.volume_db = 0.0
		ambient_player.play()


func start_ambient(location: String) -> void:
	var key := location.strip_edges().to_lower()
	var path: String = AMBIENT_STREAMS.get(key, "")
	if path.is_empty():
		push_warning("AudioManager: unknown ambient location: %s" % location)
		return
	if not ResourceLoader.exists(path):
		push_warning("AudioManager: missing ambient stream for %s: %s" % [key, path])
		return
	var loaded := load(path)
	if not (loaded is AudioStream):
		push_warning("AudioManager: not an AudioStream for %s: %s" % [key, path])
		return
	play_ambient(loaded as AudioStream)
	ambient_started.emit(key)


func enter_combat(battle_stream: AudioStream) -> void:
	"""Fade ambient out in 0.5s, then start battle theme (no overlap with ambient)."""
	_kill_transition_tween()
	sting_player.stop()
	if ambient_player.stream != null:
		_ambient_resume_stream = ambient_player.stream

	combat_player.stream = battle_stream
	combat_player.volume_db = 0.0

	_transition_tween = create_tween()
	if ambient_player.playing:
		_transition_tween.tween_property(ambient_player, "volume_db", SILENT_DB, FADE_OUT_AMBIENT_SEC)
	_transition_tween.tween_callback(func() -> void:
		ambient_player.stop()
		combat_player.play()
	)


func exit_combat_resume_ambient_only() -> void:
	"""Leave combat without a sting (e.g. flee): duck combat, resume last ambient with fade-in."""
	_kill_transition_tween()
	sting_player.stop()
	_transition_tween = create_tween()
	_transition_tween.tween_property(combat_player, "volume_db", SILENT_DB, COMBAT_DUCK_SEC)
	_transition_tween.tween_callback(func() -> void:
		combat_player.stop()
		combat_player.volume_db = 0.0
		_resume_ambient_fade_in()
	)


func play_victory_sting(sting_stream: AudioStream, sting_duration_sec: float = VICTORY_STING_SEC) -> void:
	"""Fade battle out, play the victory sting for ``sting_duration_sec`` (default 2s), then resume ambient with fade-in."""
	_kill_transition_tween()
	sting_player.stop()

	_transition_tween = create_tween()
	_transition_tween.tween_property(combat_player, "volume_db", SILENT_DB, COMBAT_DUCK_SEC)
	_transition_tween.tween_callback(func() -> void:
		combat_player.stop()
		combat_player.volume_db = 0.0
	)
	_transition_tween.tween_callback(func() -> void:
		sting_player.stream = sting_stream
		sting_player.play()
	)
	_transition_tween.tween_interval(sting_duration_sec)
	_transition_tween.tween_callback(func() -> void:
		sting_player.stop()
		_resume_ambient_fade_in()
	)


func _resume_ambient_fade_in() -> void:
	if _ambient_resume_stream == null:
		return
	ambient_player.stream = _ambient_resume_stream
	ambient_player.volume_db = SILENT_DB
	ambient_player.play()
	var fade := create_tween()
	fade.tween_property(ambient_player, "volume_db", 0.0, FADE_IN_AMBIENT_SEC)

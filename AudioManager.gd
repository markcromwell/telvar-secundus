extends Node
## Phase 2733: autoload audio — district ambient (70% linear), 1s crossfades, SFX, bus volume.
## Detects Secundus district via set_current_district(); wire gameplay zones to call it.

const CROSSFADE_SEC := 1.0
## Target linear gain for ambient music on Music bus players (0.7 = 70%).
const AMBIENT_LINEAR := 0.7
const SILENT_DB := -80.0

const KEY_MERCHANT := "merchant_district"
const KEY_VENEF := "veneficturis"
const KEY_ROOKERY := "rookery"

const DISTRICT_STREAMS := {
	KEY_MERCHANT: "res://assets/audio/ambient_merchant_medieval.wav",
	KEY_VENEF: "res://assets/audio/ambient_veneficturis_dark.wav",
	KEY_ROOKERY: "res://assets/audio/ambient_rookery_tension.wav",
}

## Normalized lookup keys (lowercase) -> district id used in DISTRICT_STREAMS
const DISTRICT_ALIASES := {
	"merchant district": KEY_MERCHANT,
	"merchantdistrict": KEY_MERCHANT,
	KEY_MERCHANT: KEY_MERCHANT,
	"veneficturis": KEY_VENEF,
	KEY_VENEF: KEY_VENEF,
	"rookery": KEY_ROOKERY,
	KEY_ROOKERY: KEY_ROOKERY,
}

@onready var _music_a: AudioStreamPlayer = $MusicA
@onready var _music_b: AudioStreamPlayer = $MusicB
@onready var _sfx_player: AudioStreamPlayer = $SFXPlayer

var _lead: AudioStreamPlayer
var _current_district: String = ""
var _fade_tween: Tween


func _ready() -> void:
	_lead = _music_a
	_music_a.bus = "Music"
	_music_b.bus = "Music"
	_sfx_player.bus = "SFX"
	_music_a.volume_db = linear_to_db(AMBIENT_LINEAR)
	_music_b.volume_db = linear_to_db(AMBIENT_LINEAR)


## Call from Area2D / gameplay when the player enters a Secundus district.
func set_current_district(area_label: String) -> void:
	var key := _resolve_district_key(area_label)
	if key.is_empty():
		return
	var path: String = DISTRICT_STREAMS.get(key, "")
	if path.is_empty():
		return
	if key == _current_district and _lead.playing() and _lead.stream != null:
		return
	var loaded := load(path)
	if not (loaded is AudioStream):
		push_warning("AudioManager: not an AudioStream: %s" % path)
		return
	_current_district = key
	_crossfade_music(loaded as AudioStream)


## Manual music (e.g. cutscenes). Clears district tracking so ambient can resume later.
func play_music(stream: AudioStream) -> void:
	if stream == null:
		return
	_current_district = ""
	_crossfade_music(stream)


func play_sfx(stream: AudioStream) -> void:
	if stream == null:
		return
	_sfx_player.stream = stream
	_sfx_player.play()


func set_volume(bus_name: String, volume_db: float) -> void:
	var idx := AudioServer.get_bus_index(bus_name)
	if idx >= 0:
		AudioServer.set_bus_volume_db(idx, volume_db)


func _collapse_spaces(s: String) -> String:
	var parts := s.split(" ", false)
	if parts.is_empty():
		return ""
	var out: String = parts[0]
	for i in range(1, parts.size()):
		out += " " + parts[i]
	return out


func _resolve_district_key(raw: String) -> String:
	var t := raw.strip_edges().to_lower()
	t = t.replace("_", " ").replace("-", " ")
	t = _collapse_spaces(t)
	return DISTRICT_ALIASES.get(t, "")


func _other(player: AudioStreamPlayer) -> AudioStreamPlayer:
	return _music_b if player == _music_a else _music_a


func _kill_fade() -> void:
	if _fade_tween != null and is_instance_valid(_fade_tween):
		_fade_tween.kill()
	_fade_tween = null


func _prepare_ambient_stream(stream: AudioStream) -> void:
	# Procedural WAVs are integer-cycle sine bursts (ffmpeg) so LOOP_FORWARD is click-free.
	if stream is AudioStreamWAV:
		var wav := stream as AudioStreamWAV
		wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
		wav.loop_begin = 0
		var samples := int(round(stream.get_length() * float(wav.mix_rate)))
		wav.loop_end = maxi(samples - 1, 0)


func _crossfade_music(next: AudioStream) -> void:
	_prepare_ambient_stream(next)
	_kill_fade()
	var outgoing := _lead
	var incoming := _other(outgoing)
	var target_db := linear_to_db(AMBIENT_LINEAR)
	if not outgoing.playing() or outgoing.stream == null:
		outgoing.stream = next
		outgoing.volume_db = target_db
		outgoing.play()
		_lead = outgoing
		return
	if outgoing.stream == next:
		return
	incoming.stream = next
	incoming.volume_db = SILENT_DB
	incoming.play()
	_fade_tween = create_tween()
	_fade_tween.set_parallel(true)
	_fade_tween.tween_property(outgoing, "volume_db", SILENT_DB, CROSSFADE_SEC)
	_fade_tween.tween_property(incoming, "volume_db", target_db, CROSSFADE_SEC)
	_fade_tween.chain().tween_callback(_finish_crossfade.bind(outgoing, incoming))


func _finish_crossfade(outgoing: AudioStreamPlayer, incoming: AudioStreamPlayer) -> void:
	outgoing.stop()
	outgoing.stream = null
	outgoing.volume_db = linear_to_db(AMBIENT_LINEAR)
	_lead = incoming
	_fade_tween = null

extends Node

@onready var music_player: AudioStreamPlayer = $MusicPlayer
@onready var sfx_player: AudioStreamPlayer = $SFXPlayer


func play_music(stream: AudioStream) -> void:
	music_player.stream = stream
	music_player.play()


func play_sfx(stream: AudioStream) -> void:
	sfx_player.stream = stream
	sfx_player.play()


func set_volume(bus_name: String, volume_db: float) -> void:
	var bus_idx := AudioServer.get_bus_index(bus_name)
	if bus_idx >= 0:
		AudioServer.set_bus_volume_db(bus_idx, volume_db)

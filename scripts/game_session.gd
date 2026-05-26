extends Node
## Tracks session play time from engine start for end-of-game display.

var _started_at_msec: int = 0


func _ready() -> void:
	_started_at_msec = Time.get_ticks_msec()


func get_elapsed_seconds() -> float:
	return (Time.get_ticks_msec() - _started_at_msec) / 1000.0

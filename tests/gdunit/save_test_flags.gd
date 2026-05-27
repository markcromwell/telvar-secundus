extends Node
## Test double: minimal [code]game_flags[/code] consumer for SaveManager restore.


var last_flags: Dictionary = {}


func _ready() -> void:
	add_to_group(&"game_flags")


func restore_flags_from_save(flags: Dictionary) -> void:
	last_flags = flags.duplicate(true)

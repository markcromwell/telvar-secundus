extends Node
## Test double: minimal [code]game_quest_state[/code] consumer for SaveManager restore.


var last_state: Dictionary = {}


func _ready() -> void:
	add_to_group(&"game_quest_state")


func restore_quest_state_from_save(state: Dictionary) -> void:
	last_state = state.duplicate(true)

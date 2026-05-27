extends Control
class_name DialogueBox

## In-world dialogue panel. Plays the shared UI click on each advance (mouse or accept).


func _gui_input(event: InputEvent) -> void:
	if not visible:
		return
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
			advance_dialogue()
			accept_event()


func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if event.is_action_pressed(&"ui_accept"):
		advance_dialogue()
		get_viewport().set_input_as_handled()


## Call when advancing to the next line (also used by external choice handlers).
func advance_dialogue() -> void:
	_play_advance_click_sfx()
	# Game-specific line progression is implemented in a later phase.


func _play_advance_click_sfx() -> void:
	if DialogueManager.singleton != null:
		DialogueManager.singleton.play_ui_click()

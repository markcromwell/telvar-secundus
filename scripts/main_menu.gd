extends Control
## Entry menu: start the story or view scrolling credits (NPO attribution) without ending the game.


func _on_play_button_pressed() -> void:
	GameSession.credits_exit_to_main_menu = false
	get_tree().change_scene_to_file("res://scenes/cutscene_myramar_corridor.tscn")


func _on_credits_button_pressed() -> void:
	GameSession.credits_exit_to_main_menu = true
	get_tree().change_scene_to_file("res://scenes/credits_roll.tscn")

extends Control

# Main menu controller. Each button routes through the Menu autoload so the
# completed save/load and settings systems drive the actual scene transitions.

func _on_new_game_pressed() -> void:
	Menu.request_new_game()


func _on_load_pressed() -> void:
	Menu.request_load_game()


func _on_settings_pressed() -> void:
	Menu.request_settings()


func _on_credits_pressed() -> void:
	Menu.request_credits()

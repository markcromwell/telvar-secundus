extends Control

@onready var credits_button: Button = $TitleScreen/CreditsButton
@onready var credits_panel: Control = $TitleScreen/CreditsPanel


func _on_credits_pressed() -> void:
	credits_panel.visible = true


func _on_credits_closed() -> void:
	credits_panel.visible = false

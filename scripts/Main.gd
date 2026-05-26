extends Control

@onready var credits_button: Button = $TitleScreen/CreditsButton
@onready var credits_panel: Control = $TitleScreen/CreditsPanel


func _on_credits_pressed() -> void:
	# Same-origin on Pages: CREDITS.md is copied next to index.html in CI (no CORS).
	if OS.has_feature("web"):
		OS.shell_open("CREDITS.md")
	else:
		credits_panel.visible = true


func _on_credits_closed() -> void:
	credits_panel.visible = false

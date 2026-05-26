## Tooltip shown near building entrances (HTML5-safe; no platform branches).
extends CanvasLayer

@onready var _panel: PanelContainer = $PanelContainer


func show() -> void:
	_panel.visible = true


func hide() -> void:
	_panel.visible = false

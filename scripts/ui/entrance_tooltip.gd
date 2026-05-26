## Tooltip shown near building entrances (HTML5-safe; no platform branches).
extends CanvasLayer

@onready var _panel: PanelContainer = $PanelContainer


@warning_ignore("native_method_override")
func show() -> void:
	_panel.visible = true


@warning_ignore("native_method_override")
func hide() -> void:
	_panel.visible = false

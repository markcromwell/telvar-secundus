extends CanvasLayer

## Transient district name overlay: 2.5s visible hold, then 0.5s fade-out.

@onready var district_label: Label = $DistrictLabel
@onready var hold_timer: Timer = $DistrictHoldTimer

var _fade_tween: Tween


func _ready() -> void:
	district_label.visible = false
	district_label.modulate = Color(1, 1, 1, 1)
	hold_timer.one_shot = true
	hold_timer.wait_time = 2.5
	hold_timer.timeout.connect(_on_hold_timeout)


func show_district_name(name: String) -> void:
	_cancel_fade_tween()
	district_label.modulate.a = 1.0
	district_label.text = name
	district_label.visible = true
	hold_timer.stop()
	hold_timer.start()


func _cancel_fade_tween() -> void:
	if _fade_tween != null and is_instance_valid(_fade_tween):
		_fade_tween.kill()
	_fade_tween = null


func _on_hold_timeout() -> void:
	_cancel_fade_tween()
	_fade_tween = create_tween()
	_fade_tween.tween_property(district_label, "modulate:a", 0.0, 0.5)
	_fade_tween.tween_callback(_after_fade_hide)


func _after_fade_hide() -> void:
	district_label.visible = false
	district_label.modulate.a = 1.0
	_fade_tween = null

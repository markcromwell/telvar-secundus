extends CanvasLayer

@onready var _mana_bar: ProgressBar = $Root/ManaBar


func set_max_mana(maximum: float) -> void:
	var previous := _mana_bar.value
	_mana_bar.max_value = maximum
	set_current_mana(previous)


func set_current_mana(current: float) -> void:
	_mana_bar.value = clampf(current, 0.0, _mana_bar.max_value)

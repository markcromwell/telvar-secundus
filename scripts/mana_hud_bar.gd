extends ProgressBar
class_name ManaHudBar

## Binds to a `ManaComponent` and keeps this bar in sync. Fill uses #4488ff.

const MANA_FILL_COLOR := Color("#4488ff")

@export var mana_component: NodePath


func _ready() -> void:
	min_value = 0.0
	show_percentage = false
	_apply_mana_fill_theme()

	var mc := get_node_or_null(mana_component)
	if mc is ManaComponent:
		var mana := mc as ManaComponent
		if not mana.mana_changed.is_connected(_on_mana_changed):
			mana.mana_changed.connect(_on_mana_changed)
		_on_mana_changed(mana.get_current_mana(), mana.get_max_mana())


func _apply_mana_fill_theme() -> void:
	var fill := StyleBoxFlat.new()
	fill.bg_color = MANA_FILL_COLOR
	add_theme_stylebox_override("fill", fill)


func _on_mana_changed(cur: int, maximum: int) -> void:
	max_value = float(maximum)
	value = float(cur)

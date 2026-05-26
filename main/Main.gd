extends Node2D

## Wires player mana signals to the HUD without modifying HUD.gd / Player.gd ownership boundaries.

@onready var _player = $Player
@onready var _hud = $HUD


func _ready() -> void:
	if is_instance_valid(_player) and SpellBook.has_method("set_caster"):
		SpellBook.set_caster(_player)
	if not is_instance_valid(_player) or not is_instance_valid(_hud):
		return
	_hud.set_max_mana(_player.max_mana)
	_hud.set_current_mana(_player.mana)
	if _player.has_signal("mana_changed"):
		_player.mana_changed.connect(_hud.set_current_mana)

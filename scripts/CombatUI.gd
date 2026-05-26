extends CanvasLayer
## Overlay: initiative recap, turn indicator, HP bars, and combat action buttons.

signal action_chosen(action: String)

@onready var _control_root: Control = $ControlRoot
@onready var _initiative_label: Label = $ControlRoot/MainColumn/InitiativeLabel
@onready var _turn_indicator: Label = $ControlRoot/MainColumn/TurnIndicator
@onready var _player_hp_bar: ProgressBar = $ControlRoot/MainColumn/PlayerHpBar
@onready var _enemy_hp_bar: ProgressBar = $ControlRoot/MainColumn/EnemyHpBar
@onready var _attack_btn: Button = $ControlRoot/MainColumn/ActionMenu/AttackButton
@onready var _cast_btn: Button = $ControlRoot/MainColumn/ActionMenu/CastSpellButton
@onready var _flee_btn: Button = $ControlRoot/MainColumn/ActionMenu/FleeButton

var _initiative_lines: Array[String] = []


func _ready() -> void:
	_control_root.visible = false
	_player_hp_bar.max_value = 100.0
	_player_hp_bar.value = 100.0
	_enemy_hp_bar.max_value = 100.0
	_enemy_hp_bar.value = 100.0

	CombatManager.initiative_rolled.connect(_on_initiative_rolled)
	CombatManager.combat_started.connect(_on_combat_started)
	CombatManager.combat_ended.connect(_on_combat_ended)
	CombatManager.turn_advanced.connect(_on_turn_advanced)

	_attack_btn.pressed.connect(func() -> void: action_chosen.emit("attack"))
	_cast_btn.pressed.connect(func() -> void: action_chosen.emit("cast_spell"))
	_flee_btn.pressed.connect(func() -> void: action_chosen.emit("flee"))


func set_player_hp(current: int, maximum: int) -> void:
	_player_hp_bar.max_value = maxf(float(maximum), 1.0)
	_player_hp_bar.value = clampf(float(current), 0.0, _player_hp_bar.max_value)


func set_enemy_hp(current: int, maximum: int) -> void:
	_enemy_hp_bar.max_value = maxf(float(maximum), 1.0)
	_enemy_hp_bar.value = clampf(float(current), 0.0, _enemy_hp_bar.max_value)


func _on_initiative_rolled(actor_id: String, speed: int, die: int, total: int) -> void:
	var display := _actor_display_name(actor_id)
	_initiative_lines.append("%s — speed %d + d6 %d = %d" % [display, speed, die, total])


func _on_combat_started() -> void:
	_control_root.visible = true
	var recap := "Initiative:\n" + "\n".join(_initiative_lines)
	_initiative_label.text = recap
	_initiative_lines.clear()
	_refresh_turn_indicator()


func _on_combat_ended() -> void:
	_control_root.visible = false
	_initiative_label.text = ""
	_turn_indicator.text = ""
	_initiative_lines.clear()


func _on_turn_advanced(_round_index: int, _actor_index: int, _state: CombatManager.CombatState) -> void:
	_refresh_turn_indicator()


func _refresh_turn_indicator() -> void:
	if not CombatManager.in_combat:
		return
	var r := CombatManager.current_round
	var who := "Telvar" if CombatManager.is_current_actor_player() else "Enemy"
	var aid := CombatManager.get_current_actor_id()
	if not CombatManager.is_current_actor_player() and aid != "":
		who = _actor_display_name(aid)
	_turn_indicator.text = "Round %d — %s's turn" % [r, who]


func _actor_display_name(actor_id: String) -> String:
	if actor_id == "telvar":
		return "Telvar"
	if actor_id.begins_with("enemy_"):
		return "Enemy %s" % actor_id.trim_prefix("enemy_")
	return actor_id

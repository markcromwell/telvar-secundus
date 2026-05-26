extends CanvasLayer

@onready var player_hp_bar: ProgressBar = %PlayerHPBar
@onready var enemy_hp_bar: ProgressBar = %EnemyHPBar
@onready var action_menu: VBoxContainer = %ActionMenuVBox

var _action_buttons: Array[Button] = []


func _ready() -> void:
	for child in action_menu.get_children():
		if child is Button:
			_action_buttons.append(child)

	CombatManager.combat_state_changed.connect(_on_combat_state_changed)
	_apply_menu_for_state(CombatManager.combat_state)
	_sync_hp_bars()


func _on_combat_state_changed(state: CombatManager.CombatState) -> void:
	_apply_menu_for_state(state)


func _apply_menu_for_state(state: CombatManager.CombatState) -> void:
	var enabled: bool = state == CombatManager.CombatState.PLAYER_TURN
	for b in _action_buttons:
		b.disabled = not enabled


func _sync_hp_bars() -> void:
	player_hp_bar.max_value = float(CombatManager.player_max_hp)
	player_hp_bar.value = float(CombatManager.player_hp)
	enemy_hp_bar.max_value = float(CombatManager.enemy_max_hp)
	enemy_hp_bar.value = float(CombatManager.enemy_hp)

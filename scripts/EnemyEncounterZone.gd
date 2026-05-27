extends Area2D
## Overlap zone: when Telvar (player CharacterBody2D) enters, starts combat via CombatManager.

@export var player_speed: int = 5
@export var enemy_speed: int = 3
@export var enemy_count: int = 1


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node2D) -> void:
	if CombatManager.in_combat:
		return
	if not body.is_in_group("player"):
		return
	var speeds: Array = []
	for _i in enemy_count:
		speeds.append(enemy_speed)
	CombatManager.start_combat(player_speed, speeds)

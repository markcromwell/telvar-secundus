extends Node2D
## Phase 2540: wires Sir Valins InteractionZone -> DialogueManager (sir_valins.tscn is merge-owned).


func _ready() -> void:
	var iz: Area2D = $SirValins/InteractionZone as Area2D
	iz.body_entered.connect(_on_sir_valins_interaction_zone_entered)


func _on_sir_valins_interaction_zone_entered(_body: Node2D) -> void:
	DialogueManager.start("sir_valins")

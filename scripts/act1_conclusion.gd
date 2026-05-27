extends Area2D

## Sequences Act 1 conclusion at the Emporium entrance: Sabatha dialogue, letter UI, quest/flag updates.
## One-shot per scene load; expects DialogueManager (optional `dialogue_finished` signal) and QuestManager autoloads.

var _triggered: bool = false
var _letter_ui: Control = null

func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(_body: Node2D) -> void:
	if _triggered:
		return
	_triggered = true
	_start_sabatha_dialogue()


func _start_sabatha_dialogue() -> void:
	var path := "res://assets/dialogue/sabatha.json"
	DialogueManager.show_dialogue("sabatha", path)
	if DialogueManager.has_signal("dialogue_finished"):
		DialogueManager.dialogue_finished.connect(_on_dialogue_finished, CONNECT_ONE_SHOT)
	else:
		call_deferred("_on_dialogue_finished")


func _on_dialogue_finished() -> void:
	_show_veneficturis_letter()


func _show_veneficturis_letter() -> void:
	if _letter_ui != null and is_instance_valid(_letter_ui):
		return
	var letter_scene: PackedScene = preload("res://scenes/ui/veneficturis_letter.tscn")
	_letter_ui = letter_scene.instantiate() as Control
	get_tree().root.add_child(_letter_ui)
	var dismiss: Button = _letter_ui.get_node("DismissButton") as Button
	dismiss.pressed.connect(_on_letter_dismissed, CONNECT_ONE_SHOT)


func _on_letter_dismissed() -> void:
	if _letter_ui != null and is_instance_valid(_letter_ui):
		_letter_ui.queue_free()
	_letter_ui = null
	QuestManager.complete_objective('merchants_delivery', 'return_to_emporium')
	QuestManager.start_quest('the_assessment')
	DialogueManager.set_flag('act1_complete', true)

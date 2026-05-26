extends Node2D

const INTRO_OVERLAY_SCENE := preload("res://scenes/ui/IntroOverlay.tscn")
const SABATHA_DIALOGUE_PATH := "res://assets/dialogue/sabatha.json"


func _ready() -> void:
	var player := $Player as CharacterBody2D
	player.can_move = false
	player.global_position = $SpawnPoint.global_position

	var overlay: Node = INTRO_OVERLAY_SCENE.instantiate()
	add_child(overlay)
	overlay.intro_finished.connect(_on_intro_finished)
	overlay.call_deferred("play_intro")

	var zone := $SabathaZone as Area2D
	zone.body_entered.connect(_on_sabatha_zone_body_entered)


func _on_intro_finished() -> void:
	var player := $Player as CharacterBody2D
	player.can_move = true
	DialogueManager.set_flag("tutorial_done", true)


func _on_sabatha_zone_body_entered(body: Node2D) -> void:
	if body != $Player:
		return
	var raw := FileAccess.get_file_as_string(SABATHA_DIALOGUE_PATH)
	var parsed: Variant = JSON.parse_string(raw)
	if typeof(parsed) != TYPE_ARRAY:
		push_error("Invalid sabatha dialogue JSON")
		return
	DialogueManager.show_dialogue("sabatha", parsed)

extends Area2D
## Myramar assessment: dialogue via DialogueManager; on success flag, lore, inventory, sprite, ceremony UI.
## Expects the player CharacterBody2D (or other body) to be in group "player" for range detection.

const NPC_ID := "myramar"
const DIALOGUE_PATH := "res://assets/dialogue/myramar.json"
const SUCCESS_FLAG := "myramar_assessment_complete"
const LORE_ON_SUCCESS := "wizard_ranks"
const BAND_ITEM_ID := "rutilus_band"
const BAND_SPRITE_RES := "res://assets/sprites/telvar_rutilus_band.png"

const _CEREMONY_SCENE := preload("res://scenes/ceremony_card.tscn")

@export var band_texture: Texture2D

@onready var sprite: Sprite2D = $Sprite2D

var _player_in_range := false
var _rewards_applied := false


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	DialogueManager.dialogue_closed.connect(_on_dialogue_closed)


func _unhandled_input(event: InputEvent) -> void:
	if not _player_in_range:
		return
	if event.is_action_pressed("ui_accept"):
		_start_dialogue()
		get_viewport().set_input_as_handled()


func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("player"):
		_player_in_range = true


func _on_body_exited(body: Node2D) -> void:
	if body.is_in_group("player"):
		_player_in_range = false


func _start_dialogue() -> void:
	if DialogueManager.is_dialogue_open():
		return
	DialogueManager.show_dialogue(NPC_ID, DIALOGUE_PATH)


func _on_dialogue_closed(npc_id: String) -> void:
	if npc_id != NPC_ID:
		return
	if not (DialogueManager.get_flag(SUCCESS_FLAG, false) == true):
		return
	if _rewards_applied:
		return
	_rewards_applied = true
	_apply_assessment_success()


func _apply_assessment_success() -> void:
	LoreManager.unlock(LORE_ON_SUCCESS)
	InventoryManager.add_item(BAND_ITEM_ID)
	_update_sprite_for_band()
	_spawn_ceremony_card()


func _resolve_band_texture() -> Texture2D:
	if band_texture != null:
		return band_texture
	if ResourceLoader.exists(BAND_SPRITE_RES):
		return load(BAND_SPRITE_RES) as Texture2D
	return null


func _update_sprite_for_band() -> void:
	var tex := _resolve_band_texture()
	if tex != null and is_instance_valid(sprite):
		sprite.texture = tex


func _spawn_ceremony_card() -> void:
	var card: Node = _CEREMONY_SCENE.instantiate()
	var layer := CanvasLayer.new()
	layer.layer = 75
	layer.add_child(card)
	get_tree().root.add_child(layer)

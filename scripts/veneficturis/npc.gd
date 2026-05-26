extends CharacterBody2D

## Base library NPC: interaction zone + dialogue hook for quest / inventory wiring.

@export var dialogue_id: String = "library_reader_default"
@export var portrait_path: String = ""

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var _zone: Area2D = $InteractionZone

var _player_inside := false
var _prompt: Label


func _ready() -> void:
	_prompt = _resolve_prompt()
	_configure_sprite_frames()
	_zone.body_entered.connect(_on_zone_body_entered)
	_zone.body_exited.connect(_on_zone_body_exited)


func _configure_sprite_frames() -> void:
	var tex: Texture2D = preload("res://assets/sprites/reader_sprite.png")
	var sf := SpriteFrames.new()
	if not sf.has_animation("idle"):
		sf.add_animation("idle")
	sf.set_animation_speed("idle", 1.0)
	sf.add_frame("idle", tex, 1.0)
	_sprite.sprite_frames = sf
	_sprite.play("idle")


func _process(_delta: float) -> void:
	if not _player_inside:
		return
	if Input.is_action_just_pressed("ui_accept"):
		_start_dialogue()


func _on_zone_body_entered(body: Node) -> void:
	if body.is_in_group("player"):
		_player_inside = true
		_set_prompt_visible(true)


func _on_zone_body_exited(body: Node) -> void:
	if body.is_in_group("player"):
		_player_inside = false
		_set_prompt_visible(false)


func _set_prompt_visible(on: bool) -> void:
	if _prompt:
		_prompt.visible = on
		_prompt.text = "Press E to talk" if on else ""


func _resolve_prompt() -> Label:
	var scene := get_tree().current_scene
	if scene:
		return scene.get_node_or_null("UI/PromptLabel") as Label
	return null


func _start_dialogue() -> void:
	var scene := get_tree().current_scene
	var dlg: Node = null
	if scene:
		dlg = scene.get_node_or_null("DialogueData")
	var text := _fallback_line()
	if dlg and dlg.has_method("get_line"):
		var line: String = str(dlg.call("get_line", dialogue_id))
		if line != "":
			text = line
	var popup: Node = null
	if scene:
		popup = scene.get_node_or_null("UI/LorePopup")
	if popup and popup.has_method("show_message"):
		popup.call("show_message", dialogue_id.capitalize(), text, portrait_path)
		return
	print("[Library NPC] ", dialogue_id, ": ", text)
	get_tree().call_group("dialogue_handlers", "on_dialogue_request", dialogue_id, text)


func _fallback_line() -> String:
	return "The Veneficturis stacks keep their own counsel. Telvar listens, and tries not to guess which silence matters most."

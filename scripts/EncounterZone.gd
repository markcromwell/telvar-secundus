extends Area2D

## Proximity radius for the well encounter: 3 tiles × 32 px (16×16 art at 2× scale).
const TRIGGER_RADIUS_PX := 96

@export var thug_dialogue: PackedStringArray = []

var _encounter_started: bool = false

signal encounter_started(player: CharacterBody2D)
signal thug_line_shown(line: String)


func _ready() -> void:
	monitoring = true
	body_entered.connect(_on_body_entered)
	_ensure_trigger_shape()


func _ensure_trigger_shape() -> void:
	for child in get_children():
		if child is CollisionShape2D:
			var cs := child as CollisionShape2D
			var circle := cs.shape as CircleShape2D
			if circle != null:
				circle.radius = TRIGGER_RADIUS_PX
				return
	var shape_node := CollisionShape2D.new()
	var circle_shape := CircleShape2D.new()
	circle_shape.radius = TRIGGER_RADIUS_PX
	shape_node.shape = circle_shape
	add_child(shape_node)


func _on_body_entered(body: Node2D) -> void:
	if _encounter_started:
		return
	if not _body_is_player(body):
		return
	var player := body as CharacterBody2D
	_encounter_started = true
	player.set("can_move", false)
	encounter_started.emit(player)
	for line in thug_dialogue:
		thug_line_shown.emit(line)


func _body_is_player(body: Node) -> bool:
	if not (body is CharacterBody2D):
		return false
	if body.is_in_group("player"):
		return true
	return String(body.name) == "Player"

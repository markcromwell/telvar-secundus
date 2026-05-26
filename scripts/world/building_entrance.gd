## Area trigger for building entrances: adjacency tooltip and Enter/E (ui_accept).
extends Area2D

signal entered(building_name: String, entrance_id: String)

@export var building_name: String = ""
@export var entrance_id: String = ""

var player_in_range: bool = false

var _players_inside: int = 0
@onready var _tooltip: CanvasLayer = $EntranceTooltip


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)


func _unhandled_input(event: InputEvent) -> void:
	if not player_in_range:
		return
	if event.is_action_pressed("ui_accept"):
		entered.emit(building_name, entrance_id)
		_on_enter()
		get_viewport().set_input_as_handled()


func _on_body_entered(body: Node) -> void:
	if not _is_player_body(body):
		return
	_players_inside += 1
	if _players_inside == 1:
		player_in_range = true
		_tooltip.show()


func _on_body_exited(body: Node) -> void:
	if not _is_player_body(body):
		return
	_players_inside = max(0, _players_inside - 1)
	if _players_inside == 0:
		player_in_range = false
		_tooltip.hide()


func _is_player_body(body: Node) -> bool:
	return body.is_in_group("player")


func _on_enter() -> void:
	print(building_name)

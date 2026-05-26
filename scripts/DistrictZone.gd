extends Area2D

## Area that briefly shows a HUD label when the player enters this district.
@export var district_name: String = ""
@export var hud_label: NodePath

var _hide_timer: Timer


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	_hide_timer = Timer.new()
	_hide_timer.one_shot = true
	_hide_timer.wait_time = 3.0
	add_child(_hide_timer)
	_hide_timer.timeout.connect(_on_hide_timer_timeout)


func _on_body_entered(_body: Node2D) -> void:
	var node := get_node_or_null(hud_label)
	if node is CanvasItem:
		(node as CanvasItem).visible = true
	_hide_timer.stop()
	_hide_timer.start()


func _on_hide_timer_timeout() -> void:
	var node := get_node_or_null(hud_label)
	if node is CanvasItem:
		(node as CanvasItem).visible = false

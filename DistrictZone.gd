extends Area2D
class_name DistrictZone

signal district_entered(name: String)

@export var district_name: String = ""

func _ready() -> void:
	monitorable = false
	monitoring = true
	body_entered.connect(_on_body_entered)

func _on_body_entered(_body: Node2D) -> void:
	district_entered.emit(district_name)

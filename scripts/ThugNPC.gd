extends CharacterBody2D

@export var speed: float = 64.0

var _fleeing: bool = false
var _flee_origin: Vector2 = Vector2.ZERO


func start_flee(origin: Vector2) -> void:
    _fleeing = true
    var p := get_parent()
    if p is Node2D:
        _flee_origin = (p as Node2D).global_transform.affine_inverse() * origin
    else:
        _flee_origin = origin


func _physics_process(_delta: float) -> void:
    if not _fleeing:
        return
    var away: Vector2 = position - _flee_origin
    if away.length_squared() < 0.0001:
        return
    velocity = away.normalized() * speed
    move_and_slide()

extends GutTest

const PLAYER_SCRIPT := preload("res://scripts/Player.gd")
const PLAYER_SCENE := preload("res://scenes/Player.tscn")

var _player: CharacterBody2D
var _input_sender


func before_each() -> void:
	_player = PLAYER_SCRIPT.new() as CharacterBody2D
	add_child_autofree(_player)
	_input_sender = InputSender.new(Input)
	_input_sender.set_auto_flush_input(true)


func after_each() -> void:
	_input_sender.release_all()


func test_speed_default() -> void:
	assert_eq(_player.get("speed"), 128.0)


func test_can_move_default() -> void:
	assert_true(_player.get("can_move"))


func test_can_move_false_zeroes_velocity() -> void:
	_input_sender.action_down("ui_right")
	_player.can_move = false
	_player._physics_process(0.016)
	assert_eq(_player.velocity, Vector2.ZERO)


func test_cardinal_directions_velocity_matches_speed() -> void:
	var cases := [
		["ui_left", Vector2.LEFT],
		["ui_right", Vector2.RIGHT],
		["ui_up", Vector2.UP],
		["ui_down", Vector2.DOWN],
	]
	for pair in cases:
		var action: String = pair[0]
		var unit: Vector2 = pair[1]
		_input_sender.release_all()
		_input_sender.action_down(action)
		_player._physics_process(0.016)
		var expected := unit * _player.speed
		assert_almost_eq(_player.velocity, expected, Vector2(0.0001, 0.0001), str("velocity for ", action))


func test_diagonal_normalised() -> void:
	_input_sender.action_down("ui_right")
	_input_sender.action_down("ui_up")
	_player._physics_process(0.016)
	assert_almost_eq(_player.velocity.length(), _player.speed, 0.01)


func test_camera_has_position_smoothing_speed() -> void:
	var root := PLAYER_SCENE.instantiate()
	add_child_autofree(root)
	var cam := root.get_node_or_null("Camera2D") as Camera2D
	assert_not_null(cam, "Player scene should include Camera2D child")
	assert_eq(cam.position_smoothing_speed, 0.1)

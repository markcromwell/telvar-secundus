extends Node
class_name DialogueManager

## Autoload-friendly coordinator for dialogue flow and UI click SFX.
## Uses a single **AudioStreamPlayer** on the **SFX** bus so rapid clicks do not stack.

const BUS_SFX := "SFX"
const _DEFAULT_CLICK := "res://assets/audio/ui_click.wav"

static var singleton: DialogueManager

@export var ui_click_stream: AudioStream

var _ui_click_player: AudioStreamPlayer


func _enter_tree() -> void:
	singleton = self


func _exit_tree() -> void:
	if singleton == self:
		singleton = null


func _ready() -> void:
	_ui_click_player = AudioStreamPlayer.new()
	_ui_click_player.bus = BUS_SFX
	_ui_click_player.max_polyphony = 1
	add_child(_ui_click_player)
	if ui_click_stream == null:
		ui_click_stream = load(_DEFAULT_CLICK) as AudioStream


## Short UI / dialogue advance click. Restarts playback if already playing
## so rapid interaction does not layer into clipping distortion.
func play_ui_click() -> void:
	var stream := ui_click_stream
	if stream == null:
		return
	_ui_click_player.stop()
	_ui_click_player.stream = stream
	_ui_click_player.play()


## Recursively connect **BaseButton.pressed** under `root` for menu / HUD clicks.
func wire_buttons_under(root: Node) -> void:
	if root == null:
		return
	_wire_buttons_recursive(root)


func _wire_buttons_recursive(node: Node) -> void:
	if node is BaseButton:
		var b := node as BaseButton
		if not b.pressed.is_connected(_on_wired_button_pressed):
			b.pressed.connect(_on_wired_button_pressed)
	for child in node.get_children():
		_wire_buttons_recursive(child)


func _on_wired_button_pressed() -> void:
	play_ui_click()

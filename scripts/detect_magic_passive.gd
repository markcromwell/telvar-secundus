extends Node
## Passive Detect Magic: when the player knows the spell, nearby nodes in group
## `magical` receive a gold shimmer for exactly HIGHLIGHT_DURATION_SEC, then
## the effect cannot re-trigger until COOLDOWN_AFTER_HIGHLIGHT_SEC has passed
## after the highlight ends.
##
## Wire-up: add the player root to group `player`. Mark magical props with
## `add_to_group("magical")` (any CanvasItem / Node2D works).

const HIGHLIGHT_DURATION_SEC := 5.0
const COOLDOWN_AFTER_HIGHLIGHT_SEC := 3.0
const DETECTION_RADIUS_PX := 256.0
const SHIMMER_SPEED := 8.0

var _highlight_remaining := 0.0
var _cooldown_remaining := 0.0
var _shimmer_phase := 0.0
var _highlighted: Array[CanvasItem] = []
var _original_modulates: Array[Color] = []


func _process(delta: float) -> void:
	if _highlight_remaining > 0.0:
		_highlight_remaining -= delta
		_shimmer_phase += delta
		_apply_shimmer_modulates()
		if _highlight_remaining <= 0.0:
			_clear_highlights()
			_cooldown_remaining = COOLDOWN_AFTER_HIGHLIGHT_SEC
		return

	if _cooldown_remaining > 0.0:
		_cooldown_remaining -= delta
		return

	if not _player_knows_detect_magic():
		return

	var player := _find_player()
	if player == null:
		return

	var in_range := _magical_canvas_items_in_range(player.global_position)
	if in_range.is_empty():
		return

	_begin_highlight(in_range)
	_highlight_remaining = HIGHLIGHT_DURATION_SEC


func _player_knows_detect_magic() -> bool:
	for s in SpellBook.get_known_spells():
		if s.spell_id == "detect_magic":
			return true
	return false


func _find_player() -> Node2D:
	var tree := get_tree()
	if tree == null:
		return null
	var nodes := tree.get_nodes_in_group("player")
	if nodes.is_empty():
		return null
	var n: Node = nodes[0]
	return n as Node2D


func _canvas_item_global_position(ci: CanvasItem) -> Vector2:
	if ci is Node2D:
		return (ci as Node2D).global_position
	if ci is Control:
		return (ci as Control).global_position
	return Vector2.ZERO


func _magical_canvas_items_in_range(origin: Vector2) -> Array[CanvasItem]:
	var out: Array[CanvasItem] = []
	var tree := get_tree()
	if tree == null:
		return out
	for node in tree.get_nodes_in_group("magical"):
		if not (node is CanvasItem):
			continue
		var ci := node as CanvasItem
		if not ci.is_inside_tree():
			continue
		var pos := _canvas_item_global_position(ci)
		if pos.distance_to(origin) > DETECTION_RADIUS_PX:
			continue
		out.append(ci)
	return out


func _begin_highlight(items: Array[CanvasItem]) -> void:
	_highlighted.clear()
	_original_modulates.clear()
	for ci in items:
		_highlighted.append(ci)
		_original_modulates.append(ci.modulate)


func _apply_shimmer_modulates() -> void:
	var pulse := (sin(_shimmer_phase * SHIMMER_SPEED) * 0.5 + 0.5)
	var gold_bright := Color(1.0, 0.95, 0.65)
	var gold_deep := Color(1.0, 0.78, 0.35)
	var shimmer := gold_deep.lerp(gold_bright, pulse)
	for i in range(_highlighted.size()):
		_highlighted[i].modulate = _original_modulates[i] * shimmer


func _clear_highlights() -> void:
	for i in range(_highlighted.size()):
		if is_instance_valid(_highlighted[i]):
			_highlighted[i].modulate = _original_modulates[i]
	_highlighted.clear()
	_original_modulates.clear()
	_shimmer_phase = 0.0

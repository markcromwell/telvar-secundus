extends Node2D
## Phase 2691 — Aelyn's quarters: cleared by apprentice runners — no kit, no furniture, only the floor note.
## Phase 2692 — Floor note completes quest objective read_floor_note; entering completes enter_aelyns_room.

const QUEST_ID := "where_is_aelyn"

@onready var _floor: TileMapLayer = $Floor
@onready var _floor_note: Area2D = $FloorNote
@onready var _note_label: Label = $FloorNote/NoteText


func _ready() -> void:
	_paint_room()
	_note_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_floor_note.input_event.connect(_on_floor_note_input_event)
	_try_complete_enter_objective()


func _try_complete_enter_objective() -> void:
	if not QuestManager.quests.has(QUEST_ID):
		return
	var objs: Dictionary = QuestManager.quests[QUEST_ID]["objectives"]
	if objs.has("enter_aelyns_room") and not objs["enter_aelyns_room"]:
		QuestManager.complete_objective(QUEST_ID, "enter_aelyns_room")


func _on_floor_note_input_event(_viewport: Node, event: InputEvent, _shape_idx: int) -> void:
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
			_read_floor_note()


func _read_floor_note() -> void:
	if not QuestManager.quests.has(QUEST_ID):
		return
	var objs: Dictionary = QuestManager.quests[QUEST_ID]["objectives"]
	if not objs.has("read_floor_note") or objs["read_floor_note"]:
		return
	QuestManager.complete_objective(QUEST_ID, "read_floor_note")
	_floor_note.input_pickable = false
	_floor_note.visible = false


func _paint_room() -> void:
	var width := 12
	var height := 10
	var door_x := width // 2
	for y in range(height):
		for x in range(width):
			var coords := Vector2i(x, y)
			var is_wall := x == 0 or x == width - 1 or y == 0 or y == height - 1
			if y == height - 1 and x == door_x:
				is_wall = false
			var atlas := Vector2i(1, 0) if is_wall else Vector2i(0, 0)
			_floor.set_cell(coords, 0, atlas)

extends Control
## S-key spell panel: lists learnable and known spells with mana costs (SpellBook).


@onready var _mana_label: Label = $Center/Frame/VBox/ManaLabel
@onready var _known_list: ItemList = $Center/Frame/VBox/KnownList
@onready var _learnable_list: ItemList = $Center/Frame/VBox/LearnableList


func _ready() -> void:
	visible = false
	visibility_changed.connect(_on_visibility_changed)


func toggle_visible() -> void:
	visible = not visible


func _on_visibility_changed() -> void:
	if visible:
		_refresh_lists()


func _refresh_lists() -> void:
	_mana_label.text = "Mana: %d / %d  |  Copper: %d" % [
		SpellBook.mana_current,
		SpellBook.mana_max,
		SpellBook.copper,
	]
	_known_list.clear()
	for line in _known_spell_lines():
		_known_list.add_item(line)
	_learnable_list.clear()
	for line in SpellBook.get_learnable_display_lines():
		_learnable_list.add_item(line)


func _known_spell_lines() -> PackedStringArray:
	var lines: PackedStringArray = []
	for spell_id in SpellBook.known_spells.keys():
		var s: Spell = SpellBook.known_spells[spell_id] as Spell
		if s:
			lines.append("%s — %d MP" % [s.spell_name, s.mana_cost])
	return lines


func get_known_spell_lines() -> PackedStringArray:
	return _known_spell_lines()

extends Control

@onready var spell_list = $Panel/VBoxContainer/SpellList

func _ready() -> void:
	hide()
	_update_spell_list()

func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and event.keycode == KEY_S:
		visible = !visible
		if visible:
			_update_spell_list()

func _update_spell_list() -> void:
	if not spell_list:
		return
	for child in spell_list.get_children():
		child.queue_free()
		
	# SpellBook is an autoload
	var spells = SpellBook.get_known_spells()
	for spell in spells:
		var label = Label.new()
		label.text = "%s - Cost: %d MP" % [spell.name, spell.mana_cost]
		spell_list.add_child(label)

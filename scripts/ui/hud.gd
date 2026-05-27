extends CanvasLayer

@onready var mana_bar = $VBoxContainer/ManaBar
@onready var spell_panel = $SpellPanel
@onready var spell_slots = $SpellPanel/VBoxContainer/SpellSlots

signal spell_cast(spell: Spell)

var mana_component: ManaComponent
var current_mana: int = 0

func _ready() -> void:
	spell_panel.visible = false
	
	# Try to find a ManaComponent if not set
	if not mana_component:
		# Just a fallback, ideally it's injected
		var group = get_tree().get_nodes_in_group("player")
		if group.size() > 0:
			var player = group[0]
			for child in player.get_children():
				if child is ManaComponent:
					mana_component = child
					break

	if mana_component:
		mana_component.mana_changed.connect(_on_mana_changed)
		mana_bar.max_value = mana_component.max_mana
		mana_bar.value = mana_component.current_mana
		current_mana = mana_component.current_mana

	for i in range(spell_slots.get_child_count()):
		var slot_btn = spell_slots.get_child(i)
		if slot_btn is Button:
			slot_btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
			slot_btn.pressed.connect(_on_spell_slot_pressed.bind(i))

	_populate_spell_panel()

func setup(p_mana_component: ManaComponent) -> void:
	mana_component = p_mana_component
	mana_component.mana_changed.connect(_on_mana_changed)
	mana_bar.max_value = mana_component.max_mana
	mana_bar.value = mana_component.current_mana
	current_mana = mana_component.current_mana
	_update_spell_buttons()

func _on_mana_changed(current: int, maximum: int) -> void:
	mana_bar.value = current
	mana_bar.max_value = maximum
	current_mana = current
	if spell_panel.visible:
		_update_spell_buttons()

func _input(event: InputEvent) -> void:
	if event.is_action_pressed(&"toggle_spell_panel", false):
		_toggle_spell_panel()
	elif event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE and spell_panel.visible:
			spell_panel.visible = false

func _toggle_spell_panel() -> void:
	spell_panel.visible = not spell_panel.visible
	if spell_panel.visible:
		_populate_spell_panel()

func _populate_spell_panel() -> void:
	var spell_book = get_node_or_null("/root/SpellBook")
	for i in range(mini(3, spell_slots.get_child_count())):
		var btn = spell_slots.get_child(i) as Button
		if btn == null:
			continue
		if btn.has_meta("spell"):
			btn.remove_meta("spell")
		btn.text = "—"
		btn.disabled = true
		btn.modulate = Color(0.55, 0.55, 0.55, 1.0)
		if spell_book == null:
			continue
		if i >= spell_book.known_spells.size():
			continue
		var spell: Spell = spell_book.known_spells[i]
		if spell == null:
			continue
		btn.text = "%s (%d MP)" % [spell.name, spell.mana_cost]
		btn.set_meta("spell", spell)

	_update_spell_buttons()

func _update_spell_buttons() -> void:
	for i in range(mini(3, spell_slots.get_child_count())):
		var btn = spell_slots.get_child(i) as Button
		if btn == null:
			continue
		if not btn.has_meta("spell"):
			btn.disabled = true
			btn.modulate = Color(0.55, 0.55, 0.55, 1.0)
			continue
		var spell: Spell = btn.get_meta("spell") as Spell
		if spell == null:
			btn.disabled = true
			btn.modulate = Color(0.55, 0.55, 0.55, 1.0)
			continue
		var can_cast := current_mana >= spell.mana_cost
		btn.disabled = not can_cast
		btn.modulate = Color(0.55, 0.55, 0.55, 1.0) if not can_cast else Color.WHITE

func _on_spell_slot_pressed(slot_index: int) -> void:
	var btn = spell_slots.get_child(slot_index) as Button
	if btn == null or not btn.has_meta("spell"):
		return
	var spell: Spell = btn.get_meta("spell") as Spell
	if spell == null:
		return
	if mana_component and mana_component.use_mana(spell.mana_cost):
		spell_cast.emit(spell)
		spell_panel.visible = false

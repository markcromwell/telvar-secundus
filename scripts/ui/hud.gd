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
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_S:
			_toggle_spell_panel()
		elif event.keycode == KEY_ESCAPE and spell_panel.visible:
			spell_panel.visible = false

func _toggle_spell_panel() -> void:
	spell_panel.visible = not spell_panel.visible
	if spell_panel.visible:
		_populate_spell_panel()
		_update_spell_buttons()

func _populate_spell_panel() -> void:
	# Clear existing
	for child in spell_slots.get_children():
		child.queue_free()
		
	var spell_book = get_node_or_null("/root/SpellBook")
	if not spell_book:
		return
		
	for spell in spell_book.known_spells:
		if spell == null:
			continue
			
		var btn = Button.new()
		btn.text = "%s (%d MP)" % [spell.name, spell.mana_cost]
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		btn.pressed.connect(func(): _on_spell_button_pressed(spell))
		btn.set_meta("spell", spell)
		spell_slots.add_child(btn)

func _update_spell_buttons() -> void:
	for btn in spell_slots.get_children():
		if btn is Button:
			var spell: Spell = btn.get_meta("spell")
			if spell:
				var can_cast = current_mana >= spell.mana_cost
				btn.disabled = not can_cast

func _on_spell_button_pressed(spell: Spell) -> void:
	if current_mana >= spell.mana_cost:
		if mana_component and mana_component.use_mana(spell.mana_cost):
			spell_cast.emit(spell)
			spell_panel.visible = false

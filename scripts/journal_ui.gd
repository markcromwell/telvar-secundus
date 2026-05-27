extends CanvasLayer

@onready var active_list = $PanelContainer/TabContainer/Active/QuestList
@onready var done_list = $PanelContainer/TabContainer/Done/QuestList
@onready var lore_list = $PanelContainer/TabContainer/Lore/LoreList

var lore_db: Array = []

func _ready() -> void:
	visible = false
	QuestManager.quest_updated.connect(_on_quest_updated)
	QuestManager.objective_completed.connect(_on_objective_completed)
	LoreManager.lore_unlocked.connect(_on_lore_unlocked)
	_load_lore_db()
	refresh_all()

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("open_journal"):
		visible = not visible
		if visible:
			refresh_all()

func _on_quest_updated(_quest_id: String) -> void:
	if visible:
		refresh_quests()

func _on_objective_completed(_quest_id: String, _obj_id: String) -> void:
	if visible:
		refresh_quests()

func _on_lore_unlocked(_entry_id: String) -> void:
	if visible:
		refresh_lore()
	show_toast("Lore Unlocked!")

func show_toast(msg: String) -> void:
	if has_node("ToastLabel"):
		var toast = get_node("ToastLabel") as Label
		toast.text = msg
		toast.visible = true
		var timer = get_tree().create_timer(3.0)
		timer.timeout.connect(func(): toast.visible = false)

func _load_lore_db() -> void:
	var path := "res://assets/lore/lore_entries.json"
	if not FileAccess.file_exists(path):
		return
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return
	var txt := f.get_as_text()
	var data = JSON.parse_string(txt)
	if typeof(data) == TYPE_ARRAY:
		lore_db = data

func refresh_all() -> void:
	refresh_quests()
	refresh_lore()

func refresh_quests() -> void:
	# Clear existing
	for child in active_list.get_children():
		child.queue_free()
	for child in done_list.get_children():
		child.queue_free()
	
	for q_id in QuestManager.quests:
		var q: Dictionary = QuestManager.quests[q_id]
		var status = str(q.get("status", ""))
		if status == "active":
			_build_quest_ui(q_id, q, active_list)
		elif status == "completed" or status == "done":
			_build_quest_ui(q_id, q, done_list)

func _build_quest_ui(q_id: String, q: Dictionary, parent: Control) -> void:
	var vbox = VBoxContainer.new()
	parent.add_child(vbox)
	
	var header_hbox = HBoxContainer.new()
	vbox.add_child(header_hbox)
	
	var toggle_btn = Button.new()
	toggle_btn.text = "v"
	header_hbox.add_child(toggle_btn)
	
	var title_lbl = Label.new()
	title_lbl.text = str(q.get("title", q_id))
	header_hbox.add_child(title_lbl)
	
	var progress_lbl = Label.new()
	var objs: Array = q.get("objectives", [])
	var done_count = 0
	for o in objs:
		if typeof(o) == TYPE_DICTIONARY and o.get("done", false):
			done_count += 1
	progress_lbl.text = "(%d/%d)" % [done_count, objs.size()]
	header_hbox.add_child(progress_lbl)
	
	var obj_vbox = VBoxContainer.new()
	vbox.add_child(obj_vbox)
	
	toggle_btn.pressed.connect(func():
		obj_vbox.visible = not obj_vbox.visible
		toggle_btn.text = "v" if obj_vbox.visible else ">"
	)
	
	for o in objs:
		if typeof(o) != TYPE_DICTIONARY:
			continue
		var o_dict: Dictionary = o
		var o_hbox = HBoxContainer.new()
		obj_vbox.add_child(o_hbox)
		
		var chk = CheckBox.new()
		chk.button_pressed = o_dict.get("done", false)
		chk.disabled = true
		o_hbox.add_child(chk)
		
		var rtl = RichTextLabel.new()
		rtl.bbcode_enabled = true
		var desc = str(o_dict.get("desc", ""))
		if o_dict.get("done", false):
			rtl.text = "[s]%s[/s]" % desc
		else:
			rtl.text = desc
		rtl.fit_content = true
		rtl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		rtl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		o_hbox.add_child(rtl)

func refresh_lore() -> void:
	for child in lore_list.get_children():
		child.queue_free()
	
	for entry in lore_db:
		if typeof(entry) == TYPE_DICTIONARY:
			var e: Dictionary = entry
			var id = str(e.get("id", ""))
			if LoreManager.is_unlocked(id):
				var vbox = VBoxContainer.new()
				lore_list.add_child(vbox)
				
				var title_lbl = Label.new()
				title_lbl.text = str(e.get("title", ""))
				title_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
				vbox.add_child(title_lbl)
				
				var txt_lbl = Label.new()
				txt_lbl.text = str(e.get("text", ""))
				txt_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
				vbox.add_child(txt_lbl)

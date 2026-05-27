extends Control

const LORE_ENTRIES_PATH := "res://assets/lore/lore_entries.json"

@onready var entry_list: VBoxContainer = %EntryList

var _entries_by_id: Dictionary = {}


func _ready() -> void:
	_load_lore_entries()
	LoreManager.lore_unlocked.connect(refresh)
	refresh()


func _load_lore_entries() -> void:
	_entries_by_id.clear()
	if not FileAccess.file_exists(LORE_ENTRIES_PATH):
		push_warning("LoreTab: missing lore entries at %s" % LORE_ENTRIES_PATH)
		return
	var raw := FileAccess.get_file_as_string(LORE_ENTRIES_PATH)
	var parsed: Variant = JSON.parse_string(raw)
	if typeof(parsed) != TYPE_ARRAY:
		push_warning("LoreTab: lore_entries.json is not a JSON array")
		return
	for item in parsed:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var d: Dictionary = item
		if not d.has("id"):
			continue
		var eid := str(d["id"])
		_entries_by_id[eid] = {
			"title": str(d.get("title", eid)),
			"text": str(d.get("text", "")),
		}


func refresh(_unused_entry_id: String = "") -> void:
	for i in range(entry_list.get_child_count() - 1, -1, -1):
		entry_list.get_child(i).free()

	for entry_id in LoreManager.unlocked:
		var meta: Variant = _entries_by_id.get(entry_id, null)
		var title: String = entry_id
		var body: String = ""
		if meta is Dictionary:
			title = str(meta.get("title", entry_id))
			body = str(meta.get("text", ""))

		var row := VBoxContainer.new()
		row.size_flags_horizontal = Control.SIZE_EXPAND_FILL

		var title_rtl := RichTextLabel.new()
		title_rtl.bbcode_enabled = true
		title_rtl.fit_content_height = true
		title_rtl.scroll_active = false
		title_rtl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		title_rtl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		title_rtl.clear()
		title_rtl.push_bold()
		title_rtl.add_text(title)
		title_rtl.pop()

		var desc_l := Label.new()
		desc_l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		desc_l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		desc_l.text = body

		row.add_child(title_rtl)
		row.add_child(desc_l)
		entry_list.add_child(row)

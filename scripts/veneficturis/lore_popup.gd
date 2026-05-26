extends AcceptDialog

## Lore / short dialogue popup for library shelves and reading NPCs.

func _ready() -> void:
	unresizable = true
	ok_button_text = "Close"


func show_message(title: String, body: String, _portrait_path: String = "") -> void:
	title = title.strip_edges()
	body = body.strip_edges()
	dialog_text = "%s\n\n%s" % [title, body]
	popup_centered_ratio(0.55)

extends Resource
class_name Item

## Stable id used for saves and story scripting (e.g. wizard_band_red).
@export var id: String = ""

## Shown in inventory and obtain UI.
@export var display_name: String = ""

## Short flavor for cards and tooltips.
@export var description: String = ""

## Filter / rules tags (e.g. magical, quest).
@export var tags: PackedStringArray = []


func has_tag(tag: String) -> bool:
	return tag in tags

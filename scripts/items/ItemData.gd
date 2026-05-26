extends Resource
class_name ItemData

@export var id: StringName
@export var display_name: String = ""
@export_multiline var description: String = ""
@export var item_type: StringName = &"misc"
@export var stackable: bool = false
@export var consumable: bool = false

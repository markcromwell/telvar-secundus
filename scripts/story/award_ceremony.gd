extends RefCounted
class_name AwardCeremony

## Resource path for the Rutilus ceremony band (must match resources/items/).
const WIZARD_BAND_RED_PATH := "res://resources/items/wizard_band_red.tres"


## Run at the end of the Veneficturis award ceremony: grants `wizard_band_red`,
## updates the player wrist overlay, and shows the obtain card.
static func complete_award(player: Node, inventory: Inventory, obtain_card: Node) -> void:
	var template := load(WIZARD_BAND_RED_PATH)
	if template == null:
		push_error("AwardCeremony: failed to load " + WIZARD_BAND_RED_PATH)
		return
	if not (template is Item):
		push_error("AwardCeremony: resource is not an Item")
		return
	var band: Item = (template as Item).duplicate() as Item
	if band == null:
		push_error("AwardCeremony: duplicate() did not yield Item")
		return

	inventory.add_item(band)

	if player != null and player.has_method(&"set_wrist_band_visible"):
		player.call(&"set_wrist_band_visible", true)

	if obtain_card != null and obtain_card.has_method(&"show_for_item"):
		obtain_card.call(&"show_for_item", band)

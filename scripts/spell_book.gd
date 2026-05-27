extends Node

var known_spells: Array[Spell] = []

func _ready() -> void:
	# Initialize starter spells
	var detect_magic = Spell.new("detect_magic", "Detect Magic", 0, 0, "passive, 3s cooldown, gold shimmer on magical objects")
	var light_sphere = Spell.new("light_sphere", "Light Sphere", 5, 0, "5-tile 30s light")
	var banishment = Spell.new("banishment", "Banishment", 20, 15, "push+stun, 15 dmg vs shades")
	
	known_spells.append(detect_magic)
	known_spells.append(light_sphere)
	known_spells.append(banishment)

func get_known_spells() -> Array[Spell]:
	return known_spells

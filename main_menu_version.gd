# Tiny attach script for the build version label.
extends Label

func _ready() -> void:
	if has_node("/root/BuildVersion"):
		text = "v %s" % BuildVersion.version
	else:
		text = "v dev"

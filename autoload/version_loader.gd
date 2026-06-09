# res://autoload/version_loader.gd
# 2026-06-08: small autoload that exposes a build version string for the
# main menu (and any UI that wants to display it). The actual value is
# written into res://build_version.txt by the GitHub Actions deploy
# workflow before the export runs.
extends Node

const VERSION_FILE := "res://build_version.txt"
const FALLBACK := "dev"

var version: String = FALLBACK


func _ready() -> void:
	var f := FileAccess.open(VERSION_FILE, FileAccess.READ)
	if f != null:
		version = f.get_as_text().strip_edges()
		f.close()

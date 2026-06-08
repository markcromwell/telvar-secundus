extends Control
## Main menu: hosts the Settings, Load, and Credits screens as CanvasLayer
## overlays. Only one overlay is open at a time; every open is guarded against
## double instantiation so rapid presses cannot stack duplicate layers or orphan
## state. Each overlay reports its Back action through a "back" signal, and the
## shared _on_overlay_back handler dismisses the overlay and returns focus to the
## menu without ever freeing the menu itself. Audio slider state persists across
## the round-trip via the Menu autoload, so reopening Settings shows the values
## last set (including those changed during gameplay).

## Overlay scenes, loaded on demand by path. Settings and Load are authored by
## sibling phases; loading by path (guarded with ResourceLoader.exists) means a
## not-yet-merged scene degrades to a no-op warning instead of a parse/crash.
const _CREDITS_SCENE_PATH := "res://Credits.tscn"
const _SETTINGS_SCENE_PATH := "res://SettingsMenu.tscn"
const _LOAD_SCENE_PATH := "res://LoadScreen.tscn"

## Back-signal names an overlay may expose. Credits/Settings/Load were authored by
## different phases, so we connect to whichever one this overlay declares; that is
## what lets all three share a single consistent back path.
const _BACK_SIGNALS := ["back_requested", "back_pressed"]

## CanvasLayer index for overlays, so they render above the menu.
const _OVERLAY_LAYER := 100

@onready var _settings_button: Button = $CenterContainer/VBoxContainer/SettingsButton
@onready var _load_button: Button = $CenterContainer/VBoxContainer/LoadButton
@onready var _credits_button: Button = $CenterContainer/VBoxContainer/CreditsButton

## The single active overlay CanvasLayer, or null when the menu has focus. This is
## the guard that prevents a second press from creating a duplicate layer.
var _active_overlay: CanvasLayer = null


func _ready() -> void:
	_settings_button.pressed.connect(_on_settings_pressed)
	_load_button.pressed.connect(_on_load_pressed)
	_credits_button.pressed.connect(_on_credits_pressed)


func _on_settings_pressed() -> void:
	_open_overlay(_SETTINGS_SCENE_PATH, _settings_button)


func _on_load_pressed() -> void:
	_open_overlay(_LOAD_SCENE_PATH, _load_button)


func _on_credits_pressed() -> void:
	_open_overlay(_CREDITS_SCENE_PATH, _credits_button)


## Instantiate `scene_path` inside a fresh CanvasLayer overlay and wire its back
## signal to the shared close handler. Guarded twice so navigation can never crash
## or orphan state: it refuses to open while another overlay is active, and it
## skips (with a warning) when the scene resource is missing. `return_focus` is the
## menu button focus returns to once the overlay closes.
func _open_overlay(scene_path: String, return_focus: Control) -> void:
	if _active_overlay != null:
		return
	if not ResourceLoader.exists(scene_path):
		push_warning("MainMenu: overlay scene not found: %s" % scene_path)
		return
	var packed: PackedScene = load(scene_path)
	if packed == null:
		push_warning("MainMenu: failed to load overlay scene: %s" % scene_path)
		return
	var screen: Node = packed.instantiate()
	var layer := CanvasLayer.new()
	layer.layer = _OVERLAY_LAYER
	layer.add_child(screen)
	add_child(layer)
	_active_overlay = layer
	_connect_back(screen, return_focus)


## Connect the overlay's back signal to the shared close handler. We accept any of
## _BACK_SIGNALS so screens authored by different phases interoperate; the
## connection is one-shot since each open instantiates a fresh screen.
func _connect_back(screen: Node, return_focus: Control) -> void:
	for signal_name in _BACK_SIGNALS:
		if screen.has_signal(signal_name):
			screen.connect(signal_name, _on_overlay_back.bind(return_focus), CONNECT_ONE_SHOT)
			return
	push_warning("MainMenu: overlay '%s' exposes no recognized back signal" % screen.name)


## Shared back handler for every overlay. Releases the active-overlay guard, then
## frees the layer only if the overlay did not already free itself — overlays such
## as LoadScreen self-free, so we skip a layer already queued for deletion and
## avoid a redundant free, while still cleaning up overlays that do not self-free.
## The main menu itself is never freed; focus returns to the originating button.
func _on_overlay_back(return_focus: Control) -> void:
	var layer := _active_overlay
	_active_overlay = null
	if is_instance_valid(layer) and not layer.is_queued_for_deletion():
		layer.queue_free()
	if is_instance_valid(return_focus):
		return_focus.grab_focus()

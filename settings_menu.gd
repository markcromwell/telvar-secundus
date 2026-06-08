extends Control

signal back_pressed

@onready var master_slider: HSlider = $VBoxContainer/MasterRow/MasterSlider
@onready var master_value_label: Label = $VBoxContainer/MasterRow/MasterValueLabel
@onready var music_slider: HSlider = $VBoxContainer/MusicRow/MusicSlider
@onready var music_value_label: Label = $VBoxContainer/MusicRow/MusicValueLabel
@onready var sfx_slider: HSlider = $VBoxContainer/SfxRow/SfxSlider
@onready var sfx_value_label: Label = $VBoxContainer/SfxRow/SfxValueLabel
@onready var back_button: Button = $VBoxContainer/BackButton


func _ready() -> void:
	# Connect signals in code to be explicit
	master_slider.value_changed.connect(_on_master_slider_value_changed)
	music_slider.value_changed.connect(_on_music_slider_value_changed)
	sfx_slider.value_changed.connect(_on_sfx_slider_value_changed)
	back_button.pressed.connect(_on_back_button_pressed)

	# Initialize slider values from the Menu autoload
	_initialize_sliders()


func _initialize_sliders() -> void:
	# Set master slider
	var master_vol = Menu.get_volume("Master")
	master_slider.value = master_vol
	master_value_label.text = str(int(master_vol))

	# Set music slider
	var music_vol = Menu.get_volume("Music")
	music_slider.value = music_vol
	music_value_label.text = str(int(music_vol))

	# Set sfx slider
	var sfx_vol = Menu.get_volume("SFX")
	sfx_slider.value = sfx_vol
	sfx_value_label.text = str(int(sfx_vol))


func _on_master_slider_value_changed(value: float) -> void:
	master_value_label.text = str(int(value))
	Menu.set_volume("Master", value)


func _on_music_slider_value_changed(value: float) -> void:
	music_value_label.text = str(int(value))
	Menu.set_volume("Music", value)


func _on_sfx_slider_value_changed(value: float) -> void:
	sfx_value_label.text = str(int(value))
	Menu.set_volume("SFX", value)


func _on_back_button_pressed() -> void:
	emit_signal("back_pressed")

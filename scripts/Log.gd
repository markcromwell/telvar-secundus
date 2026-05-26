class_name Log
extends RefCounted
## Minimal logging helpers for autoloads and gameplay code.


static func warn(message: String) -> void:
	push_warning(message)

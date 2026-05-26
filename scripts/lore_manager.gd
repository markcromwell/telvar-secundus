extends Node

## Autoload: tracks which lore entry IDs the player has unlocked.

signal lore_unlocked(entry_id: String)

var unlocked: Array[String] = []


func unlock(entry_id: String) -> void:
	if unlocked.has(entry_id):
		return
	unlocked.append(entry_id)
	lore_unlocked.emit(entry_id)


func is_unlocked(id: String) -> bool:
	return unlocked.has(id)

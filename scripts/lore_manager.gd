extends Node

signal lore_unlocked(entry_id: String)

var unlocked: Array[String] = []


func unlock(entry_id: String) -> void:
	if is_unlocked(entry_id):
		return
	unlocked.append(entry_id)
	lore_unlocked.emit(entry_id)


func is_unlocked(id: String) -> bool:
	return id in unlocked

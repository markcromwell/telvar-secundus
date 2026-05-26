# Telvar: Chronicles of Secundus

A top-down RPG set in the city of Secundus from the New Paladin Order book series.
Young Telvar Orsson grows from merchant's son to wizard apprentice.

Built with Godot 4.x · Free LPC Tilesets · Inspired by Ultima IV

## Scene changes and autosave

Use the `SceneTransition` autoload for all scene switches (`change_scene_to_file` / `change_scene_to_packed`). It writes `user://save_autosave.json` first, with no UI. In load menus, use `SaveManager.get_slot_display_name(path)` so that slot shows as **Autosave**.


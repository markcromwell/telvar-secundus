# Telvar: Chronicles of Secundus

A top-down RPG set in the city of Secundus from the New Paladin Order book series.
Young Telvar Orsson grows from merchant's son to wizard apprentice.

Built with Godot 4.x · Free LPC Tilesets · Inspired by Ultima IV

## Apprentice hall (Veneficturis)

`apprentice_room.tscn` is an 8×6 tile room with three friend NPCs (Daran, Yessa, Corvin). Each uses `apprentice_npc.gd` with LPC-layout 32×32 walk sheets under `assets/sprites/lpc_apprentice/` and dialogue from `data/dialogue/apprentice_room_friends.json` (not `veneficturis_npcs.json`).

Room registration and per-NPC tile spawns live in `data/game_data_resources.json` (`veneficturis_apprentice_room`); `apprentice_room_floor.gd` reads that file at runtime and places `NpcDaran` / `NpcYessa` / `NpcCorvin` on the grid.


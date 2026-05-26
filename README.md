# Telvar: Chronicles of Secundus

A top-down RPG set in the city of Secundus from the New Paladin Order book series.
Young Telvar Orsson grows from merchant's son to wizard apprentice.

Built with Godot 4.x · Free LPC Tilesets · Inspired by Ultima IV

## Veneficturis Library (Phase 2624)

- Scene: `scenes/veneficturis/Library.tscn` — 30×20 `TileMap` using `assets/tilesets/lpc_terrain.tres` (16×16 source tiles; project `content_scale_factor=2` for crisp UI/world pixels).
- Structural checks: `python3 validate.py`
- Fast CI tests: `python3 -m pytest scripts/test_unit.py -q`

The library expects a `CharacterBody2D` in the `player` group for interaction prompts (`ui_accept` / Enter).

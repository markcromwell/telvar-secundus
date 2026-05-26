# Telvar: Chronicles of Secundus

A top-down RPG set in the city of Secundus from the New Paladin Order book series.
Young Telvar Orsson grows from merchant's son to wizard apprentice.

Built with Godot 4.x · Free LPC Tilesets · Inspired by Ultima IV

## Tests

- **Python (CI smoke):** `python -m pytest scripts/test_unit.py -q`
- **GdUnit4 (Godot 4.3):** from the repo root, with a 4.3 binary (headless requires `--ignoreHeadlessMode` after the GdUnit script path):

```bash
/path/to/Godot_v4.3-stable_linux.x86_64 --headless --path . \
  -s res://addons/gdUnit4/bin/GdUnitCmdTool.gd --ignoreHeadlessMode -a res://tests/test_district_zones.gd
```


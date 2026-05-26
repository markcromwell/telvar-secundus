#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap stub).
Full validation is implemented in spec #1246.
During early development, this exits 0 to allow the pipeline to proceed.
"""
import sys, os

# Bootstrap mode: check only what is strictly required at this stage
errors = []

# Phase 2741: AudioManager autoload (structural)
_root = os.path.dirname(os.path.abspath(__file__))
_audio_gd = os.path.join(_root, "autoload", "AudioManager.gd")
_audio_tscn = os.path.join(_root, "autoload", "AudioManager.tscn")
_project = os.path.join(_root, "project.godot")
if not os.path.isfile(_audio_gd):
    errors.append("missing autoload/AudioManager.gd")
if not os.path.isfile(_audio_tscn):
    errors.append("missing autoload/AudioManager.tscn")
if os.path.isfile(_project):
    with open(_project, encoding="utf-8") as f:
        pg = f.read()
    if "[autoload]" not in pg or "AudioManager" not in pg:
        errors.append("project.godot must register AudioManager in [autoload]")
    if "res://autoload/AudioManager.tscn" not in pg:
        errors.append("AudioManager autoload path must be res://autoload/AudioManager.tscn")

# Only enforce critical structural checks here
# (Full validation in spec 1246)

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Bootstrap checks passed (spec 1246 will add full validation)")
sys.exit(0)

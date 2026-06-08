#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap stub).
Full validation is implemented in spec #1246.
During early development, this exits 0 to allow the pipeline to proceed.
"""
import argparse
import os
import sys
import time
import urllib.request
import urllib.error


ROOT = os.path.dirname(os.path.abspath(__file__))


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def first_existing(*relative_paths):
    for relative_path in relative_paths:
        path = os.path.join(ROOT, relative_path)
        if os.path.isfile(path):
            return path
    return None

def fetch_url(url, timeout=30):
    """
    Fetches content from a URL.
    Returns a tuple of (content, status_code, error_message, duration).
    """
    start_time = time.time()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            duration = time.time() - start_time
            # Godot HTML5 export is utf-8
            return (
                response.read().decode("utf-8"),
                response.status,
                None,
                duration,
            )
    except urllib.error.HTTPError as e:
        duration = time.time() - start_time
        return None, e.code, str(e), duration
    except Exception as e:
        duration = time.time() - start_time
        return None, None, str(e), duration


def check_live_url(url, fetcher):
    """
    Performs live smoke tests on a URL using the provided fetcher.
    Returns a list of error strings.
    """
    errors = []
    content, status, err_msg, duration = fetcher(url)

    if err_msg:
        errors.append(f"Failed to fetch {url}: {err_msg}")
        return errors

    print(f"URL fetched in {duration:.2f}s.")

    if status != 200:
        errors.append(f"Expected HTTP 200, but got {status}")

    if not content:
        errors.append("Received empty response body")

    # Godot HTML5 boot markers
    if '<canvas id="canvas"' not in content:
        errors.append("Missing Godot <canvas> element")
    if "Godot Engine" not in content:
        errors.append("Missing 'Godot Engine' marker in HTML")
    if "Telvar" not in content:
        errors.append("Missing project title marker 'Telvar' in HTML")

    # Check for common error patterns
    # These are generic and might need refinement if they cause false positives.
    error_markers = ["error", "failed", "exception"]
    for marker in error_markers:
        # Simple search for error-like strings in the body
        if marker in content.lower():
            # A simple heuristic to reduce false positives: look for it near script tags
            # or in console error-like formats.
            if "error:" in content.lower() or "uncaught" in content.lower():
                 errors.append(f"Found potential error marker: '{marker}'")

    if duration > 3.0:
        print(f"WARN: Page load took {duration:.2f}s, exceeding 3s target.")

    return errors


def run_file_checks():
    """Performs original validation checks on local files."""
    errors = []
    _credits = os.path.join(ROOT, "CREDITS.md")
    if not os.path.isfile(_credits):
        errors.append("Missing CREDITS.md at repository root")
    else:
        _ct = read_text(_credits)
        if "# Credits" not in _ct:
            errors.append("CREDITS.md must contain a '# Credits' heading")
        for _heading in ("## Art", "## Code", "## Story", "## Audio"):
            if _heading not in _ct:
                errors.append(f"CREDITS.md must contain section {_heading}")

    _credits_scene = first_existing("scenes/ui/Credits.tscn", "Credits.tscn")
    if _credits_scene is None:
        errors.append("Missing Credits scene (expected scenes/ui/Credits.tscn or Credits.tscn)")
    else:
        _scene = read_text(_credits_scene)
        if 'type="Control"' not in _scene:
            errors.append("Credits scene must have a Control root")
        if 'type="ScrollContainer"' not in _scene:
            errors.append("Credits scene must include a ScrollContainer")
        if 'type="RichTextLabel"' not in _scene:
            errors.append("Credits scene must include a RichTextLabel")

    _main_menu_scene = first_existing("scenes/ui/MainMenu.tscn", "MainMenu.tscn")
    if _main_menu_scene is None:
        errors.append("Missing MainMenu scene (expected scenes/ui/MainMenu.tscn or MainMenu.tscn)")
    else:
        _menu = read_text(_main_menu_scene)
        if 'name="CreditsButton"' not in _menu:
            errors.append("MainMenu scene must include a CreditsButton node")
        if 'type="Button"' not in _menu:
            errors.append("MainMenu CreditsButton must be a Button node")
        if 'text = "Credits"' not in _menu and 'text="Credits"' not in _menu:
            errors.append('MainMenu CreditsButton must display text "Credits"')

    _export_presets = os.path.join(ROOT, "export_presets.cfg")
    if os.path.isfile(_export_presets):
        _export = read_text(_export_presets)
        if 'platform="Web"' in _export and "*.md" not in _export:
            errors.append("Web export preset must include markdown files so CREDITS.md is packaged")
    return errors

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    TELVAR-RPG validation script.
    Performs file-based structural checks by default.
    With --live-url, performs a smoke test on a deployed HTML5 build.
    """)
    parser.add_argument(
        "--live-url",
        type=str,
        help="URL of a deployed Godot HTML5 page to smoke test."
    )
    args = parser.parse_args()

    errors = []
    if args.live_url:
        print(f"Performing live smoke test on {args.live_url}...")
        errors = check_live_url(args.live_url, fetch_url)
    else:
        errors = run_file_checks()

    if errors:
        for e in errors:
            print("FAIL:", e)
        sys.exit(1)

    if args.live_url:
        print("Live URL smoke test passed.")
    else:
        print("Bootstrap checks passed (spec 1246 will add full validation)")

    sys.exit(0)

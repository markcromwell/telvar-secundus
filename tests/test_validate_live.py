"""Unit tests for validate.py live GitHub Pages smoke-check logic.

These exercise ``validate.check_live_url`` with an injected fake fetcher so no
real network access ever occurs. The fetcher contract is::

    fetcher(url) -> (content, status, err_msg, duration)

which makes both the HTTP response *and* the elapsed time deterministic, so the
3-second load target and the 30-second budget can be asserted without a clock.
"""

from __future__ import annotations

import pytest

import validate

# A minimal, well-formed Godot HTML5 boot page that satisfies every required
# marker (canvas host, engine banner, project title) and contains none of the
# error markers (``error`` / ``failed`` / ``exception``).
GOOD_HTML = """<!DOCTYPE html>
<html>
<head><title>Telvar RPG</title></head>
<body>
  <canvas id="canvas"></canvas>
  <script>/* Godot Engine 4.3 HTML5 export for Telvar */</script>
</body>
</html>
"""


def make_fetcher(content=GOOD_HTML, status=200, err_msg=None, duration=1.0):
    """Build a fake fetcher matching validate.fetch_url's return contract."""

    def _fetch(url):
        return (content, status, err_msg, duration)

    return _fetch


@pytest.fixture(autouse=True)
def _block_network(monkeypatch):
    """Guarantee that no test reaches the real network via urllib."""

    def _boom(*args, **kwargs):
        raise AssertionError("network access is not allowed in unit tests")

    monkeypatch.setattr(validate.urllib.request, "urlopen", _boom)


def test_successful_title_load_returns_no_errors():
    # No errors from check_live_url is what drives sys.exit(0) in validate.py.
    errors = validate.check_live_url("https://example.test/", make_fetcher())
    assert errors == []


def test_non_200_response_fails():
    errors = validate.check_live_url(
        "https://example.test/", make_fetcher(status=404)
    )
    assert any("200" in e for e in errors)


def test_fetch_error_fails_fast():
    fetcher = make_fetcher(content=None, status=None, err_msg="connection refused")
    errors = validate.check_live_url("https://example.test/", fetcher)
    # An unreachable host yields exactly one fetch error and short-circuits.
    assert len(errors) == 1
    assert "Failed to fetch" in errors[0]


def test_empty_body_fails():
    errors = validate.check_live_url(
        "https://example.test/", make_fetcher(content="")
    )
    assert any("empty response" in e.lower() for e in errors)


def test_missing_canvas_marker_fails():
    html = GOOD_HTML.replace('<canvas id="canvas">', "<div></div>")
    errors = validate.check_live_url("https://example.test/", make_fetcher(content=html))
    assert any("canvas" in e.lower() for e in errors)


def test_missing_godot_engine_marker_fails():
    html = GOOD_HTML.replace("Godot Engine", "Some Other Engine")
    errors = validate.check_live_url("https://example.test/", make_fetcher(content=html))
    assert any("Godot Engine" in e for e in errors)


def test_missing_title_marker_fails():
    html = GOOD_HTML.replace("Telvar", "Anonymous")
    errors = validate.check_live_url("https://example.test/", make_fetcher(content=html))
    assert any("Telvar" in e for e in errors)


def test_html5_audio_error_marker_fails():
    # A page that booted but logged an HTML5/audio failure must be flagged.
    html = GOOD_HTML.replace(
        "</body>",
        "<script>console.log('Uncaught error: audio context failed');</script></body>",
    )
    errors = validate.check_live_url("https://example.test/", make_fetcher(content=html))
    assert any("error marker" in e.lower() for e in errors)


def test_slow_load_flags_3s_target_but_still_succeeds(capsys):
    # 4.5s exceeds the 3s target yet stays well inside the 30s budget.
    duration = 4.5
    assert duration < 30.0
    errors = validate.check_live_url(
        "https://example.test/", make_fetcher(duration=duration)
    )
    out = capsys.readouterr().out
    assert errors == []  # over-target load is a warning, not a failure
    assert "exceeding 3s target" in out


def test_normal_load_does_not_warn(capsys):
    duration = 1.2
    assert duration < 3.0
    errors = validate.check_live_url(
        "https://example.test/", make_fetcher(duration=duration)
    )
    out = capsys.readouterr().out
    assert errors == []
    assert "exceeding 3s target" not in out
    assert "WARN" not in out

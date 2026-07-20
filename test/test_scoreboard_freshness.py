# Copyright (c) ONNX Project Contributors
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for the scoreboard freshness checker script."""

from __future__ import annotations

import json

from datetime import datetime, timezone

from scripts.check_scoreboard_freshness import (
    DATE_FORMAT,
    evaluate,
    extract_database,
    latest_date,
    parse_date,
    render_markdown,
)


def test_extract_database_parses_embedded_payload():
    """Read the embedded database JSON from the generated page."""
    payload = json.dumps({"backend": {"name": "RTen"}})
    html = "<div id='content' database='" + payload + "'>"
    assert extract_database(html) == {"backend": {"name": "RTen"}}


def test_latest_date_returns_last_trend_entry():
    """Use the latest trend item when deriving freshness."""
    backend_data = {
        "trend": [
            {"date": "03/24/2026 00:50:48"},
            {"date": "03/25/2026 00:50:48"},
        ]
    }

    assert latest_date(backend_data) == "03/25/2026 00:50:48"


def test_evaluate_marks_stale_and_missing_backends():
    """Classify stale, fresh, and missing-trend backends consistently."""
    now = datetime(2026, 3, 28, 0, 50, 48, tzinfo=timezone.utc)
    database = {
        "fresh": {
            "name": "Fresh Backend",
            "trend": [{"date": "03/27/2026 00:50:48"}],
        },
        "stale": {
            "name": "Stale Backend",
            "trend": [{"date": "03/20/2026 00:50:48"}],
        },
        "missing": {"name": "Missing Backend", "trend": []},
    }

    report = evaluate(database, max_age_days=3.0, now=now)

    assert {row["backend"] for row in report} == {"missing", "stale", "fresh"}
    missing = next(row for row in report if row["backend"] == "missing")
    stale = next(row for row in report if row["backend"] == "stale")
    fresh = next(row for row in report if row["backend"] == "fresh")

    assert missing["stale"] is True
    assert missing["reason"] == "no trend data"
    assert stale["stale"] is True
    assert fresh["stale"] is False


def test_render_markdown_includes_backend_statuses():
    """Render a stable issue body that highlights stale backends."""
    now = datetime(2026, 3, 28, 0, 50, 48, tzinfo=timezone.utc)
    source = "scoreboard-source"
    report = [
        {
            "backend": "stale",
            "name": "Stale Backend",
            "date": "03/20/2026 00:50:48",
            "age_days": 8.0,
            "stale": True,
            "reason": "",
        },
        {
            "backend": "fresh",
            "name": "Fresh Backend",
            "date": "03/27/2026 00:50:48",
            "age_days": 1.0,
            "stale": False,
            "reason": "",
        },
    ]

    body = render_markdown(report, source, 3.0, now)

    assert "Stale Backend" in body
    assert "✅ ok" in body
    assert "⚠️ stale" in body
    assert source in body


def test_parse_date_uses_scoreboard_format():
    """Parse the website's date format into a UTC datetime."""
    parsed = parse_date("03/25/2026 00:50:48")

    assert parsed.tzinfo == timezone.utc
    assert parsed.strftime(DATE_FORMAT) == "03/25/2026 00:50:48"

# Copyright (c) ONNX Project Contributors
#
# SPDX-License-Identifier: Apache-2.0

"""Check whether the published scoreboard page shows up-to-date data.

The script downloads the rendered scoreboard page (by default the public
``index.html``), reads the per-backend "Date" values that the website renders
from ``trend[-1].date`` and reports any backend whose latest update is older
than a configurable threshold (default: 3 days).

It is meant to run in CI: results are written to ``GITHUB_OUTPUT`` so a
follow-up step can open / update / close a single tracking issue.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request

from datetime import datetime, timezone


DEFAULT_URL = "https://onnx.ai/backend-scoreboard/index.html"

# The website embeds the full scoreboard as JSON in
# <div id="content" database='{...}'>. The visible "Date" column is rendered
# from each backend's last trend entry (trend[-1].date).
DATABASE_RE = re.compile(r"database='(.*?)'>", re.DOTALL)

# Date format produced by website-generator/generator.py:
# datetime.now().strftime("%m/%d/%Y %H:%M:%S")
DATE_FORMAT = "%m/%d/%Y %H:%M:%S"


def fetch_html(url: str, timeout: int = 60) -> str:
    """Download the scoreboard page."""
    headers = {"User-Agent": "scoreboard-freshness-check"}
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def extract_database(html: str) -> dict:
    """Extract and parse the embedded scoreboard database JSON."""
    match = DATABASE_RE.search(html)
    if not match:
        raise ValueError("Could not find the 'database' payload in the page")
    return json.loads(match.group(1))


def latest_date(backend_data: dict) -> str | None:
    """Return the most recent trend date string for a backend, if any."""
    trend = backend_data.get("trend") or []
    if not trend:
        return None
    return trend[-1].get("date")


def parse_date(value: str) -> datetime:
    """Parse a scoreboard date string as a UTC datetime."""
    return datetime.strptime(value, DATE_FORMAT).replace(tzinfo=timezone.utc)


def evaluate(database: dict, max_age_days: float, now: datetime) -> list[dict]:
    """Return a per-backend freshness report sorted by descending age."""
    report = []
    for backend, backend_data in database.items():
        name = backend_data.get("name", backend)
        date_str = latest_date(backend_data)

        if not date_str:
            report.append(
                {
                    "backend": backend,
                    "name": name,
                    "date": None,
                    "age_days": None,
                    "stale": True,
                    "reason": "no trend data",
                }
            )
            continue

        try:
            updated = parse_date(date_str)
        except ValueError:
            report.append(
                {
                    "backend": backend,
                    "name": name,
                    "date": date_str,
                    "age_days": None,
                    "stale": True,
                    "reason": "unparseable date",
                }
            )
            continue

        age_days = (now - updated).total_seconds() / 86400.0
        report.append(
            {
                "backend": backend,
                "name": name,
                "date": date_str,
                "age_days": age_days,
                "stale": age_days > max_age_days,
                "reason": "",
            }
        )

    def sort_key(row: dict) -> float:
        return -1.0 if row["age_days"] is None else row["age_days"]

    report.sort(key=sort_key, reverse=True)
    return report


def render_markdown(
    report: list[dict], url: str, max_age_days: float, now: datetime
) -> str:
    """Build a Markdown summary suitable for an issue body."""
    stale = [row for row in report if row["stale"]]
    lines = [
        f"The scoreboard page reports data older than **{max_age_days:g} days** "
        f"for {len(stale)} of {len(report)} backend(s).",
        "",
        f"- Source: {url}",
        f"- Checked at: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC",
        "",
        "| Backend | Last update (UTC) | Age | Status |",
        "| --- | --- | --- | --- |",
    ]
    for row in report:
        if row["age_days"] is None:
            age = row["reason"] or "unknown"
        else:
            age = f"{row['age_days']:.1f} days"
        status = "⚠️ stale" if row["stale"] else "✅ ok"
        lines.append(f"| {row['name']} | {row['date'] or '—'} | {age} | {status} |")
    return "\n".join(lines)


def write_outputs(stale: bool, report: list[dict], body: str) -> None:
    """Expose results to later workflow steps via GITHUB_OUTPUT."""
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    stale_names = ", ".join(row["name"] for row in report if row["stale"])
    with open(output_path, "a", encoding="utf-8") as handle:
        handle.write(f"stale={'true' if stale else 'false'}\n")
        handle.write(f"stale_count={sum(1 for row in report if row['stale'])}\n")
        handle.write(f"stale_backends={stale_names}\n")
        handle.write("body<<FRESHNESS_EOF\n")
        handle.write(body + "\n")
        handle.write("FRESHNESS_EOF\n")


def main(argv: list[str] | None = None) -> int:
    """Run the freshness check and emit a report plus CI outputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="Scoreboard page URL")
    parser.add_argument(
        "--html-file",
        help="Read the page from a local file instead of fetching it (for testing)",
    )
    parser.add_argument(
        "--max-age-days",
        type=float,
        default=3.0,
        help="A backend is stale if its latest date is older than this many days "
        "(default: 3)",
    )
    args = parser.parse_args(argv)

    source = args.html_file or args.url
    try:
        if args.html_file:
            with open(args.html_file, encoding="utf-8") as handle:
                html = handle.read()
        else:
            html = fetch_html(args.url)
        database = extract_database(html)
    except Exception as error:  # noqa: BLE001 - surface any failure as a stale signal
        message = f"Failed to read scoreboard data from {source}: {error}"
        print(message, file=sys.stderr)
        body = (
            f"The freshness check could not read the scoreboard page.\n\n"
            f"- Source: {source}\n- Error: `{error}`"
        )
        write_outputs(True, [], body)
        return 0

    now = datetime.now(timezone.utc)
    report = evaluate(database, args.max_age_days, now)
    stale = any(row["stale"] for row in report)
    body = render_markdown(report, source, args.max_age_days, now)

    print(body)
    write_outputs(stale, report, body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

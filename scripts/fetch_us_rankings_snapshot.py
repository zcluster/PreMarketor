#!/usr/bin/env python3
"""Capture the small Moomoo ranking subset used by the A/H brief."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

INDUSTRY_URL = "https://www.moomoo.com/hans/quote/us/sector-industry"
CONCEPT_URL = "https://www.moomoo.com/hans/quote/sparks-us"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "Chrome/126.0.0.0 Safari/537.36"
)


def extract_initial_state(html: str) -> dict:
    marker = "window.__INITIAL_STATE__="
    start = html.find(marker)
    if start < 0:
        raise ValueError("window.__INITIAL_STATE__ not found")
    start += len(marker)
    decoder = json.JSONDecoder()
    state, _ = decoder.raw_decode(html[start:].lstrip())
    return state


def pct_value(value: object) -> float:
    text = str(value or "").replace("%", "").replace(",", "").strip()
    return float(text)


def normalize_row(row: dict) -> dict:
    return {
        "name": row.get("plateName"),
        "nameEn": row.get("plateEnName"),
        "code": row.get("plateCode"),
        "changePct": row.get("changeRatio"),
        "leaderName": row.get("stockName"),
        "leaderTicker": row.get("stockCode"),
        "leaderChangePct": row.get("stockChangeRatio"),
        "breadth": {
            "advancers": row.get("priceRiseCount"),
            "decliners": row.get("priceFallCount"),
            "unchanged": row.get("priceSameCount"),
        },
    }


def positive_top(rows: list[dict], limit: int = 5) -> list[dict]:
    ranked = sorted(rows, key=lambda row: pct_value(row.get("changeRatio")), reverse=True)
    return [normalize_row(row) for row in ranked if pct_value(row.get("changeRatio")) > 0][:limit]


def negative_bottom(rows: list[dict], limit: int = 5) -> list[dict]:
    negative = sorted(rows, key=lambda row: pct_value(row.get("changeRatio")))[:limit]
    return [normalize_row(row) for row in reversed(negative) if pct_value(row.get("changeRatio")) < 0]


def previous_success(previous: dict, group_name: str) -> dict | None:
    group = previous.get("groups", {}).get(group_name, {})
    if group.get("status") in {"ok", "partial"}:
        return {
            "fetchedAt": group.get("fetchedAt"),
            "top": group.get("top", []),
            "bottom": group.get("bottom", []),
        }
    return group.get("lastSuccess")


async def response_text(page, url: str) -> tuple[str, int]:
    response = await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
    if response is None:
        raise RuntimeError("navigation returned no response")
    if response.status != 200:
        raise RuntimeError(f"HTTP {response.status}; final URL {page.url}")
    return await response.text(), response.status


async def fetch_industry(page, fetched_at: str) -> dict:
    html, status_code = await response_text(page, INDUSTRY_URL)
    state = extract_initial_state(html)
    plate = state["plate_list"]
    pagination = plate["pagination"]
    top = positive_top(plate["list"])
    page_count = int(pagination["pageCount"])
    if not top:
        raise RuntimeError("no positive industry rows on first page")

    bottom: list[dict] = []
    bottom_error = None
    if page_count > 1:
        try:
            items = page.locator(".base-pagination.pagination > span.item")
            target = None
            for index in range(await items.count()):
                candidate = items.nth(index)
                if (await candidate.inner_text()).strip() == str(page_count):
                    target = candidate
                    break
            if target is None:
                raise RuntimeError(f"last-page control {page_count} not found")
            async with page.expect_response(
                lambda response: "/get-plate-list" in response.url,
                timeout=20_000,
            ) as pending:
                await target.click()
            payload = await (await pending.value).json()
            data = payload.get("data") or {}
            api_page = int((data.get("pagination") or {}).get("page", -1))
            if api_page != page_count - 1:
                raise RuntimeError(f"last-page assertion failed: {api_page} != {page_count - 1}")
            bottom = negative_bottom(data.get("list") or [])
            if not bottom:
                raise RuntimeError("no negative industry rows on last page")
        except Exception as exc:  # Top5 is still useful when the last-page request fails.
            bottom_error = f"{type(exc).__name__}: {exc}"

    return {
        "status": "ok" if len(top) == 5 and len(bottom) == 5 else "partial",
        "source": "Moomoo industry ranking",
        "sourceUrl": INDUSTRY_URL,
        "httpStatus": status_code,
        "fetchedAt": fetched_at,
        "pagination": {
            "firstPage": int(pagination.get("page", 0)),
            "pageCount": page_count,
            "total": pagination.get("total"),
        },
        "top": top,
        "bottom": bottom,
        "missing": (["bottom5"] if bottom_error else []),
        "error": bottom_error,
    }


async def fetch_concept(page, fetched_at: str) -> dict:
    html, status_code = await response_text(page, CONCEPT_URL)
    sparks = extract_initial_state(html)["sparks_index"]
    top = positive_top(sparks["list"])
    if not top:
        raise RuntimeError("no positive concept rows on first page")
    return {
        "status": "ok" if len(top) == 5 else "partial",
        "source": "Moomoo Sparks",
        "sourceUrl": CONCEPT_URL,
        "httpStatus": status_code,
        "fetchedAt": fetched_at,
        "pagination": sparks.get("pagination"),
        "top": top,
        "bottom": [],
        "missing": ([] if len(top) == 5 else ["top5_incomplete"]),
        "error": None,
    }


async def capture(output: Path) -> dict:
    previous = {}
    if output.exists():
        try:
            previous = json.loads(output.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            previous = {}

    now = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")
    groups = {}
    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            channel="chrome",
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = await browser.new_context(user_agent=USER_AGENT, locale="zh-CN")
        for name, fetcher in (("industry", fetch_industry), ("concept", fetch_concept)):
            page = await context.new_page()
            try:
                groups[name] = await fetcher(page, now)
            except Exception as exc:
                groups[name] = {
                    "status": "error",
                    "source": "Moomoo industry ranking" if name == "industry" else "Moomoo Sparks",
                    "sourceUrl": INDUSTRY_URL if name == "industry" else CONCEPT_URL,
                    "fetchedAt": None,
                    "top": [],
                    "bottom": [],
                    "missing": ["all_current_rows"],
                    "error": f"{type(exc).__name__}: {exc}",
                    "lastSuccess": previous_success(previous, name),
                }
            finally:
                await page.close()
        await browser.close()

    current_groups = sum(group["status"] != "error" for group in groups.values())
    status = "ok" if current_groups == 2 and all(g["status"] == "ok" for g in groups.values()) else (
        "partial" if current_groups else "error"
    )
    return {
        "schemaVersion": 1,
        "provider": "Moomoo",
        "attemptedAt": now,
        "status": status,
        "groups": groups,
    }


def validate(snapshot: dict) -> None:
    if snapshot.get("schemaVersion") != 1:
        raise ValueError("unexpected schemaVersion")
    for name in ("industry", "concept"):
        group = snapshot["groups"][name]
        if group["status"] in {"ok", "partial"}:
            for row in group["top"] + group["bottom"]:
                if not row.get("name") or not row.get("changePct"):
                    raise ValueError(f"{name} row lacks name/changePct")
    if len(snapshot["groups"]["concept"]["bottom"]) != 0:
        raise ValueError("concept Bottom5 must not be fetched")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/us-rankings-latest.json"))
    args = parser.parse_args()
    snapshot = asyncio.run(capture(args.output))
    validate(snapshot)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"US rankings snapshot: {snapshot['status']} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

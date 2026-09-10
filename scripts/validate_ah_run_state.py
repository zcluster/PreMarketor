#!/usr/bin/env python3
"""Validate the shared A/H run-state contract using only the standard library."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


TERMINAL = {"published", "failed", "blocked"}
ALLOWED = TERMINAL | {"running"}


def parse_time(value: object, field: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str):
        errors.append(f"{field} must be an ISO-8601 string")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{field} is not valid ISO-8601")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{field} must include a timezone")
        return None
    return parsed


def validate(state: dict, now: datetime | None = None) -> list[str]:
    errors: list[str] = []
    for field in ("run_id", "owner", "status", "heartbeat_at", "lease_until"):
        if field not in state:
            errors.append(f"missing {field}")
    status = state.get("status")
    if status not in ALLOWED:
        errors.append(f"status must be one of {sorted(ALLOWED)}")
    heartbeat = parse_time(state.get("heartbeat_at"), "heartbeat_at", errors)
    lease = parse_time(state.get("lease_until"), "lease_until", errors)
    if heartbeat and lease:
        if status == "running" and lease <= heartbeat:
            errors.append("running lease_until must be after heartbeat_at")
        if status in TERMINAL and lease > heartbeat:
            errors.append("terminal state must release the lease")
        if status == "running" and now and lease <= now:
            errors.append("running lease is expired; write failed/blocked or perform a CAS takeover")
    if status == "published" and not state.get("published_commit"):
        errors.append("published requires published_commit")
    if status in {"failed", "blocked"}:
        error = state.get("error")
        if not isinstance(error, dict):
            errors.append(f"{status} requires an error object")
        else:
            for field in ("stage", "code", "message", "recoverable_stage", "occurred_at"):
                if not error.get(field):
                    errors.append(f"error.{field} is required")
            if error.get("occurred_at"):
                parse_time(error["occurred_at"], "error.occurred_at", errors)
    if state.get("published_commit") and status != "published":
        stage = state.get("error", {}).get("stage") if isinstance(state.get("error"), dict) else None
        if status not in {"running", "blocked"} or (status == "blocked" and stage != "deployment_verification"):
            errors.append("non-published published_commit is allowed only while verifying deployment or when deployment is blocked")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path)
    parser.add_argument("--now", help="ISO-8601 time used to detect an expired running lease")
    args = parser.parse_args()
    state = json.loads(args.state.read_text(encoding="utf-8"))
    now = None
    now_errors: list[str] = []
    if args.now:
        now = parse_time(args.now, "--now", now_errors)
    errors = now_errors + validate(state, now)
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

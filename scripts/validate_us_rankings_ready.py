#!/usr/bin/env python3
"""Require current rows for both ranking groups before publishing the morning brief."""
import argparse
import hashlib
import json
import math
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from scripts.update_us_rankings_panel import latest_close


def validate(snapshot, expected_session, now):
    errors = []
    session = date.fromisoformat(expected_session)
    close = datetime.combine(session, datetime.min.time()).replace(hour=16, tzinfo=ZoneInfo('America/New_York'))
    if session.weekday() >= 5 or close > now:
        errors.append('expected session is not a completed weekday session')
    if snapshot.get('status') not in ('ok', 'partial'):
        errors.append('current snapshot unavailable')
    for name in ('industry', 'concept'):
        group = snapshot.get('groups', {}).get(name, {})
        try:
            fetched = datetime.fromisoformat(group['fetchedAt'])
            if fetched.tzinfo is None or not close <= fetched <= now:
                errors.append(name + ': capture does not cover the required close')
        except (KeyError, TypeError, ValueError):
            errors.append(name + ': valid capture time missing')
        rows = group.get('top', []) + (group.get('bottom', []) if name == 'industry' else [])
        if group.get('status') not in ('ok', 'partial') or not rows:
            errors.append(name + ': no current ranking rows')
        for row in rows:
            try:
                change = float(str(row['changePct']).replace('%', ''))
                if not row.get('name') or not math.isfinite(change):
                    raise ValueError('missing name')
            except (KeyError, TypeError, ValueError):
                errors.append(name + ': invalid current row')
    return errors


def groups_hash(snapshot):
    return hashlib.sha256(json.dumps(snapshot['groups'], sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('--expected-session-date')
    parser.add_argument('--request', type=Path)
    parser.add_argument('--annotate', action='store_true')
    args = parser.parse_args()
    now = datetime.now(ZoneInfo('Asia/Shanghai'))
    request = json.loads(args.request.read_text()) if args.request else {}
    expected = args.expected_session_date or request.get('expected_session_date') or latest_close(now).date().isoformat()
    snapshot = json.loads(args.snapshot.read_text())
    errors = validate(snapshot, expected, now)
    gate = {'ready': not errors, 'expected_session_date': expected,
            'checked_at': now.isoformat(timespec='seconds'), 'request_id': request.get('request_id'),
            'groups_sha256': groups_hash(snapshot), 'errors': errors}
    if args.annotate:
        snapshot['publicationGate'] = gate
        args.snapshot.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(gate, ensure_ascii=False))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())

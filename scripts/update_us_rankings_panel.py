#!/usr/bin/env python3
"""Refresh the two homepage ranking markers from the current source snapshot."""
import argparse
import json
import re
from datetime import datetime, timedelta
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo


def latest_close(reference):
    day = reference.astimezone(ZoneInfo('America/New_York'))
    close = day.replace(hour=16, minute=0, second=0, microsecond=0)
    if day < close:
        close -= timedelta(days=1)
    while close.weekday() >= 5:
        close -= timedelta(days=1)
    return close


def ranking_html(snapshot, reference, english=False):
    result = []
    cutoff = latest_close(reference)
    for name, title in [('industry', 'Overnight US Industry Ranking' if english else '隔夜美股行业排行'),
                        ('concept', 'Overnight US Concept Ranking' if english else '隔夜美股概念排行')]:
        group = snapshot['groups'][name]
        fetched = datetime.fromisoformat(group['fetchedAt']) if group.get('fetchedAt') else None
        fresh = fetched is not None and cutoff <= fetched <= reference
        usable = fresh and group['status'] in ('ok', 'partial')
        rows = group.get('top', []) + (group.get('bottom', []) if name == 'industry' else []) if usable else []
        badge = ('Partial' if english else '部分数据') if group['status'] == 'partial' else ''
        if not usable:
            badge = 'Awaiting latest snapshot' if english else '等待最新快照'
        result.append(f'<div class="us-ranking-block {name}-ranking"><div class="us-sector-head"><b>{title}</b><span>{badge}</span></div><div class="spark-table">')
        for row in rows:
            display_name = row.get('nameEn') if english else row.get('name')
            ticker = row.get('leaderTicker') or ('unavailable' if english else '不可得')
            leader_change = row.get('leaderChangePct') or ('unavailable' if english else '不可得')
            change = str(row['changePct'])
            css = ' down' if change.startswith('-') else ''
            breadth = row.get('breadth') or {}
            counts = [str(breadth.get(key)) if breadth.get(key) is not None else ('unavailable' if english else '不可得')
                      for key in ('advancers', 'decliners', 'unchanged')]
            breadth_text = f'{counts[0]} up / {counts[1]} down / {counts[2]} flat' if english else f'涨{counts[0]} / 跌{counts[1]} / 平{counts[2]}'
            result.append(f'<div class="spark-row"><div><div class="spark-name">{escape(display_name or row["name"])}</div><div class="spark-leader">{escape(ticker)} {escape(leader_change)} · {escape(breadth_text)}</div></div><div class="spark-change{css}">{escape(change)}</div></div>')
        result.append('</div>')
        if usable:
            stamp = fetched.astimezone(ZoneInfo('America/New_York') if english else ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M %Z')
            message = f'Moomoo snapshot · {stamp} · {len(rows)} rows' if english else f'Moomoo 快照 · {stamp} · {len(rows)} 行'
            if group.get('missing'):
                message += ' · ' + ', '.join(group['missing'])
        else:
            message = ('The latest capture has not arrived or the source failed; old rows are not reused.' if english else '最新快照尚未到达或来源抓取失败；不沿用旧榜。')
        result.append(f'<p class="spark-source">{escape(message)}</p></div>')
    return ''.join(result)


def update_html(html, snapshot, reference):
    for marker, english in [('US_SECTOR_PANEL', False), ('US_SECTOR_PANEL_EN', True)]:
        start, end = f'<!-- {marker}_START -->', f'<!-- {marker}_END -->'
        if html.count(start) != 1 or html.count(end) != 1:
            raise ValueError(f'{marker}: expected exactly one marker pair')
        before, content = html.split(start, 1)
        _, after = content.split(end, 1)
        html = before + start + '\n' + ranking_html(snapshot, reference, english) + end + after
    return html


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, default=Path('data/us-rankings-latest.json'))
    parser.add_argument('--index', type=Path, default=Path('index.html'))
    args = parser.parse_args()
    snapshot = json.loads(args.snapshot.read_text(encoding='utf-8'))
    reference = datetime.fromisoformat(snapshot['attemptedAt'])
    original = args.index.read_text(encoding='utf-8')
    # A newer brief must never be overwritten by a delayed capture for an older session.
    match = re.search(r'<!-- A_H_TIME_START -->\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}) CST', original)
    if match:
        reference = max(reference, datetime.strptime(match[1], '%Y-%m-%d %H:%M').replace(tzinfo=ZoneInfo('Asia/Shanghai')))
    args.index.write_text(update_html(original, snapshot, reference), encoding='utf-8')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Validate cloud screening evidence against the actual bilingual stock cards.

Standard library only. Exit 1 on incomplete evidence; never infer pass from zero cards.
This checks contracts/arithmetic, not the truth of a source or investment merit.
"""
import argparse
import hashlib
import json
import math
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo


class Cards(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.depth = 0
        self.card_depth = None
        self.ticker_depth = None
        self.tickers = []
        self.text = ''
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag != 'div':
            return
        self.depth += 1
        classes = dict(attrs).get('class', '').split()
        if 'stock-card' in classes:
            self.card_depth = self.depth
            self.text = ''
        if self.card_depth is not None and 'stock-ticker' in classes:
            self.ticker_depth = self.depth

    def handle_data(self, data):
        if self.ticker_depth is not None:
            self.text += data

    def handle_endtag(self, tag):
        if tag != 'div':
            return
        if self.depth == self.ticker_depth:
            self.ticker_depth = None
        if self.depth == self.card_depth:
            self.tickers.append(self.text.strip())
            self.card_depth = None
        self.depth -= 1


def timestamp(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('timezone required')
    return result


def number(value):
    return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value)


def validate(evidence, cn, en):
    errors = []
    def require(ok, message):
        if not ok:
            errors.append(message)

    try:
        checked = timestamp(evidence['checked_at'])
        published = timestamp(evidence['publication_at'])
        require(checked <= published, 'publication precedes verification')
        candidates = evidence['candidates']
        expected = evidence['expected_candidates']
        require(bool(expected), 'candidate inventory missing; zero cards is not a pass')
        ids = [c['id'] for c in candidates]
        require(len(ids) == len(set(ids)), 'duplicate candidates')
        require(set(ids) == set(expected), 'candidate inventory not fully covered')
        require(bool(evidence.get('inventory_source')), 'inventory provenance missing')
        included = []
        unavailable = False
        for c in candidates:
            key = c['id']
            status = c.get('verification_status')
            decision = c.get('decision')
            require(status in ('verified', 'source_unavailable'), key + ': unfinished verification')
            require(decision in ('include', 'exclude'), key + ': decision missing')
            require(bool(c.get('reason')), key + ': reason missing')
            if status == 'verified' and decision == 'exclude':
                require(c.get('exclusion_kind') in ('hard_gate', 'negative_response', 'risk_priority'), key + ': verified exclusion basis missing')
                require(bool(c.get('exclusion_evidence')), key + ': exclusion evidence missing')
            if status == 'source_unavailable':
                unavailable = True
                attempts = c.get('attempts', [])
                domains = set()
                for a in attempts:
                    u = urlparse(a['url'])
                    require(u.scheme in ('https', 'http') and bool(u.hostname), key + ': invalid source URL')
                    domains.add(u.hostname)
                    require(bool(a.get('error')), key + ': source failure evidence missing')
                    require(timestamp(a['at']) <= checked, key + ': future source attempt')
                require(len(domains) >= 2, key + ': independent fallback not recorded')
                require(decision == 'exclude', key + ': unavailable candidate included')
            if decision != 'include':
                continue
            included.append(c['ticker_text'])
            require(status == 'verified', key + ': included without verification')
            require(c.get('currency') == {'A': 'CNY', 'HK': 'HKD'}.get(c.get('market')), key + ': currency/market mismatch')
            for field, limit, inclusive in [('market_cap', 1e10, True), ('profit_ttm', 0, False), ('latest_profit', 0, True)]:
                v = c.get(field)
                require(number(v) and (v >= limit if inclusive else v > limit), key + ': failed ' + field)
            pe = c.get('pe_ttm')
            require(number(pe) and 0 < pe <= 200, key + ': failed PE_TTM')
            for field in ('financial_source', 'financial_period', 'market_source', 'pros', 'cons', 'trigger', 'invalidation'):
                require(bool(c.get(field)), key + ': missing ' + field)
            quote_at = timestamp(c['quote_at'])
            require(quote_at <= checked, key + ': quote after verification')
            require(quote_at.date() == checked.date(), key + ': stale quote date')
            require(c.get('trigger_status') in ('met_at_quote', 'not_met', 'unavailable'), key + ': invalid trigger status')
            require(bool(c.get('quote_disclosure_cn')) and c['quote_disclosure_cn'] in cn, key + ': CN quote time disclosure missing')
            require(bool(c.get('quote_disclosure_en')) and c['quote_disclosure_en'] in en, key + ': EN quote time disclosure missing')
            if c.get('claims_current_confirmation'):
                require(False, key + ': use confirmation as of quote, not undated current confirmation')
            if c.get('relative_spread') is not None:
                require(timestamp(c['benchmark_at']) == quote_at, key + ': asynchronous exact relative spread')
            sessions = c['sessions']
            dates = [s['date'] for s in sessions]
            require(len(dates) == 21 and dates == sorted(set(dates)), key + ': expected 21 ordered unique trading sessions')
            require(bool(c.get('calendar_source')), key + ': trading calendar provenance missing')
            require(dates[-1] == c['return_endpoint'], key + ': return endpoint mismatch')
            require(dates[-1] < quote_at.date().isoformat(), key + ': interval returns must end at prior close')
            require(all(number(s.get('close')) and s['close'] > 0 for s in sessions), key + ': invalid close')
            if len(sessions) == 21 and all(number(s.get('close')) and s['close'] > 0 for s in sessions):
                for n in (5, 20):
                    actual = (sessions[-1]['close'] / sessions[-1-n]['close'] - 1) * 100
                    reported = c.get('return_' + str(n))
                    require(number(reported) and abs(actual - reported) <= .02, key + ': wrong return_' + str(n))
        for label, html in [('CN', cn), ('EN', en)]:
            require(Cards(html).tickers == included, label + ': displayed recommendations differ from evidence')
            require('零推荐通过硬筛选' not in html, label + ': internal success claim leaked')
        if not included:
            require(evidence.get('zero_reason') == ('source_unavailable' if unavailable else 'verified_exclusions'), 'zero recommendation reason misclassified')
    except (KeyError, TypeError, ValueError, IndexError, AttributeError) as exc:
        errors.append('invalid evidence: ' + str(exc))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('history', type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.history.read_text())
        entries = [e for e in data['entries'] if e.get('type') == 'AH']
        if len(entries) != 1:
            raise ValueError('expected exactly one AH entry')
        a = entries[0]
        evidence = json.loads(args.evidence.read_text())
        errors = validate(evidence, a['html'], a['html_en'])
        expected_time = timestamp(evidence['publication_at']).astimezone(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M CST')
        if a.get('time') != expected_time:
            errors.append('history publication time differs from evidence')
    except (ValueError, KeyError, OSError, TypeError) as exc:
        errors = [str(exc)]
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (args.evidence, args.history) if p.is_file()}
    print(json.dumps({'ok': not errors, 'errors': errors, 'sha256': hashes}, ensure_ascii=False))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())

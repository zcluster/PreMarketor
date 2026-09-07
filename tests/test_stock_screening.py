import unittest
from datetime import date, timedelta
from scripts.validate_stock_screening import validate


def fixture():
    dates = []
    d = date(2026, 9, 4)
    while len(dates) < 21:
        if d.weekday() < 5:
            dates.append(d.isoformat())
        d -= timedelta(days=1)
    c = dict(id='example', decision='include', verification_status='verified',
             reason='verified business mapping', ticker_text='600001', market='A',
             currency='CNY', market_cap=1e10, profit_ttm=1e8, latest_profit=1e7,
             pe_ttm=200, financial_source='https://issuer.example/report',
             financial_period='2026H1', market_source='https://exchange.example/quote',
             pros='orders', cons='dilution', trigger='above prior close', invalidation='below prior close',
             quote_at='2026-09-07T10:37:00+08:00', trigger_status='met_at_quote',
             quote_disclosure_cn='10:37 CST', quote_disclosure_en='10:37 CST',
             sessions=[dict(date=x, close=100) for x in reversed(dates)],
             calendar_source='https://exchange.example/calendar',
             return_endpoint='2026-09-04', return_5=0, return_20=0)
    e = dict(checked_at='2026-09-07T10:38:00+08:00', publication_at='2026-09-07T10:40:00+08:00',
             expected_candidates=['example'], inventory_source='cloud raw candidate inventory', candidates=[c])
    html = '<div class="stock-card"><div><div class="stock-ticker">600001</div></div><p>10:37 CST</p></div>'
    return e, html


class ScreeningTests(unittest.TestCase):
    def test_valid_boundary(self):
        e, h = fixture()
        self.assertEqual(validate(e, h, h), [])

    def test_pending_cannot_pass_with_zero_cards(self):
        e, _ = fixture()
        e['candidates'][0].update(decision='exclude', verification_status='pending')
        e['zero_reason'] = 'verified_exclusions'
        self.assertTrue(validate(e, '', ''))

    def test_empty_inventory(self):
        e, _ = fixture()
        e.update(expected_candidates=[], candidates=[], zero_reason='verified_exclusions')
        self.assertTrue(validate(e, '', ''))

    def test_verified_exclusion_needs_evidence(self):
        e, _ = fixture()
        c = e['candidates'][0]
        c.update(decision='exclude')
        e['zero_reason'] = 'verified_exclusions'
        self.assertTrue(validate(e, '', ''))
        c.update(exclusion_kind='hard_gate', exclusion_evidence='source URL and verified failed metric')
        self.assertEqual(validate(e, '', ''), [])

    def test_missing_candidate(self):
        e, h = fixture()
        e['expected_candidates'].append('crypto_candidate')
        self.assertTrue(validate(e, h, h))

    def test_hard_gates(self):
        for field, value in [('market_cap', 1e10-1), ('pe_ttm', 201), ('pe_ttm', 0),
                             ('pe_ttm', float('nan')), ('profit_ttm', -1), ('latest_profit', -1)]:
            with self.subTest(field=field, value=value):
                e, h = fixture()
                e['candidates'][0][field] = value
                self.assertTrue(validate(e, h, h))

    def test_unavailable_requires_independent_attempts(self):
        e, _ = fixture()
        c = e['candidates'][0]
        c.update(decision='exclude', verification_status='source_unavailable', attempts=[])
        e['zero_reason'] = 'source_unavailable'
        self.assertTrue(validate(e, '', ''))
        c['attempts'] = [dict(url='https://'+host+'/quote', at=e['checked_at'], error='HTTP 403')
                         for host in ('a.example', 'b.example')]
        self.assertEqual(validate(e, '', ''), [])
        e['zero_reason'] = 'verified_exclusions'
        self.assertTrue(validate(e, '', ''))

    def test_bilingual_cards(self):
        e, h = fixture()
        self.assertTrue(validate(e, h, h.replace('600001', '600002')))

    def test_publication_before_check(self):
        e, h = fixture()
        e['publication_at'] = '2026-09-07T10:15:00+08:00'
        self.assertTrue(validate(e, h, h))

    def test_wrong_interval_math(self):
        e, h = fixture()
        e['candidates'][0]['return_5'] = 3.2
        self.assertTrue(validate(e, h, h))

    def test_intraday_endpoint_cannot_replace_prior_close(self):
        e, h = fixture()
        e['candidates'][0]['return_endpoint'] = '2026-09-07'
        self.assertTrue(validate(e, h, h))

    def test_missing_session(self):
        e, h = fixture()
        e['candidates'][0]['sessions'].pop(4)
        self.assertTrue(validate(e, h, h))

    def test_asynchronous_relative_spread(self):
        e, h = fixture()
        e['candidates'][0].update(relative_spread=2.2, benchmark_at='2026-09-07T10:14:00+08:00')
        self.assertTrue(validate(e, h, h))

    def test_undated_current_confirmation(self):
        e, h = fixture()
        e['candidates'][0]['claims_current_confirmation'] = True
        self.assertTrue(validate(e, h, h))


if __name__ == '__main__':
    unittest.main()

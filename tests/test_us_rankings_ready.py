import unittest
from datetime import datetime
from scripts.validate_us_rankings_ready import validate, groups_hash


def snapshot(stamp):
    return {'status': 'ok', 'groups': {name: {'status': 'ok', 'fetchedAt': stamp,
            'top': [{'name': 'Current', 'changePct': '+1%'}], 'bottom': []}
            for name in ('industry', 'concept')}}


class RankingsReadyTests(unittest.TestCase):
    now = datetime.fromisoformat('2026-10-13T08:30:00+08:00')

    def test_previous_friday_snapshot_blocks_tuesday_brief(self):
        self.assertTrue(validate(snapshot('2026-10-10T09:54:00+08:00'), '2026-10-12', self.now))

    def test_on_demand_fresh_capture_passes_before_publication(self):
        self.assertEqual(validate(snapshot('2026-10-13T08:29:00+08:00'), '2026-10-12', self.now), [])

    def test_partial_current_rows_are_allowed(self):
        s = snapshot('2026-10-13T07:20:00+08:00')
        s['status'] = s['groups']['industry']['status'] = 'partial'
        self.assertEqual(validate(s, '2026-10-12', self.now), [])

    def test_last_success_cannot_bypass_gate(self):
        s = snapshot('2026-10-13T07:20:00+08:00')
        s['groups']['concept'].update(status='error', top=[], lastSuccess={'top': [{'name': 'Old'}]})
        self.assertTrue(validate(s, '2026-10-12', self.now))

    def test_future_and_timezone_free_quotes_do_not_pass(self):
        for stamp in ('2026-10-13T11:10:00+08:00', '2026-10-13T07:20:00'):
            with self.subTest(stamp=stamp):
                self.assertTrue(validate(snapshot(stamp), '2026-10-12', self.now))

    def test_exchange_holiday_expected_session_can_be_supplied(self):
        # Caller verifies the exchange calendar; a Monday closure requires Friday's session.
        self.assertEqual(validate(snapshot('2026-09-08T07:20:00+08:00'), '2026-09-04',
                         datetime.fromisoformat('2026-09-08T08:30:00+08:00')), [])

    def test_gate_hash_changes_when_rows_change(self):
        s = snapshot('2026-10-13T07:20:00+08:00')
        before = groups_hash(s)
        s['groups']['industry']['top'][0]['changePct'] = '+2%'
        self.assertNotEqual(before, groups_hash(s))


if __name__ == '__main__':
    unittest.main()

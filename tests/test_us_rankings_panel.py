import unittest
from datetime import datetime
from scripts.update_us_rankings_panel import update_html


def snapshot(stamp='2026-10-13T11:10:12+08:00'):
    row = {'name': '医疗设备', 'nameEn': 'Medical Devices', 'changePct': '+2.06%', 'leaderTicker': 'PMI'}
    return {'groups': {name: {'status': 'partial', 'fetchedAt': stamp, 'top': [row], 'bottom': []}
                       for name in ('industry', 'concept')}}


class RankingsPanelTests(unittest.TestCase):
    def setUp(self):
        self.html = ('protected brief<!-- US_SECTOR_PANEL_START -->old<!-- US_SECTOR_PANEL_END -->'
                     'protected script<!-- US_SECTOR_PANEL_EN_START -->old<!-- US_SECTOR_PANEL_EN_END -->footer')
        self.now = datetime.fromisoformat('2026-10-13T11:11:00+08:00')

    def test_late_success_replaces_empty_panels_in_both_languages(self):
        updated = update_html(self.html, snapshot(), self.now)
        self.assertEqual(updated.count('class="spark-row"'), 4)
        self.assertIn('医疗设备', updated)
        self.assertIn('Medical Devices', updated)
        self.assertIn('2026-10-12 23:10 EDT', updated)
        self.assertTrue(updated.startswith('protected brief'))
        self.assertTrue(updated.endswith('footer'))
        self.assertIn('protected script', updated)

    def test_saturday_snapshot_cannot_fill_tuesday_rankings(self):
        updated = update_html(self.html, snapshot('2026-10-10T09:54:00+08:00'), self.now)
        self.assertNotIn('class="spark-row"', updated)
        self.assertIn('等待最新快照', updated)

    def test_weekend_keeps_friday_capture(self):
        updated = update_html(self.html, snapshot('2026-10-10T09:54:00+08:00'),
                              datetime.fromisoformat('2026-10-12T08:30:00+08:00'))
        self.assertEqual(updated.count('class="spark-row"'), 4)

    def test_failed_source_never_reuses_last_success(self):
        data = snapshot()
        data['groups']['industry'].update(status='error', lastSuccess={'top': data['groups']['industry']['top']})
        updated = update_html(self.html, data, self.now)
        self.assertEqual(updated.count('class="spark-row"'), 2)

    def test_source_names_are_escaped_and_markers_are_required(self):
        data = snapshot()
        data['groups']['industry']['top'][0]['name'] = '<script>bad</script>'
        self.assertNotIn('<script>bad', update_html(self.html, data, self.now))
        with self.assertRaises(ValueError):
            update_html('missing markers', data, self.now)


if __name__ == '__main__':
    unittest.main()

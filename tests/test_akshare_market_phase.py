import unittest
from datetime import datetime, date
from zoneinfo import ZoneInfo

from scripts.fetch_akshare_snapshot import latest_session, market_phase


class MarketPhaseTests(unittest.TestCase):
    def test_holiday_refresh_keeps_prior_close_date(self):
        sessions = ['2026-09-24', '2026-09-28']
        now = datetime(2026, 9, 25, 12, 59, tzinfo=ZoneInfo('Asia/Shanghai'))
        market_date = latest_session(sessions, now.date())
        self.assertEqual(market_date, '2026-09-24')
        self.assertEqual(market_phase(now, 15, market_date == now.date().isoformat()),
                         'previous_close_baseline')

    def test_trading_day_intraday_and_preopen(self):
        sessions = ['2026-09-24', '2026-09-28']
        day = date(2026, 9, 28)
        self.assertEqual(latest_session(sessions, day), day.isoformat())
        for hour, minute, expected in [(8, 20, 'previous_close_baseline'),
                                       (10, 0, 'intraday_snapshot')]:
            now = datetime(2026, 9, 28, hour, minute, tzinfo=ZoneInfo('Asia/Shanghai'))
            self.assertEqual(market_phase(now, 15, True), expected)


if __name__ == '__main__':
    unittest.main()

import unittest
from datetime import datetime

from scripts.validate_ah_run_state import validate


BASE = {
    "run_id": "ah-20260910-test",
    "owner": "test",
    "status": "running",
    "heartbeat_at": "2026-09-10T09:00:00+08:00",
    "lease_until": "2026-09-10T09:10:00+08:00",
    "published_commit": None,
}


class RunStateTests(unittest.TestCase):
    def test_valid_running(self):
        self.assertEqual(validate(dict(BASE), datetime.fromisoformat("2026-09-10T09:05:00+08:00")), [])

    def test_expired_running_requires_resolution(self):
        errors = validate(dict(BASE), datetime.fromisoformat("2026-09-10T09:11:00+08:00"))
        self.assertTrue(any("expired" in error for error in errors))

    def test_valid_published_releases_lease(self):
        state = dict(BASE, status="published", published_commit="a" * 40,
                     lease_until=BASE["heartbeat_at"])
        self.assertEqual(validate(state), [])

    def test_blocked_requires_structured_error(self):
        state = dict(BASE, status="blocked", lease_until=BASE["heartbeat_at"])
        self.assertTrue(any("error object" in error for error in validate(state)))

    def test_deployment_block_keeps_commit(self):
        state = dict(
            BASE,
            status="blocked",
            published_commit="b" * 40,
            lease_until=BASE["heartbeat_at"],
            error={
                "stage": "deployment_verification",
                "code": "deployment_not_ready",
                "message": "production still serves the previous A/H entry",
                "recoverable_stage": "deployment_verification",
                "occurred_at": "2026-09-10T09:20:00+08:00",
            },
        )
        self.assertEqual(validate(state), [])


if __name__ == "__main__":
    unittest.main()

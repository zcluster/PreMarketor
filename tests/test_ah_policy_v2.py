import json
import unittest
from pathlib import Path

RULES_PATH = Path(__file__).resolve().parents[1] / "brief_rules.md"
START = "<!-- AH_AUTOMATION_POLICY_V2_START -->"
END = "<!-- AH_AUTOMATION_POLICY_V2_END -->"

CORE_CHECKS = (
    "traceable_sources",
    "material_us_to_ah_mapping",
    "marker_whitelist",
    "atomic_publish",
    "bilingual_archive_consistency",
)


def load_policy():
    text = RULES_PATH.read_text(encoding="utf-8")
    payload = text.split(START, 1)[1].split(END, 1)[0].strip()
    return json.loads(payload)


def publication_allowed(policy, evidence):
    if evidence.get("negative_signal_packaged_as_long", False):
        return False
    return all(evidence.get(name, False) for name in CORE_CHECKS)


class AHPolicyV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = load_policy()

    def core_evidence(self):
        return {name: True for name in CORE_CHECKS}

    def test_schedule_labels_match_current_ah_jobs(self):
        self.assertEqual(self.policy["first_run_time"], "08:30 Asia/Shanghai")
        self.assertEqual(self.policy["incremental_review_time"], "09:15 Asia/Shanghai")

    def test_removed_legacy_gates_are_disabled(self):
        for name in (
            "require_exhaustive_hk_announcements",
            "require_21_session_history",
            "require_5_20_day_returns",
            "require_market_cap_profit_pe_thresholds",
            "require_legacy_stock_validator",
            "require_browser_acceptance",
        ):
            with self.subTest(name=name):
                self.assertIs(self.policy[name], False)

    def test_missing_legacy_inputs_do_not_block_publication(self):
        evidence = self.core_evidence()
        evidence.update(
            hkex_full_ledger=None,
            trading_sessions=None,
            returns_5d=None,
            returns_20d=None,
            market_cap=None,
            profit_ttm=None,
            pe_ttm=None,
            browser_available=False,
        )
        self.assertTrue(publication_allowed(self.policy, evidence))

    def test_retained_safety_contracts_still_block(self):
        for missing in CORE_CHECKS:
            evidence = self.core_evidence()
            evidence[missing] = False
            with self.subTest(missing=missing):
                self.assertFalse(publication_allowed(self.policy, evidence))

        evidence = self.core_evidence()
        evidence["negative_signal_packaged_as_long"] = True
        self.assertFalse(publication_allowed(self.policy, evidence))


if __name__ == "__main__":
    unittest.main()

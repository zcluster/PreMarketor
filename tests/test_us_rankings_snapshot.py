import importlib.util
import json
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "fetch_us_rankings_snapshot.py"
SPEC = importlib.util.spec_from_file_location("us_rankings", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def row(name, change):
    return {
        "plateName": name,
        "plateEnName": f"{name} EN",
        "plateCode": f"BK{name}",
        "changeRatio": change,
        "stockName": "Leader",
        "stockCode": "TEST",
        "stockChangeRatio": "+1.00%",
        "priceRiseCount": 2,
        "priceFallCount": 1,
        "priceSameCount": 0,
    }


class USRankingsSnapshotTest(unittest.TestCase):
    def test_extracts_hydration_json(self):
        payload = {"sparks_index": {"list": [row("A", "+2.00%")]}}
        html = f"<script>window.__INITIAL_STATE__={json.dumps(payload)};</script>"
        self.assertEqual(MODULE.extract_initial_state(html), payload)

    def test_selects_only_required_rankings(self):
        rows = [row(str(index), f"{change:+.2f}%") for index, change in enumerate([3, 2, 1, .5, .1, -.1, -.5, -1, -2, -3, -4])]
        self.assertEqual([item["changePct"] for item in MODULE.positive_top(rows)], ["+3.00%", "+2.00%", "+1.00%", "+0.50%", "+0.10%"])
        self.assertEqual([item["changePct"] for item in MODULE.negative_bottom(rows)], ["-0.50%", "-1.00%", "-2.00%", "-3.00%", "-4.00%"])

    def test_retains_previous_success_separately(self):
        previous = {"groups": {"concept": {"status": "ok", "fetchedAt": "old", "top": [{"name": "A"}], "bottom": []}}}
        retained = MODULE.previous_success(previous, "concept")
        self.assertEqual(retained["fetchedAt"], "old")
        self.assertEqual(retained["top"], [{"name": "A"}])

    def test_partial_rows_require_name_and_change_only(self):
        snapshot = {
            "schemaVersion": 1,
            "groups": {
                "industry": {"status": "partial", "top": [{"name": "A", "changePct": "+1%"}], "bottom": []},
                "concept": {"status": "partial", "top": [{"name": "B", "changePct": "+2%"}], "bottom": []},
            },
        }
        MODULE.validate(snapshot)


if __name__ == "__main__":
    unittest.main()

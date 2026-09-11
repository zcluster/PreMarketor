import json
import unittest
from pathlib import Path

RULES_PATH = Path(__file__).resolve().parents[1] / "brief_rules.md"
POLICY_START = "<!-- AH_AUTOMATION_POLICY_V2_START -->"
POLICY_END = "<!-- AH_AUTOMATION_POLICY_V2_END -->"


def load_contract():
    rules = RULES_PATH.read_text(encoding="utf-8")
    payload = rules.split(POLICY_START, 1)[1].split(POLICY_END, 1)[0].strip()
    return rules, json.loads(payload)


class AHPolicyV2ContractTest(unittest.TestCase):
    """Static contract tests for brief_rules.md, not an end-to-end publisher test."""

    @classmethod
    def setUpClass(cls):
        cls.rules, cls.policy = load_contract()

    def test_schedule_labels_match_current_ah_jobs(self):
        self.assertEqual(self.policy["first_run_time"], "08:30 Asia/Shanghai")
        self.assertEqual(self.policy["incremental_review_time"], "09:15 Asia/Shanghai")

    def test_cancelled_requirements_are_explicitly_disabled(self):
        cancelled = (
            "require_full_hkex_ledger",
            "require_exhaustive_hk_announcements",
            "require_21_session_history",
            "require_5_20_day_returns",
            "require_market_cap_profit_pe_thresholds",
            "require_legacy_stock_validator",
            "require_browser_acceptance",
        )
        for name in cancelled:
            with self.subTest(name=name):
                self.assertIn(name, self.policy)
                self.assertIs(self.policy[name], False)

    def test_retained_safety_contracts_are_explicitly_enabled(self):
        retained = (
            "require_ranked_major_movement_reconciliation",
            "require_traceable_sources",
            "require_material_us_to_ah_mapping",
            "forbid_negative_signal_as_long_pick",
            "allow_conditional_watch_and_avoid_cards",
            "forbid_quote_gap_as_sole_card_exclusion",
            "require_marker_whitelist",
            "require_atomic_publish",
            "require_bilingual_archive_consistency",
        )
        for name in retained:
            with self.subTest(name=name):
                self.assertIn(name, self.policy)
                self.assertIs(self.policy[name], True)

    def test_ranked_major_movements_must_be_reconciled(self):
        required_text = (
            "行业 Top5/Bottom5、概念 Top5",
            "任一榜单前两名",
            "板块涨跌幅绝对值不低于 5%",
            "同一主题占概念 Top5 至少 2 席",
            "业务映射核验 → 条件关注/看多候选/回避/无候选 → 状态理由",
            "不得只检查正文已经选择的主题",
            "加密货币等显著大涨主题",
            "全部重大主题的 decision 必须属于 conditional_watch|bullish_candidate|avoid|no_candidate 且无 pending",
            "不扩大榜单抓取",
        )
        for text in required_text:
            with self.subTest(text=text):
                self.assertIn(text, self.rules)

    def test_legacy_publish_gates_are_not_reintroduced(self):
        forbidden_text = (
            "scripts/hk_coverage_ledger.py",
            "scripts/validate_stock_screening.py",
            "total_market_cap >= 10000000000",
            "0 < PE_TTM <= 200",
            "连续21个收盘日",
        )
        for text in forbidden_text:
            with self.subTest(text=text):
                self.assertNotIn(text, self.rules)
        self.assertIn("真实浏览器不是发布前置", self.rules)

    def test_candidate_card_states_and_quote_gaps(self):
        required_text = (
            "条件关注/Conditional Watch",
            "看多候选/Bullish Candidate",
            "回避/Avoid",
            "decision=conditional_watch|bullish_candidate|avoid|no_candidate",
            "不得单独据此排除候选或清空卡片",
            "不得设置统一实时报价新门槛",
            "0 卡仅允许用于本轮没有任何可核验业务或事件依据",
            "普通融资、审批或交付风险就自动排除",
        )
        for text in required_text:
            with self.subTest(text=text):
                self.assertIn(text, self.rules)
        self.assertNotIn("decision=include|exclude", self.rules)
        self.assertNotIn("拟推荐股仍须取得最新可得价格反馈", self.rules)
        self.assertIn("对拟展示的候选必须尝试取得最新可得价格反馈", self.rules)
        self.assertIn("不得仅因报价缺口删除卡片", self.rules)
        self.assertIn("contract tests", self.__class__.__doc__)
        self.assertIn("not an end-to-end", self.__class__.__doc__)

    def test_failure_section_is_unique(self):
        self.assertEqual(self.rules.count("## 失败处理与阻塞条件"), 1)


if __name__ == "__main__":
    unittest.main()

"""算法 02/03 文档合同与人造反例验证。

本脚本不连接生产数据库，只验证文档合同、关键边界和可复算样例，不能代替真实数据验收。
运行：python3 examples/synthetic_data/validate_algo02_03_linkage.py
"""

from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from pathlib import Path
import random
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[2]
D2 = "04_algorithm_cards/developer_version/算法卡_02_门店品类等级.md"
D3 = "04_algorithm_cards/developer_version/算法卡_03_门店群消费者画像贡献.md"
B2 = "04_algorithm_cards/business_readable/算法02_门店品类等级_业务解读版.md"
B3 = "04_algorithm_cards/business_readable/算法03_门店群消费者画像贡献_业务解读版.md"
CITY_SNAPSHOT = (
    "03_data_contracts/base_tables/"
    "dim_algorithm_batch_city_region_snapshot_统一算法批次城市区域映射快照表.md"
)
D = Decimal


def contribution(counts, amounts):
    """按会员占比和销售占比的调和平均计算贡献得分。"""
    with localcontext() as ctx:
        ctx.prec, ctx.rounding = 50, ROUND_HALF_EVEN
        member_total = sum(counts)
        sales_total = sum(map(D, amounts))
        if member_total <= 0 or sales_total <= 0:
            raise ValueError("empty denominator")
        result = []
        for member_cnt, sales_amt in zip(counts, amounts):
            member_share = D(member_cnt) / member_total
            sales_share = D(sales_amt) / sales_total
            result.append(
                2 * sales_share * member_share / (sales_share + member_share) * 100
            )
        return result


def jenks(values):
    """Decimal50 参考计算；排序序号仅用于人造测试。"""
    with localcontext() as ctx:
        ctx.prec, ctx.rounding = 50, ROUND_HALF_EVEN
        vals = sorted(map(D, values))
        if not vals:
            raise ValueError("no profiles")
        if len(vals) == 1:
            return {
                "k": 1,
                "high": [True],
                "break": None,
                "sse": {},
                "bic": {},
                "status": "SINGLE_PROFILE",
            }

        def sse(items):
            mean = sum(items) / len(items)
            return sum((item - mean) ** 2 for item in items)

        sse_k1 = sse(vals)
        candidates = [
            (sse(vals[:index]) + sse(vals[index:]), vals[index], index)
            for index in range(1, len(vals))
            if vals[index - 1] != vals[index]
        ]
        best = min(candidates, key=lambda item: (item[0], -item[1])) if candidates else None
        sse_by_k = {1: sse_k1}
        if best:
            sse_by_k[2] = best[0]
        bic_by_k = {
            k: D(len(vals)) * (value / len(vals) + D("1e-12")).ln()
            + D(k) * D(len(vals)).ln()
            for k, value in sse_by_k.items()
        }
        selected_k = min(bic_by_k, key=lambda k: (bic_by_k[k], k))
        return {
            "k": selected_k,
            "high": [selected_k == 2 and item >= best[1] for item in vals],
            "break": best[1] if selected_k == 2 else None,
            "candidate_break": best[1] if best else None,
            "sse": sse_by_k,
            "bic": bic_by_k,
            "status": "SUCCESS" if selected_k == 2 else "NO_OBVIOUS_MAIN",
        }


def rating_group_gate(release, rows):
    """用最小发布记录和正式结果行判断算法 03 是否可读。"""
    if not release or release.get("release_status") != "AUTO_PUBLISHED":
        return "BLOCKED"
    if not rows or any(row.get("run_id") != release.get("latest_run_id") for row in rows):
        return "BLOCKED"
    if any(row.get("source_data_version") != release.get("source_data_version") for row in rows):
        return "BLOCKED"
    group_reasons = {
        reason
        for row in rows
        for reason in row.get("degraded_reason", [])
    }
    if group_reasons & {"GROUP_SOURCE_GAP", "GROUP_RELIABILITY_UNVERIFIED"}:
        return "BLOCKED"
    if release.get("rating_population_completeness_status") == "PASSED":
        counts_match = (
            release.get("expected_key_missing_result_cnt") == 0
            and release.get("unexpected_result_key_cnt") == 0
            and release.get("expected_rating_key_cnt")
            == release.get("result_rating_key_cnt")
        )
        return "AVAILABLE" if counts_match else "BLOCKED"
    return "UNAVAILABLE"


def operating_days(rows):
    """rows: (日期, 历史营业, 可售, 源完整, 销售额)。"""
    if len({row[0] for row in rows}) != len(rows):
        raise ValueError("duplicate store date")
    if any(row[1] is None or row[2] is None for row in rows):
        return None, None, None, None
    potential = [row for row in rows if row[1] and row[2]]
    valid = [row for row in potential if row[3]]
    sales_total = sum(D(row[4]) for row in valid)
    return (
        len(potential),
        len(potential) - len(valid),
        len(valid),
        sales_total / len(valid) if valid else None,
    )


def group_total(rows):
    values = {D(row["group_sales_amt"]) for row in rows}
    if len(values) != 1:
        raise ValueError("inconsistent repeated group totals")
    return next(iter(values))


def bootstrap_fields(status, completed):
    if status == "NOT_APPLICABLE":
        return 0, D(1), D(1), D(1), D(0)
    if status == "FAILED":
        return completed, None, None, None, None
    raise ValueError("fixture supports boundary states only")


def deterministic_draw(members, count, seed=20260723):
    rng = random.Random(seed)
    ordered = sorted(members, key=lambda item: item.encode("utf-8"))
    return [ordered[rng.randrange(len(ordered))] for _ in range(count)]


def publication(rows):
    return (
        bool(rows)
        and all(flag == 1 and published_at for flag, published_at in rows)
        and len({published_at for flag, published_at in rows}) == 1
    )


class SyntheticRules(unittest.TestCase):
    def setUp(self):
        self.release = {
            "release_status": "AUTO_PUBLISHED",
            "latest_run_id": "r1",
            "source_data_version": "src1",
            "rating_population_completeness_status": "PASSED",
            "expected_rating_key_cnt": 2,
            "result_rating_key_cnt": 2,
            "expected_key_missing_result_cnt": 0,
            "unexpected_result_key_cnt": 0,
        }
        self.rows = [
            {
                "run_id": "r1",
                "source_data_version": "src1",
                "result_status": "SUCCESS",
                "degraded_reason": [],
            },
            {
                "run_id": "r1",
                "source_data_version": "src1",
                "result_status": "SUCCESS",
                "degraded_reason": [],
            },
        ]

    def test_complete_group(self):
        self.assertEqual(rating_group_gate(self.release, self.rows), "AVAILABLE")

    def test_coverage_only_unavailable(self):
        release = dict(self.release, rating_population_completeness_status="UNAVAILABLE")
        self.assertEqual(rating_group_gate(release, self.rows), "UNAVAILABLE")

    def test_group_source_gap_blocks(self):
        rows = [dict(self.rows[0], degraded_reason=["GROUP_SOURCE_GAP"]), self.rows[1]]
        self.assertEqual(rating_group_gate(self.release, rows), "BLOCKED")

    def test_group_reliability_unverified_blocks(self):
        rows = [
            dict(self.rows[0], degraded_reason=["GROUP_RELIABILITY_UNVERIFIED"]),
            self.rows[1],
        ]
        self.assertEqual(rating_group_gate(self.release, rows), "BLOCKED")

    def test_release_count_mismatch_blocks(self):
        release = dict(self.release, expected_rating_key_cnt=3)
        self.assertEqual(rating_group_gate(release, self.rows), "BLOCKED")

    def test_stale_run_blocks(self):
        rows = [dict(row, run_id="r0") for row in self.rows]
        self.assertEqual(rating_group_gate(self.release, rows), "BLOCKED")

    def test_source_data_version_mismatch_blocks(self):
        rows = [dict(self.rows[0], source_data_version="src2"), self.rows[1]]
        self.assertEqual(rating_group_gate(self.release, rows), "BLOCKED")

    def test_historical_daily_state(self):
        rows = [("d1", True, True, True, "100"), ("d2", False, True, True, "200")]
        self.assertEqual(operating_days(rows), (1, 0, 1, D(100)))

    def test_real_zero_sales_in_denominator(self):
        rows = [("d1", True, True, True, "100"), ("d2", True, True, True, "0")]
        self.assertEqual(operating_days(rows), (2, 0, 2, D(50)))

    def test_missing_day_removed_from_numerator_and_denominator(self):
        rows = [(str(index), True, True, index != 1, "100") for index in range(3)]
        self.assertEqual(operating_days(rows), (3, 1, 2, D(100)))

    def test_unknown_operating_or_saleable_population_is_not_zero(self):
        self.assertEqual(operating_days([("d1", True, None, False, "0")]), (None,) * 4)
        self.assertEqual(operating_days([("d1", None, True, True, "100")]), (None,) * 4)

    def test_duplicate_historical_day_blocks_join(self):
        with self.assertRaises(ValueError):
            operating_days([("d", True, True, True, "1")] * 2)

    def test_precision_can_change_partition(self):
        scores = contribution([5000, 5000], ["500000.10", "499999.90"])
        shown = [score.quantize(D("0.0001"), rounding=ROUND_HALF_EVEN) for score in scores]
        self.assertEqual(shown, [D("50.0000"), D("50.0000")])
        self.assertNotEqual(scores[0], scores[1])
        self.assertEqual(jenks(scores)["k"], 2)
        self.assertEqual(jenks(shown)["k"], 1)

    def test_tied_sse_uses_higher_break(self):
        self.assertEqual(jenks(["10", "20", "30"])["candidate_break"], D(30))

    def test_equal_scores_not_split(self):
        self.assertEqual(jenks(["10", "10", "20", "20"])["high"], [False, False, True, True])

    def test_normal_k1_retains_sse_bic(self):
        result = jenks(["50", "50"])
        self.assertEqual(result["status"], "NO_OBVIOUS_MAIN")
        self.assertEqual(result["sse"][1], 0)
        self.assertIn(1, result["bic"])
        self.assertIsNone(result["break"])

    def test_single_profile_no_fake_bic(self):
        self.assertEqual(jenks(["100"])["bic"], {})

    def test_summary_repeated_total_take_once(self):
        self.assertEqual(group_total([{"group_sales_amt": "100"}] * 2), D(100))

    def test_summary_inconsistency_blocks(self):
        with self.assertRaises(ValueError):
            group_total([{"group_sales_amt": "100"}, {"group_sales_amt": "200"}])

    def test_bootstrap_failure_null_not_zero(self):
        self.assertEqual(bootstrap_fields("FAILED", 27), (27, None, None, None, None))

    def test_single_profile_bootstrap_boundary(self):
        self.assertEqual(
            bootstrap_fields("NOT_APPLICABLE", 0),
            (0, D(1), D(1), D(1), D(0)),
        )

    def test_reproducible_bootstrap_uses_fixed_seed_and_sorted_members(self):
        first = deterministic_draw(["m2", "m1"], 100)
        second = deterministic_draw(["m1", "m2"], 100)
        self.assertEqual(first, second)

    def test_algorithm_01_publication_rows_all_agree(self):
        self.assertTrue(publication([(1, "t"), (1, "t")]))
        invalid = [[], [(1, "t"), (0, "t")], [(1, "t"), (1, None)], [(1, "t"), (1, "t2")]]
        for rows in invalid:
            self.assertFalse(publication(rows))


class DocumentContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        paths = (D2, D3, B2, B3, CITY_SNAPSHOT)
        cls.texts = {path: (ROOT / path).read_text() for path in paths}
        cls.d2 = cls.texts[D2]
        cls.d3 = cls.texts[D3]

    def test_fences_closed(self):
        for path, content in self.texts.items():
            opened = None
            for line in content.splitlines():
                match = re.match(r"^(`{3,}|~{3,})(.*)$", line)
                if match:
                    if opened is None:
                        opened = match.group(1)
                    elif match.group(1)[0] == opened[0] and not match.group(2).strip():
                        opened = None
            self.assertIsNone(opened, path)

    def test_no_removed_source_table(self):
        for path, content in self.texts.items():
            self.assertNotRegex(content, r"dws_member_order_item_detail_df_all(?!_new)", path)

    def test_no_removed_technical_contracts(self):
        banned = (
            "run_config_snapshot_json",
            "model_manifest_digest",
            "rule_sql_digest",
            "param_source_digest",
            "candidate_manifest_digest",
            "code_release_id",
            "algorithm_logic_version",
            "category_read_binding_json",
            "store_history_read_binding_json",
            "rating_population_evidence_json",
            "rating_group_evidence_json",
            "mart_store_category_level_run_param",
            "mart_store_category_level_discount_param",
            "mart_store_category_level_run_quality_issue",
            "mart_store_category_level_param_publish_audit",
        )
        for path in (D2, D3, B2, B3):
            for token in banned:
                self.assertNotIn(token, self.texts[path], f"{path}: {token}")

    def test_algorithm_02_minimal_stable_tables(self):
        expected = (
            "mart_store_category_level",
            "mart_store_category_level_sell_through_param",
            "mart_store_category_level_loss_threshold_param",
            "mart_store_category_level_run_release",
        )
        for table in expected:
            self.assertIn(table, self.d2)
        removed = (
            "mart_store_category_level_metric_detail",
            "mart_store_category_level_standard_param",
            "mart_store_category_level_critic_weight",
            "mart_store_category_level_critic_corr",
            "mart_store_category_level_segment_param",
        )
        for table in removed:
            self.assertNotIn(table, self.d2)

    def test_algorithm_03_keeps_two_formal_outputs_only(self):
        for table in (
            "mart_store_group_consumer_contribution",
            "mart_store_group_consumer_summary",
        ):
            self.assertIn(table, self.d3)
        self.assertIn("不新增算法 03 独立运行参数表", self.d3)

    def test_shared_city_snapshot_contract(self):
        snapshot = self.texts[CITY_SNAPSHOT]
        self.assertIn("algorithm_batch_version + city", snapshot)
        self.assertIn("effective_end_date >= calculation_end_date", snapshot)
        self.assertIn("is_active（是否当前有效）", snapshot)
        self.assertIn("不用于回算历史批次", snapshot)

    def test_source_data_version_boundary_is_explicit(self):
        for content in (self.d2, self.d3):
            self.assertIn("调度系统", content)
            self.assertIn("source_data_version（源数据版本）", content)
            self.assertIn("不要求算法 01 正式结果新增字段或表", content)

    def test_q1_candidate_window_timing_is_closed(self):
        for token in ("30 / 60 / 90", "全部候选统一", "入选窗口"):
            self.assertIn(token, self.d2)

    def test_q2_promotion_scope_is_fixed(self):
        self.assertIn("promotion_discount_scope（促销折扣口径）", self.d2)
        self.assertIn("TOTAL_DISCOUNT_INCL_TIME（总折扣已包含时段折扣）", self.d2)
        self.assertIn("不设人工登记或审批", self.d2)

    def test_q3_four_retained_metrics_are_formal_fields(self):
        for field in (
            "daily_valid_member_ticket_cnt",
            "valid_member_sales_amt",
            "valid_member_sales_ratio",
            "valid_member_ticket_ratio",
        ):
            self.assertRegex(self.d2, rf"(?m)^\| [^|]+ \| `{field}` \|", field)

    def test_output_fields_use_six_column_contract(self):
        outputs = (
            self.d2.split("## 14. 输出表结构", 1)[1],
            self.d3.split("## 15. 输出字段", 1)[1],
            self.texts[CITY_SNAPSHOT].split("## 5. 完整字段合同", 1)[1],
        )
        header = "| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |"
        for content in outputs:
            in_fields = False
            for line in content.splitlines():
                if line.startswith("| 中文字段名"):
                    self.assertEqual(line, header)
                    in_fields = True
                elif in_fields and line.startswith("|"):
                    self.assertEqual(len(line.strip("|").split("|")), 6, line)
                else:
                    in_fields = False

    def test_formal_output_requirement_is_not_advisory(self):
        d2_output = self.d2.split("## 14. 输出表结构", 1)[1]
        d3_output = self.d3.split("## 15. 输出字段", 1)[1]
        self.assertNotIn("| 建议 |", d2_output)
        self.assertNotIn("| 建议 |", d3_output)

    def test_formal_tables_have_no_duplicate_fields(self):
        sections = {
            "algo02_result": self.d2.split("## 14. 输出表结构", 1)[1].split("## 15.", 1)[0],
            "algo02_release": self.d2.split("表名：`mart_store_category_level_run_release`", 1)[1].split("### 15.1", 1)[0],
            "algo02_sell_param": self.d2.split("表名：`mart_store_category_level_sell_through_param`", 1)[1].split("### 15.2", 1)[0],
            "algo02_loss_param": self.d2.split("表名：`mart_store_category_level_loss_threshold_param`", 1)[1].split("### 15.3", 1)[0],
            "algo03_detail": self.d3.split("## 15. 输出字段", 1)[1].split("## 16.", 1)[0],
            "algo03_summary": self.d3.split("## 16. 输出字段", 1)[1].split("### 16.1", 1)[0],
            "city_snapshot": self.texts[CITY_SNAPSHOT].split("## 5. 完整字段合同", 1)[1].split("## 6.", 1)[0],
        }
        for name, content in sections.items():
            fields = re.findall(r"^\| [^|]+ \| `([a-z0-9_]+)` \|", content, re.M)
            self.assertTrue(fields, name)
            duplicates = sorted({field for field in fields if fields.count(field) > 1})
            self.assertEqual(duplicates, [], name)

    def test_all_stable_table_keys_use_unified_batch(self):
        required_key_fragments = (
            "algorithm_batch_version\nscope_type\nscope_id\nstore_id",
            "algorithm_code + algorithm_batch_version",
            "algorithm_batch_version + scope_type + scope_id + category_granularity + category_code + measurement_type",
            "algorithm_batch_version + scope_type + scope_id + category_granularity + category_code + loss_trigger_month_count",
            "algorithm_batch_version\nscope_type\nscope_id\ncategory_granularity\ncategory_code\nstore_group_type",
            "algorithm_batch_version + city",
        )
        joined = self.d2 + self.d3 + self.texts[CITY_SNAPSHOT]
        for fragment in required_key_fragments:
            self.assertIn(fragment, joined, fragment)

    def test_result_enum_fields_have_constraint_rows(self):
        for content, start in (
            (self.d2, "## 14. 输出表结构"),
            (self.d3, "## 15. 输出字段"),
        ):
            output = content.split(start, 1)[1]
            names = re.findall(
                r"^\| [^|]+ \| `([a-z_]+)` \| (?:varchar|tinyint|int)",
                output,
                re.M,
            )
            enums = [name for name in names if name.endswith(("_status", "_flag", "_method"))]
            for name in enums:
                self.assertRegex(content, rf"(?m)^\| `{re.escape(name)}` \|", name)

    def test_unified_batch_is_the_only_business_version(self):
        for path in (D2, D3, B2, B3):
            self.assertIn("algorithm_batch_version", self.texts[path])
        independent = re.compile(
            r"profile_model_version|category_level_model_version|consumer_contribution_model_version|"
            r"category_mapping_version|scope_version|rule_version|parameter_version|price_version|batch_seq"
        )
        for path in (D2, D3, B2, B3):
            for line in self.texts[path].splitlines():
                if independent.search(line):
                    self.assertTrue(
                        "不生成" in line or "不得" in line or "不能生成或引用" in line,
                        f"{path}: {line}",
                    )

    def test_no_manual_approval_dependency(self):
        positive_dependency = re.compile(r"APPROVED|待审核|审批后|确认后才能|手工点击")
        for path in (D2, D3, B2, B3):
            for line in self.texts[path].splitlines():
                if positive_dependency.search(line):
                    self.assertTrue(
                        any(token in line for token in ("不存在", "不需要", "不依赖", "不得", "不等待")),
                        f"{path}: {line}",
                    )

    def test_algorithm_03_fixed_bootstrap_seed(self):
        self.assertIn("bootstrap_random_seed（Bootstrap 随机种子）", self.d3)
        self.assertIn("20260723", self.d3)
        self.assertIn("不再按范围、品类或门店等级派生第二个种子", self.d3)

    def test_algorithm_03_business_json_outputs_preserved(self):
        for field in (
            "sse_by_k_json",
            "bic_by_k_json",
            "main_profiles_json",
            "relative_main_candidates_json",
            "quality_metrics_json",
        ):
            self.assertIn(field, self.d3)

    def test_developer_and_business_statuses_align(self):
        for token in ("SUCCESS", "NOT_CALCULABLE", "AUTO_PUBLISHED"):
            self.assertIn(token, self.d2)
            self.assertIn(token, self.texts[B2])
        for token in (
            "SUCCESS",
            "SINGLE_PROFILE",
            "NO_OBVIOUS_MAIN",
            "GROUP_SOURCE_GAP",
            "GROUP_RELIABILITY_UNVERIFIED",
        ):
            self.assertIn(token, self.d3)
            self.assertIn(token, self.texts[B3])

    def test_core_business_methods_retained(self):
        for token in (
            "CRITIC",
            "Jenks",
            "BIC",
            "Bootstrap",
            "Isotonic Regression",
            "promotion_health_score",
            "loss_health_score",
        ):
            self.assertTrue(token in self.d2 or token in self.d3, token)

    def test_original_real_sample_acceptance_preserved(self):
        for content in (self.d3, self.texts[B3]):
            self.assertIn("至少 30 个门店群结果", content)

    def test_git_whitespace(self):
        subprocess.check_call(["git", "diff", "--check"], cwd=ROOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""02/03 文档合同与人造反例验证。非生产算法，不连接数据库，不代表真实数据验收。
运行：python3 examples/synthetic_data/validate_algo02_03_linkage.py
"""
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
from pathlib import Path
import hashlib
import json
import random
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
D2 = "04_algorithm_cards/developer_version/算法卡_02_门店品类等级.md"
D3 = "04_algorithm_cards/developer_version/算法卡_03_门店群消费者画像贡献.md"
B2 = "04_algorithm_cards/business_readable/算法02_门店品类等级_业务解读版.md"
B3 = "04_algorithm_cards/business_readable/算法03_门店群消费者画像贡献_业务解读版.md"
D = Decimal
ZERO_KEYS = (
    "source_missing_store_day_cnt", "unmapped_store_source_record_cnt",
    "unmapped_scope_source_record_cnt", "unmapped_category_source_record_cnt",
    "expected_key_missing_result_cnt", "unexpected_result_key_cnt",
)


def contribution(counts, amounts):
    with localcontext() as ctx:
        ctx.prec, ctx.rounding = 50, ROUND_HALF_EVEN
        n, total = sum(counts), sum(map(D, amounts))
        if n <= 0 or total <= 0:
            raise ValueError("empty denominator")
        values = []
        for count, amt in zip(counts, amounts):
            m, a = D(count) / n, D(amt) / total
            values.append(2 * a * m / (a + m) * 100)
        return values


def jenks(values):
    """Decimal50 参考计算；排序后的序号仅用于人造测试，不是业务排名。"""
    with localcontext() as ctx:
        ctx.prec, ctx.rounding = 50, ROUND_HALF_EVEN
        vals = sorted(map(D, values))
        n = len(vals)
        if not n:
            raise ValueError("no profiles")
        if n == 1:
            return dict(k=1, high=[True], br=None, sse={}, bic={},
                        status="SINGLE_PROFILE")
        def sse(xs):
            mean = sum(xs) / len(xs)
            return sum((x - mean) ** 2 for x in xs)
        s1 = sse(vals)
        candidates = [(sse(vals[:i]) + sse(vals[i:]), vals[i], i)
                      for i in range(1, n) if vals[i - 1] != vals[i]]
        best = min(candidates, key=lambda c: (c[0], -c[1])) if candidates else None
        ss = {1: s1}
        if best:
            ss[2] = best[0]
        bc = {k: D(n) * (v / n + D("1e-12")).ln() + D(k) * D(n).ln()
              for k, v in ss.items()}
        k = min(bc, key=lambda x: (bc[x], x))
        return dict(k=k, high=[k == 2 and x >= best[1] for x in vals],
                    br=best[1] if k == 2 else None,
                    candidate_break=best[1] if best else None,
                    sse=ss, bic=bc,
                    status="SUCCESS" if k == 2 else "NO_OBVIOUS_MAIN")


def evidence(**updates):
    e = dict(checked_run_id="r1", rating_group_status="RELIABLE",
             rating_validation_ref="synthetic/r1/grade-validation",
             rating_population_completeness_status="PASSED",
             source_delivery_status="COMPLETE",
             source_delivery_check_ref="synthetic/r1/delivery",
             expected_rating_key_cnt=100, result_rating_key_cnt=100)
    e.update({k: 0 for k in ZERO_KEYS})
    e.update(updates)
    return e


def read_gate(e, run="r1", actual_keys=100, proof_verified=True, scope_hold=False):
    """proof_verified 仅是测试注入的核验结论；真实系统须实际读取并验证证据内容。"""
    if not e or scope_hold or not proof_verified:
        return "BLOCKED"
    if (e.get("checked_run_id") != run or e.get("rating_group_status") != "RELIABLE"
            or not e.get("rating_validation_ref")):
        return "BLOCKED"
    if e.get("source_delivery_status") == "KNOWN_GAP":
        return "BLOCKED"
    if any((e.get(k) or 0) > 0 for k in ZERO_KEYS[:4]):
        return "BLOCKED"
    if e.get("result_rating_key_cnt") != actual_keys:
        return "BLOCKED"
    complete = (
        e.get("rating_population_completeness_status") == "PASSED"
        and e.get("source_delivery_status") == "COMPLETE"
        and bool(e.get("source_delivery_check_ref"))
        and all(e.get(k) == 0 for k in ZERO_KEYS)
        and e.get("expected_rating_key_cnt") == e.get("result_rating_key_cnt")
    )
    return "AVAILABLE" if complete else "UNAVAILABLE"


def operating_days(rows):
    """rows: (日期, 历史营业, 可售, 源完整, 销售额)。"""
    if len({r[0] for r in rows}) != len(rows):
        raise ValueError("duplicate store date")
    if any(r[1] is None or r[2] is None for r in rows):
        return None, None, None, None
    potential = [r for r in rows if r[1] and r[2]]
    valid = [r for r in potential if r[3]]
    total = sum(D(r[4]) for r in valid)
    return (len(potential), len(potential) - len(valid), len(valid),
            total / len(valid) if valid else None)


def frozen_category(rows, upper_bound):
    if upper_bound is None:
        raise ValueError("historical binding absent")
    result = {}
    for sku, category, arrival_id in rows:
        if arrival_id <= upper_bound:
            if sku in result and result[sku] != category:
                raise ValueError("ambiguous SKU category")
            result[sku] = category
    return result


def group_total(rows):
    values = {D(r["group_sales_amt"]) for r in rows}
    if len(values) != 1:
        raise ValueError("inconsistent repeated group totals")
    return next(iter(values))


def bootstrap_fields(status, completed):
    if status == "NOT_APPLICABLE":
        return (0, D(1), D(1), D(1), D(0))
    if status == "FAILED":
        return (completed, None, None, None, None)
    raise ValueError("fixture supports boundary states only")


def deterministic_draw(keys, members, count):
    payload = json.dumps(keys, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    seed = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
    rng = random.Random(seed)
    members = sorted(members, key=lambda x: x.encode("utf-8"))
    return [members[rng.randrange(len(members))] for _ in range(count)]


def publication(rows):
    return (bool(rows) and all(flag == 1 and at for flag, at in rows)
            and len({at for flag, at in rows}) == 1)


def range_held(ranges, group):
    if ranges is None:
        return True
    fields = ('scope_type', 'scope_id', 'category_granularity', 'category_code')
    return any(all(r.get(k) is None or r[k] == group[k] for k in fields)
               for r in ranges)


class SyntheticRules(unittest.TestCase):
    def test_global_unlocated_hold(self):
        group = dict(scope_type='CITY', scope_id='SH', category_granularity='SMALL', category_code='x')
        self.assertTrue(range_held([{}], group))
        self.assertTrue(range_held(None, group))

    def test_region_hold_all_categories_not_other_region(self):
        group = dict(scope_type='CITY', scope_id='SH', category_granularity='SMALL', category_code='x')
        self.assertTrue(range_held([dict(scope_type='CITY', scope_id='SH')], group))
        self.assertFalse(range_held([dict(scope_type='CITY_CLUSTER', scope_id='HZ_NB_SX')], group))

    def test_explicit_empty_holds_still_requires_group_gate(self):
        group = dict(scope_type='CITY', scope_id='SH', category_granularity='SMALL', category_code='x')
        self.assertFalse(range_held([], group))
        self.assertEqual(read_gate(None), 'BLOCKED')

    def test_complete_group(self):
        self.assertEqual(read_gate(evidence()), "AVAILABLE")

    def test_whole_store_omission_even_balanced_results(self):
        e = evidence(expected_rating_key_cnt=99, result_rating_key_cnt=99,
                     source_missing_store_day_cnt=1, source_delivery_status="KNOWN_GAP")
        self.assertEqual(read_gate(e, actual_keys=99), "BLOCKED")

    def test_partition_presence_is_not_complete_evidence(self):
        e = evidence(source_delivery_status="UNVERIFIED",
                     rating_group_status="BLOCKED_UNVERIFIED")
        self.assertEqual(read_gate(e), "BLOCKED")

    def test_missing_group_record_blocks(self):
        self.assertEqual(read_gate(None), "BLOCKED")

    def test_reliable_grades_coverage_only_unavailable(self):
        e = evidence(rating_population_completeness_status="UNAVAILABLE",
                     source_delivery_status="UNVERIFIED",
                     source_delivery_check_ref=None, source_missing_store_day_cnt=None)
        self.assertEqual(read_gate(e), "UNAVAILABLE")

    def test_reference_string_not_proof(self):
        self.assertEqual(read_gate(evidence(), proof_verified=False), "BLOCKED")

    def test_missing_rating_proof_blocks(self):
        self.assertEqual(read_gate(evidence(rating_validation_ref=None)), "BLOCKED")

    def test_known_gap_overrides_successful_label(self):
        self.assertEqual(read_gate(evidence(source_delivery_status="KNOWN_GAP")), "BLOCKED")

    def test_unmapped_store_blocks(self):
        self.assertEqual(read_gate(evidence(unmapped_store_source_record_cnt=1)), "BLOCKED")

    def test_unmapped_region_blocks(self):
        self.assertEqual(read_gate(evidence(unmapped_scope_source_record_cnt=1)), "BLOCKED")

    def test_unmapped_category_blocks(self):
        self.assertEqual(read_gate(evidence(unmapped_category_source_record_cnt=1)), "BLOCKED")

    def test_null_is_not_zero(self):
        self.assertEqual(read_gate(evidence(source_missing_store_day_cnt=None)), "UNAVAILABLE")

    def test_result_read_mismatch_is_not_coverage_only(self):
        self.assertEqual(read_gate(evidence(), actual_keys=99), "BLOCKED")

    def test_scope_hold_overrides_group_label(self):
        self.assertEqual(read_gate(evidence(), scope_hold=True), "BLOCKED")

    def test_stale_run_blocks(self):
        self.assertEqual(read_gate(evidence(), run="r2"), "BLOCKED")

    def test_reliable_other_group_continues(self):
        self.assertEqual([read_gate(evidence()), read_gate(evidence(
            rating_group_status="BLOCKED_SOURCE_GAP"))], ["AVAILABLE", "BLOCKED"])

    def test_old_success_not_kept_after_revocation(self):
        self.assertEqual(read_gate(evidence(rating_group_status="BLOCKED_SOURCE_GAP")), "BLOCKED")

    def test_historical_daily_state(self):
        rows = [("d1", True, True, True, "100"), ("d2", False, True, True, "200")]
        self.assertEqual(operating_days(rows), (1, 0, 1, D(100)))

    def test_real_zero_sales_in_denominator(self):
        rows = [("d1", True, True, True, "100"), ("d2", True, True, True, "0")]
        self.assertEqual(operating_days(rows), (2, 0, 2, D(50)))

    def test_remove_missing_day_numerator_and_denominator(self):
        rows = [(str(i), True, True, i != 1, "100") for i in range(3)]
        self.assertEqual(operating_days(rows), (3, 1, 2, D(100)))

    def test_unknown_saleable_population_is_not_zero(self):
        self.assertEqual(operating_days([("d1", True, None, False, "0")]), (None,) * 4)

    def test_unknown_operating_day_is_not_closed(self):
        self.assertEqual(operating_days([("d1", None, True, True, "100")]), (None,) * 4)

    def test_duplicate_historical_day_blocks_join(self):
        with self.assertRaises(ValueError):
            operating_days([("d", True, True, True, "1")] * 2)

    def test_append_does_not_change_old_classification(self):
        original = [("sku1", "A", 1)]
        appended = original + [("sku1", "B", 2), ("sku2", "C", 2)]
        self.assertEqual(frozen_category(original, 1), frozen_category(appended, 1))

    def test_history_without_read_boundary_blocks(self):
        with self.assertRaises(ValueError):
            frozen_category([("sku", "TODAY", 9)], None)

    def test_conflicting_category_not_arbitrary_last(self):
        with self.assertRaises(ValueError):
            frozen_category([("sku", "A", 1), ("sku", "B", 1)], 1)

    def test_precision_can_change_partition(self):
        scores = contribution([5000, 5000], ["500000.10", "499999.90"])
        shown = [s.quantize(D("0.0001"), rounding=ROUND_HALF_EVEN) for s in scores]
        self.assertEqual(shown, [D("50.0000"), D("50.0000")])
        self.assertNotEqual(scores[0], scores[1])
        self.assertEqual(jenks(scores)["k"], 2)
        self.assertEqual(jenks(shown)["k"], 1)

    def test_tied_sse_uses_higher_break(self):
        self.assertEqual(jenks(["10", "20", "30"])["candidate_break"], D(30))

    def test_equal_scores_not_split(self):
        r = jenks(["10", "10", "20", "20"])
        self.assertEqual(r["high"], [False, False, True, True])

    def test_break_boundary_in_high_group(self):
        r = jenks(["10", "10", "20", "20"])
        self.assertEqual(r["br"], D(20))
        self.assertTrue(r["high"][2])

    def test_normal_k1_retains_sse_bic(self):
        r = jenks(["50", "50"])
        self.assertEqual(r["status"], "NO_OBVIOUS_MAIN")
        self.assertEqual(r["sse"][1], 0)
        self.assertIn(1, r["bic"])
        self.assertIsNone(r["br"])

    def test_single_profile_no_fake_bic(self):
        r = jenks(["100"])
        self.assertEqual(r["status"], "SINGLE_PROFILE")
        self.assertEqual(r["bic"], {})

    def test_summary_repeated_total_take_once(self):
        self.assertEqual(group_total([{"group_sales_amt": "100"}] * 2), D(100))

    def test_summary_inconsistency_blocks(self):
        with self.assertRaises(ValueError):
            group_total([{"group_sales_amt": "100"}, {"group_sales_amt": "200"}])

    def test_bootstrap_failure_null_not_zero(self):
        self.assertEqual(bootstrap_fields("FAILED", 27), (27, None, None, None, None))

    def test_single_profile_bootstrap_boundary(self):
        self.assertEqual(bootstrap_fields("NOT_APPLICABLE", 0), (0, D(1), D(1), D(1), D(0)))

    def test_reproducible_bootstrap_sorted_members(self):
        a = deterministic_draw(["BATCH_202608", "SH", "牛肉"], ["m2", "m1"], 100)
        b = deterministic_draw(["BATCH_202608", "SH", "牛肉"], ["m1", "m2"], 100)
        self.assertEqual(a, b)

    def test_published_parameter_rows_all_agree(self):
        self.assertTrue(publication([(1, "t"), (1, "t")]))
        for rows in [[], [(1, "t"), (0, "t")], [(1, "t"), (1, None)], [(1, "t"), (1, "t2")]]:
            self.assertFalse(publication(rows))

    def test_retained_core_formula_example(self):
        scores = contribution([3500, 3000, 2000, 1500],
                              ["3400000", "3200000", "1800000", "1600000"])
        r = jenks(scores)
        self.assertEqual(r["k"], 2)
        self.assertEqual(sum(r["high"]), 2)
        self.assertEqual(scores[0].quantize(D(".01")), D("34.49"))


class DocumentContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texts = {p: (ROOT / p).read_text() for p in (D2, D3, B2, B3)}
        cls.a, cls.b = cls.texts[D2], cls.texts[D3]

    def test_fences_closed(self):
        for path, content in self.texts.items():
            opened = None
            for line in content.splitlines():
                m = re.match(r"^(\x60{3,}|~{3,})(.*)$", line)
                if m:
                    if opened is None:
                        opened = m.group(1)
                    elif m.group(1)[0] == opened[0] and not m.group(2).strip():
                        opened = None
            self.assertIsNone(opened, path)

    def test_no_removed_source_table(self):
        for path, content in self.texts.items():
            self.assertNotRegex(content, r"dws_member_order_item_detail_df_all(?!_new)", path)

    def test_no_stale_mapping_field_names(self):
        self.assertNotIn("source_effective_start_date", self.b)
        self.assertNotIn("source_effective_end_date", self.b)
        for field in ("mapping_effective_start_date", "mapping_effective_end_date"):
            self.assertIn(field, self.a)
            self.assertIn(field, self.b)

    def test_group_interface_and_enum_alignment(self):
        for name in ("rating_group_evidence_json", "rating_group_status", "checked_run_id",
                     "rating_validation_ref", "source_delivery_status",
                     "RELIABLE", "BLOCKED_SOURCE_GAP", "BLOCKED_UNVERIFIED"):
            self.assertIn(name, self.a)
            self.assertIn(name, self.b)
        for name in ZERO_KEYS:
            self.assertIn(name, self.a)
            self.assertIn(name, self.b)

    def test_no_unconditional_coverage_only_fallback(self):
        bad = ("不满足时只把未评级门店数和评级覆盖率置空",
               "证据不可用不影响已经正常算出的门店等级",
               "后者只使下游覆盖率不可用",
               "缺数据日期仅从分母排除")
        for content in self.texts.values():
            for phrase in bad:
                self.assertNotIn(phrase, content)

    def test_01_existing_publication_control_reused(self):
        self.assertIn("dim_customer_profile_region_param.published_flag", self.b)
        self.assertIn("dim_customer_profile_region_param.published_at", self.b)

    def test_classification_separate_from_source_version(self):
        self.assertNotIn("algorithm_batch_version + source_data_version", self.b)
        for content in (self.a, self.b):
            self.assertIn("category_read_binding_json", content)
            self.assertIn("不新增分类快照", content)

    def test_output_fields_six_columns(self):
        # 只检查字段定义表；状态表/JSON表有各自表头。
        outputs = (self.a.split('## 14. 输出表结构', 1)[1],
                   self.b.split('## 15. 输出字段', 1)[1],
                   self.a.split('### 5.3.1 共享范围快照表', 1)[1].split('### 5.4', 1)[0])
        for content in outputs:
            in_fields = False
            for line in content.splitlines():
                if line.startswith("| 中文字段名"):
                    self.assertEqual(line, "| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |")
                    in_fields = True
                elif in_fields and line.startswith("|"):
                    self.assertEqual(len(line.strip("|").split("|")), 6, line)
                else:
                    in_fields = False

    def test_original_real_sample_acceptance_preserved(self):
        for content in (self.b, self.texts[B3]):
            self.assertIn("至少 30 个门店群结果", content)

    def test_output_tables_preserved(self):
        for name in ("mart_store_group_consumer_contribution", "mart_store_group_consumer_summary"):
            self.assertIn(name, self.b)
        self.assertIn("实体结果表", self.b)
        self.assertIn("algorithm_batch_version + city", self.a)

    def test_new_scope_hold_interface_aligned(self):
        self.assertIn('blocked_scope_ranges', self.a)
        self.assertIn('blocked_scope_ranges', self.b)

    def test_result_enum_fields_have_constraint_rows(self):
        for content, start in ((self.a, '## 14. 输出表结构'), (self.b, '## 15. 输出字段')):
            output = content.split(start, 1)[1]
            names = re.findall(r'^\| [^|]+ \| \x60([a-z_]+)\x60 \| (?:varchar|tinyint|int)', output, re.M)
            enums = [n for n in names if n.endswith(('_status', '_flag', '_method'))]
            for name in enums:
                self.assertTrue(re.search(r'^\| \x60' + re.escape(name) + r'\x60 \|', content, re.M), name)

    def test_v19_scoring_and_auto_selection_unchanged(self):
        old = subprocess.check_output(["git", "show", "acc64a5:" + D2], cwd=ROOT, text=True)
        def section(text, begin, end):
            return text.split(begin, 1)[1].split(end, 1)[0]
        # 不含状态/交付文字，只核对原有计算与选参正文。
        for begin, end in (
            ("## 8. 通用指标标准化", "## 9. CRITIC"),
            ("## 10. 七个一级维度计算", "### 10.8 空分母"),
            ("## 11. 一级维度综合评分", "## 13. 经营底线"),
            ("### 13.1 连续亏损上限", "### 13.3 数据与权重"),
        ):
            self.assertEqual(section(old, begin, end), section(self.a, begin, end), begin)

    def test_dangerous_tokens_reviewed(self):
        patterns = (r"逻辑字段名|建议类型|物理表名待开发确认|待开发确认|需要用户确认|是否能到|"
                    r"字段中文注释补充|英文枚举中文注释|状态枚举表|采购手动输入候选|可比商品组字典|"
                    r"profile_model_version|model_version|scope_version|rule_version|parameter_version|"
                    r"price_version|batch_seq|V[12]_YYYYMM|V_YYYYMM|profile_YYYYMM")
        for content in self.texts.values():
            for line in content.splitlines():
                if re.search(patterns, line):
                    self.assertTrue("不生成" in line or "不能生成或引用" in line
                                    or "hour_promotion_rule_version" in line, line)

    def test_git_whitespace(self):
        subprocess.check_call(["git", "diff", "--check"], cwd=ROOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)

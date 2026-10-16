"""Regression and adversarial tests for the four algorithm 07 review findings."""
import copy
import json
from pathlib import Path
import re
import tempfile
import unittest

from algorithm07_contract_checks import (
    AUDIT_LOCATION, CONDITIONAL_STAGES, DEV_PATH, FIELD_HEADER,
    canonical_hash, check_four_fix_contracts, conditional_cohort,
    conditional_growth_label, formal_tables, local_reference_issues,
    numeric_input_hash, parse_field_contract, range_key, validate_audit_object,
)

ROOT = Path(__file__).resolve().parents[2]


def field_table(*rows):
    return '\n'.join(['| ' + ' | '.join(FIELD_HEADER) + ' |',
                       '|---|---|---|---|---|---|', *rows])


def mutate_contract(document, name, changes):
    def replace(match):
        obj = json.loads(match.group(1))
        if obj.get('contract_name') != name:
            return match.group(0)
        obj.update(changes)
        return '```json\n' + json.dumps(obj, ensure_ascii=False, indent=2) + '\n```'
    return re.sub(r'^```json\s*\n(.*?)^```\s*$', replace, document, flags=re.M | re.S)


class FieldStructureTests(unittest.TestCase):
    def test_four_original_bad_rows_are_all_rejected(self):
        doc = field_table('| 中文 | `field_a` | 描述 |', '| `field_b` | 描述 |',
                          '| `field_c` | 描述 |', '| `summary_json` | json | 必须 | 步骤 | 注释 |')
        fields, issues = parse_field_contract(doc)
        self.assertEqual(fields, {})
        self.assertEqual([item[-1] for item in issues], [3, 2, 2, 5])

    def test_valid_six_columns_are_retained(self):
        fields, issues = parse_field_contract(field_table('| 摘要 | `summary_json` | json | 必须 | 步骤 | 对象 |'))
        self.assertFalse(issues)
        self.assertIn('summary_json', fields)

    def test_empty_source_is_rejected(self):
        _, issues = parse_field_contract(field_table('| 摘要 | `summary_json` | json | 必须 | | 对象 |'))
        self.assertTrue(issues)

    def test_invalid_english_name_is_rejected(self):
        _, issues = parse_field_contract(field_table('| 摘要 | `field A / field B` | json | 必须 | 步骤 | 对象 |'))
        self.assertTrue(issues)

    def test_duplicate_field_is_rejected(self):
        row = '| 摘要 | `summary_json` | json | 必须 | 步骤 | 对象 |'
        _, issues = parse_field_contract(field_table(row, row))
        self.assertTrue(any('duplicate field' in issue for issue in issues))

    def test_downstream_missing_field_is_rejected(self):
        doc = '### 10.7 `external_candidate_internal_fit`\n\n' + field_table(
            '| 键 | `id` | string | 必须 | 系统 | 键 |')
        tables, _ = formal_tables(doc)
        issues = local_reference_issues(doc + '\nexternal_candidate_internal_fit.internal_fit_summary_json', tables)
        self.assertEqual(issues[0][-1], 'internal_fit_summary_json')


class DocumentMutationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / 'results'
        self.output.mkdir()
        names = [DEV_PATH,
                 '03_data_contracts/external_data/dim_competitor_sku_竞品SKU基础表.md',
                 '03_data_contracts/external_data/fact_competitor_sku_daily_snapshot_竞品每日快照表.md']
        for name in names:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text((ROOT / name).read_text())

    def reject(self, change, code):
        p = self.root / DEV_PATH
        before = p.read_text()
        after = change(before)
        self.assertNotEqual(before, after, 'Mutation did not exercise the document')
        p.write_text(after)
        with self.assertRaises(AssertionError):
            check_four_fix_contracts(self.root, self.output)
        issues = json.loads((self.output / 'algo07_four_fix_validation.json').read_text())['issues']
        self.assertTrue(any(issue[0] == code for issue in issues), issues)

    def test_repaired_document_is_accepted(self):
        result = check_four_fix_contracts(self.root, self.output)
        self.assertEqual(result['formal_tables_checked'], 11)
        self.assertEqual(result['execution_contracts_checked'], 3)
        self.assertFalse(result['issues'])

    def test_r01_missing_fit_summary_is_rejected(self):
        self.reject(lambda s: re.sub(r'^\| 内部适配摘要 \| `internal_fit_summary_json` \| json \| 必须 \| 第17\.10节.*\n', '', s, flags=re.M), 'R01')

    def test_r01_json_definition_wrongly_removed_is_rejected(self):
        self.reject(lambda s: re.sub(r'^\| `source_product_key_json` \|.*\n', '', s, flags=re.M), 'R01')

    def test_r01_entire_formal_table_removed_is_rejected(self):
        self.reject(lambda s: re.sub(r'^### 10\.4 `social_trend_evidence`.*?(?=^### )', '', s, flags=re.M | re.S), 'R01')

    def test_r02_raw_region_code_as_fit_key_is_rejected(self):
        self.reject(lambda s: s.replace('第17.10节range_identity执行合同派生', 'dim_algorithm_batch_city_region_snapshot.algorithm_region_code'), 'R02')

    def test_r02_key_component_order_change_is_rejected(self):
        self.reject(lambda s: mutate_contract(s, 'range_identity', {'fields': ['scope_id', 'scope_type']}), 'R02')

    def test_r02_candidate_uses_original_scope_instead_of_fit_key_is_rejected(self):
        self.reject(lambda s: s.replace('`external_candidate_internal_fit.target_city_group_id`', '`external_candidate_internal_fit.scope_id`'), 'R02')

    def test_r03_wrong_audit_path_is_rejected(self):
        self.reject(lambda s: mutate_contract(s, 'input_asset_audit', {'location': 'external_trend_run.source_audit_json'}), 'R03')

    def test_r03_audit_enters_fact_hash_is_rejected(self):
        self.reject(lambda s: mutate_contract(s, 'input_asset_audit', {'facts_hash_scope': ['source_table', 'source_audit_json', 'rows']}), 'R03')

    def test_r03_audit_not_declared_in_parent_is_rejected(self):
        self.reject(lambda s: s.replace('、source_audit_json（10.10.1固定对象）', ''), 'R03')

    def test_r03_wrong_child_type_is_rejected(self):
        types = {'collection_batch_ids': 'string'}
        self.reject(lambda s: mutate_contract(s, 'input_asset_audit', {'types': types}), 'R03')

    def test_r03_native_contract_with_unqualified_path_is_rejected(self):
        p = self.root / '03_data_contracts/external_data/dim_competitor_sku_竞品SKU基础表.md'
        p.write_text(p.read_text().replace(AUDIT_LOCATION, 'source_audit_json'))
        with self.assertRaises(AssertionError):
            check_four_fix_contracts(self.root, self.output)

    def test_r04_non_real_population_is_rejected(self):
        self.reject(lambda s: mutate_contract(s, 'conditional_growth_population', {'T_real_allowed': [0, 1]}), 'R04')

    def test_r04_boolean_is_not_an_integer_training_label(self):
        self.reject(lambda s: mutate_contract(s, 'conditional_growth_population', {'T_real_allowed': [True]}), 'R04')

    def test_r04_calibration_stage_unrestricted_is_rejected(self):
        self.reject(lambda s: mutate_contract(s, 'conditional_growth_population', {'restricted_stages': ['TRAIN', 'TEST', 'HORIZON_SELECTION', 'BACKTEST']}), 'R04')

    def test_r04_future_label_prediction_filter_is_rejected(self):
        self.reject(lambda s: mutate_contract(s, 'conditional_growth_population', {'prediction_label_filter': {'T_real': 1}}), 'R04')

    def test_r04_old_negative_definition_is_rejected(self):
        self.reject(lambda s: s.replace('delta的95%上界≤0为0', 'delta的95%上界≤0或完整未来窗确认未持续采用为0'), 'R04')


class RangeAndAuditTests(unittest.TestCase):
    def setUp(self):
        self.asset = {'source_table': 'fact_competitor_sku_daily_snapshot',
                      'business_key_columns': ['collection_date', 'data_provider', 'competitor_platform', 'city_name', 'competitor_sku_id'],
                      'source_fields': ['collection_date', 'data_provider', 'competitor_platform', 'city_name', 'competitor_sku_id', 'current_sale_price'],
                      'audit_source_fields': ['collection_batch_id', 'data_update_time']}
        self.row = {'collection_date': '2026-09-30', 'data_provider': 'JIUQIAN_TEST',
                    'competitor_platform': 'PLATFORM_TEST', 'city_name': 'CITY_TEST',
                    'competitor_sku_id': 'SKU_TEST', 'current_sale_price': '12.000000',
                    'collection_batch_id': 'SUPPLY_TEST_A', 'data_update_time': '2026-10-01 01:00:00'}
        self.audit = {'collection_batch_ids': ['SUPPLY_TEST_A'], 'upstream_run_ids': [],
                      'row_audit_reference': 'synthetic://immutable-audit',
                      'row_audit_hash': canonical_hash([self.row]), 'audit_missing_fields': []}

    def test_single_city_range_known_vector(self):
        self.assertEqual(range_key('CITY', 'REGION_TEST'), 'bd568de4a8bc9701b435835e2c0bb6260530576c0a34d7970c5886e656d7d8a9')

    def test_city_cluster_range_known_vector(self):
        self.assertEqual(range_key('CITY_CLUSTER', 'GROUP_TEST'), 'd8fb0d7590e1d836b0698251e129b45162a3a74606b103de1b43b40fb5d4b69f')

    def test_utf8_byte_length_not_character_length(self):
        self.assertEqual(range_key('CITY', '区域甲'), 'd3f77838fbb395491e65e043795d3a93fe0f712d03a250abe6fc5557f913f56e')

    def test_raw_scope_and_derived_key_are_distinct(self):
        self.assertNotEqual('REGION_TEST', range_key('CITY', 'REGION_TEST'))
        self.assertNotEqual(range_key('CITY', 'REGION_TEST'), range_key('CITY_CLUSTER', 'REGION_TEST'))

    def test_missing_scope_is_rejected(self):
        for kind, value in [('CITY', ''), ('CITY', None), ('UNKNOWN', 'REGION_TEST')]:
            with self.subTest(kind=kind, value=value), self.assertRaises(ValueError):
                range_key(kind, value)

    def test_audit_changes_do_not_change_numeric_input(self):
        changed = dict(self.row, collection_batch_id='SUPPLY_TEST_B', data_update_time='2026-10-02 01:00:00')
        self.assertEqual(numeric_input_hash(self.asset, [self.row]), numeric_input_hash(self.asset, [changed]))
        self.assertNotEqual(canonical_hash([self.row]), canonical_hash([changed]))

    def test_price_and_real_observation_date_change_facts(self):
        for column, value in [('current_sale_price', '13.000000'), ('collection_date', '2026-09-29')]:
            with self.subTest(column=column):
                self.assertNotEqual(numeric_input_hash(self.asset, [self.row]), numeric_input_hash(self.asset, [dict(self.row, **{column: value})]))

    def test_fact_row_order_does_not_change_hash(self):
        second = dict(self.row, competitor_sku_id='SKU_TEST_B')
        self.assertEqual(numeric_input_hash(self.asset, [self.row, second]), numeric_input_hash(self.asset, [second, self.row]))

    def test_duplicate_business_key_is_rejected(self):
        with self.assertRaises(ValueError):
            numeric_input_hash(self.asset, [self.row, self.row])

    def test_null_or_empty_business_key_is_rejected(self):
        for value in [None, '']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                numeric_input_hash(self.asset, [dict(self.row, competitor_sku_id=value)])

    def test_audit_column_cannot_be_declared_as_fact(self):
        asset = copy.deepcopy(self.asset)
        asset['source_fields'].append('collection_batch_id')
        with self.assertRaises(ValueError):
            numeric_input_hash(asset, [self.row])

    def test_nonempty_asset_needs_per_row_audit_reference(self):
        validate_audit_object(self.audit, 1)
        self.audit['row_audit_reference'] = None
        with self.assertRaises(ValueError):
            validate_audit_object(self.audit, 1)

    def test_missing_audit_key_is_rejected(self):
        del self.audit['row_audit_hash']
        with self.assertRaises(ValueError):
            validate_audit_object(self.audit, 1)

    def test_unknown_audit_fields_are_rejected(self):
        self.audit['undeclared'] = 'value'
        with self.assertRaises(ValueError):
            validate_audit_object(self.audit, 1)

    def test_empty_asset_has_explicit_empty_audit(self):
        audit = {'collection_batch_ids': [], 'upstream_run_ids': [], 'row_audit_reference': None,
                 'row_audit_hash': None, 'audit_missing_fields': []}
        validate_audit_object(audit, 0)

    def test_empty_asset_cannot_carry_phantom_supply_batch(self):
        audit = dict(self.audit, row_audit_reference=None, row_audit_hash=None)
        with self.assertRaises(ValueError):
            validate_audit_object(audit, 0)


class ConditionalGrowthTests(unittest.TestCase):
    def test_real_growing_is_positive(self):
        self.assertEqual(conditional_growth_label(1, 0.1, 0.4, True, True), 1)

    def test_real_non_growing_is_negative(self):
        self.assertEqual(conditional_growth_label(1, -0.4, 0, False, True), 0)

    def test_non_real_and_unknown_are_not_negatives(self):
        for real in [0, None]:
            with self.subTest(real=real):
                self.assertIsNone(conditional_growth_label(real, -0.4, -0.1, False, True))

    def test_uncertain_or_incomplete_real_is_censored(self):
        for low, high, new, complete in [(-0.1, 0.2, True, True), (0.1, 0.3, False, True), (0.1, 0.3, True, False)]:
            with self.subTest(values=(low, high, new, complete)):
                self.assertIsNone(conditional_growth_label(1, low, high, new, complete))

    def test_all_historical_stages_filter_the_same_population(self):
        rows = [{'sample_id': str(i), 'T_real': real, 'T_grow_given_real': growth}
                for i, (real, growth) in enumerate([(1, 1), (1, 0), (1, None), (0, None), (None, None)])]
        for stage in CONDITIONAL_STAGES:
            with self.subTest(stage=stage):
                selected, audit = conditional_cohort(rows, stage)
                self.assertEqual([row['sample_id'] for row in selected], ['0', '1'])
                self.assertEqual(audit['selected_count'], 2)
                self.assertEqual(audit['real_1_count'], 3)
                self.assertEqual(audit['growth_censored_count'], 1)
                self.assertEqual(audit['input_count'], 5)

    def test_non_real_negative_contamination_is_rejected(self):
        with self.assertRaises(ValueError):
            conditional_cohort([{'sample_id': 'bad', 'T_real': 0, 'T_grow_given_real': 0}], 'TRAIN')

    def test_future_label_is_not_a_prediction_filter(self):
        with self.assertRaises(ValueError):
            conditional_cohort([], 'PREDICTION')

    def test_duplicate_training_sample_is_rejected(self):
        row = {'sample_id': 'duplicate', 'T_real': 1, 'T_grow_given_real': 1}
        with self.assertRaises(ValueError):
            conditional_cohort([row, row], 'TRAIN')

    def test_conditional_probability_not_repeated_real_factor(self):
        rows = [{'sample_id': str(i), 'T_real': 1 if i < 50 else 0,
                 'T_grow_given_real': 1 if i < 30 else 0 if i < 50 else None} for i in range(100)]
        selected, report = conditional_cohort(rows, 'TEST')
        p_real = report['real_1_count'] / report['input_count']
        p_growth_given_real = sum(row['T_grow_given_real'] for row in selected) / len(selected)
        self.assertEqual(p_real * p_growth_given_real, 0.3)
        unconditional_growth = report['growth_positive_count'] / report['input_count']
        self.assertEqual(p_real * unconditional_growth, 0.15)
        self.assertNotEqual(p_real * p_growth_given_real, p_real * unconditional_growth)


if __name__ == '__main__':
    unittest.main()

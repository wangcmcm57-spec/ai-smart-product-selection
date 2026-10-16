"""Strict document checks and synthetic reference functions for algorithm 07.

These functions validate specifications, never production data or model training.
"""
import hashlib
import json
import re

DEV_PATH = '04_algorithm_cards/developer_version/算法卡_07_竞品与全球外部趋势新品发现.md'
FIELD_HEADER = ['中文字段名', '英文字段名', '类型建议', '是否必须', '字段来源', '中文注释']
AUDIT_COLUMNS = {'collection_batch_id', 'data_update_time', 'run_id', 'calculated_at', 'updated_at'}
CONDITIONAL_STAGES = ['TRAIN', 'CALIBRATION', 'TEST', 'HORIZON_SELECTION', 'BACKTEST']
AUDIT_LOCATION = 'external_trend_run.input_assets_snapshot_json[*].source_audit_json'
AUDIT_TYPES = {
    'collection_batch_ids': 'array<string>',
    'upstream_run_ids': 'array<string>',
    'row_audit_reference': 'string|null',
    'row_audit_hash': 'string|null',
    'audit_missing_fields': 'array<string>',
}
EXPECTED_TABLES = {
    'external_trend_run', 'external_attribute_mapping', 'competitor_channel_evidence',
    'social_trend_evidence', 'industry_external_evidence', 'external_trend_state',
    'external_candidate_internal_fit', 'external_candidate_image', 'external_new_product_candidate',
    'mart_external_source_coverage_audit', 'mart_external_candidate_price_input',
}


def cells(line):
    return [part.strip() for part in re.split(r'(?<!\\)\|', line.strip().strip('|'))]


def parse_field_contract(text, table_name='', line_offset=0):
    """Return every valid field and every malformed row; never skip bad rows."""
    fields = {}
    issues = []
    active = False
    found_header = False
    for number, line in enumerate(text.splitlines(), line_offset + 1):
        if not line.startswith('|'):
            active = False
            continue
        row = cells(line)
        if row == FIELD_HEADER:
            active = found_header = True
            continue
        if not active:
            continue
        if all(re.fullmatch(r':?-+:?', value) for value in row):
            if len(row) != 6:
                issues.append(['R01', table_name, number, 'bad separator column count', len(row)])
            continue
        if len(row) != 6:
            issues.append(['R01', table_name, number, 'field row must have six columns', len(row)])
            continue
        if not all(row):
            issues.append(['R01', table_name, number, 'empty field contract cell'])
            continue
        if not re.fullmatch(r'`[a-z][a-z0-9_]*`', row[1]):
            issues.append(['R01', table_name, number, 'invalid English field name', row[1]])
            continue
        field = row[1].strip('`')
        if field in fields:
            issues.append(['R01', table_name, number, 'duplicate field', field])
        if row[3] not in {'必须', '条件必须', '可选', '建议'}:
            issues.append(['R01', table_name, number, 'invalid requiredness', row[3]])
        fields[field] = row
    if not found_header:
        issues.append(['R01', table_name, line_offset, 'missing field contract header'])
    return fields, issues


def formal_tables(document):
    tables = {}
    issues = []
    for match in re.finditer(r'^### 10\.\d+ `([^`]+)`.*?(?=^### |^## |\Z)', document, re.M | re.S):
        name = match.group(1)
        offset = document[:match.start()].count('\n')
        fields, errors = parse_field_contract(match.group(0), name, offset)
        if name in tables:
            issues.append(['R01', name, offset, 'duplicate formal table definition'])
        tables[name] = fields
        issues.extend(errors)
    return tables, issues


def local_reference_issues(document, tables):
    issues = []
    for table, fields in tables.items():
        for match in re.finditer(r'\b' + re.escape(table) + r'\.([a-z][a-z0-9_]*)', document):
            field = match.group(1)
            if field not in fields:
                issues.append(['R01', table, document[:match.start()].count('\n') + 1,
                               'referenced local field missing', field])
    return issues


def execution_contracts(document):
    contracts = {}
    issues = []
    for match in re.finditer(r'^```json\s*\n(.*?)^```\s*$', document, re.M | re.S):
        try:
            obj = json.loads(match.group(1))
        except json.JSONDecodeError as error:
            issues.append(['execution_contract', 'invalid JSON', str(error)])
            continue
        if isinstance(obj, dict) and 'contract_name' in obj:
            name = obj['contract_name']
            if name in contracts:
                issues.append(['execution_contract', 'duplicate contract', name])
            contracts[name] = obj
    return contracts, issues


def range_key(scope_type, scope_id):
    if scope_type not in {'CITY', 'CITY_CLUSTER'} or not isinstance(scope_id, str) or not scope_id:
        raise ValueError('A registered scope_type and nonempty string scope_id are required')
    parts = [scope_type.encode('utf-8'), scope_id.encode('utf-8')]
    packed = b''.join(str(len(value)).encode('ascii') + b':' + value for value in parts)
    return hashlib.sha256(packed).hexdigest()


def canonical_hash(value):
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def same_json(actual, expected):
    """Compare JSON values without treating booleans as integer labels."""
    try:
        return json.dumps(actual, sort_keys=True, allow_nan=False) == json.dumps(
            expected, sort_keys=True, allow_nan=False)
    except (TypeError, ValueError):
        return False


def numeric_input_hash(asset, source_rows):
    """Hash only declared facts, preserving all business-key and observed-time fields."""
    fields = asset['source_fields']
    key_fields = asset['business_key_columns']
    if len(fields) != len(set(fields)) or not set(key_fields).issubset(fields):
        raise ValueError('Facts must contain a unique field list and every business-key column')
    if set(fields) & AUDIT_COLUMNS:
        raise ValueError('Run/supply audit columns cannot enter the numeric fact hash')
    if set(fields) & set(asset['audit_source_fields']):
        raise ValueError('Fact and audit source fields must be disjoint')
    rows = [{field: row[field] for field in fields} for row in source_rows]
    if any(row[field] is None or row[field] == '' for row in rows for field in key_fields):
        raise ValueError('Frozen business-key values cannot be null or empty')
    keys = [json.dumps([row[field] for field in key_fields], ensure_ascii=False,
                       sort_keys=True, separators=(',', ':'), allow_nan=False) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate business keys in the frozen fact rows')
    rows = [row for _, row in sorted(zip(keys, rows), key=lambda pair: pair[0])]
    return canonical_hash({'source_table': asset['source_table'],
                           'business_key_columns': key_fields, 'source_fields': fields, 'rows': rows})


def validate_audit_object(obj, record_count):
    if not isinstance(obj, dict) or type(record_count) is not int or record_count < 0:
        raise ValueError('Audit must be an object and record_count a nonnegative integer')
    if set(obj) != set(AUDIT_TYPES):
        raise ValueError('Every asset must declare exactly the fixed source_audit_json keys')
    for field in ['collection_batch_ids', 'upstream_run_ids', 'audit_missing_fields']:
        values = obj[field]
        if not isinstance(values, list) or any(not isinstance(v, str) or not v for v in values):
            raise ValueError('Audit identifier and missing-field lists must be string arrays')
        if values != sorted(set(values)):
            raise ValueError('Audit string arrays must be unique and sorted')
    reference = obj['row_audit_reference']
    digest = obj['row_audit_hash']
    if record_count > 0:
        if not isinstance(reference, str) or not reference:
            raise ValueError('Nonempty input needs an immutable per-row audit reference')
        if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
            raise ValueError('Nonempty input needs a SHA256 row-audit hash')
    elif reference is not None or digest is not None or any(
            obj[field] for field in ['collection_batch_ids', 'upstream_run_ids', 'audit_missing_fields']):
        raise ValueError('Empty input has empty audit arrays and null row-audit reference and hash')


def conditional_growth_label(real, delta_low, delta_high, repeated_new_channel, complete):
    if real is not None and (type(real) is not int or real not in {0, 1}):
        raise ValueError('T_real must be integer 0/1 or null')
    if real != 1 or not complete:
        return None
    if delta_low is None or delta_high is None or delta_low > delta_high:
        return None
    if delta_low > 0 and repeated_new_channel:
        return 1
    if delta_high <= 0:
        return 0
    return None


def conditional_cohort(rows, stage):
    if stage not in CONDITIONAL_STAGES:
        raise ValueError('Conditional label filtering is for the five historical stages only')
    selected = []
    seen_ids = set()
    report = dict.fromkeys(['input_count', 'real_1_count', 'real_0_count', 'real_unknown_count',
                            'growth_positive_count', 'growth_negative_count', 'growth_censored_count',
                            'selected_count'], 0)
    for row in rows:
        sample_id = row['sample_id']
        if not isinstance(sample_id, str) or not sample_id or sample_id in seen_ids:
            raise ValueError('Historical sample IDs must be nonempty and unique within a stage')
        seen_ids.add(sample_id)
        real, growth = row['T_real'], row['T_grow_given_real']
        if real is not None and (type(real) is not int or real not in {0, 1}):
            raise ValueError('T_real must be integer 0/1 or null')
        if growth is not None and (type(growth) is not int or growth not in {0, 1}):
            raise ValueError('Growth label must be integer 0/1 or null')
        report['input_count'] += 1
        if real != 1:
            if growth is not None:
                raise ValueError('Non-real or censored samples cannot be conditional-growth negatives')
            report['real_0_count' if real == 0 else 'real_unknown_count'] += 1
            continue
        report['real_1_count'] += 1
        if growth is None:
            report['growth_censored_count'] += 1
        else:
            report['growth_positive_count' if growth == 1 else 'growth_negative_count'] += 1
            selected.append(row)
    report['selected_count'] = len(selected)
    return selected, report


def check_four_fix_contracts(repo_root, output_dir):
    document = (repo_root / DEV_PATH).read_text()
    tables, issues = formal_tables(document)
    if set(tables) != EXPECTED_TABLES:
        issues.append(['R01', 'formal table inventory mismatch',
                       sorted(EXPECTED_TABLES - set(tables)), sorted(set(tables) - EXPECTED_TABLES)])
    issues.extend(local_reference_issues(document, tables))
    contracts, errors = execution_contracts(document)
    issues.extend(errors)
    json_section = document.split('### 10.10 ', 1)[1].split('### 10.11 ', 1)[0]
    for field in ['ranking_diagnostics_json', 'source_product_key_json', 'source_evidence_ids_json']:
        if not re.search(r'^\| `' + field + r'` \|', json_section, re.M):
            issues.append(['R01', 'JSON structure missing from 10.10', field])
    expected_range = {
        'fields': ['scope_type', 'scope_id'], 'serialization': 'UTF8_BYTE_LENGTH_PREFIX',
        'hash': 'SHA256', 'format': 'LOWERCASE_HEX', 'derived_field': 'target_city_group_id',
        'scope_id_source': 'dim_algorithm_batch_city_region_snapshot.algorithm_region_code',
        'scope_name_source': 'dim_algorithm_batch_city_region_snapshot.algorithm_region_name',
        'null_policy': 'REJECT',
    }
    range_contract = contracts.get('range_identity', {})
    for key, value in expected_range.items():
        if not same_json(range_contract.get(key), value):
            issues.append(['R02', 'range execution contract mismatch', key])
    fit = tables.get('external_candidate_internal_fit', {})
    candidate = tables.get('external_new_product_candidate', {})
    if 'range_identity' not in fit.get('target_city_group_id', ['', '', '', '', ''])[4]:
        issues.append(['R02', 'fit key field source does not use range_identity'])
    if 'algorithm_region_name' not in fit.get('target_city_group_name', ['', '', '', '', ''])[4]:
        issues.append(['R02', 'range name source is not the registered name'])
    if candidate.get('target_city_group_id', ['', '', '', '', ''])[4] != '`external_candidate_internal_fit.target_city_group_id`':
        issues.append(['R02', 'candidate key does not read the fit derived key'])
    audit = contracts.get('input_asset_audit', {})
    if audit.get('location') != AUDIT_LOCATION or audit.get('types') != AUDIT_TYPES:
        issues.append(['R03', 'audit location or field types undefined'])
    if audit.get('facts_hash_scope') != ['source_table', 'business_key_columns', 'source_fields', 'rows']:
        issues.append(['R03', 'fact hash contract mismatch'])
    if set(audit.get('excluded_input_columns', [])) != AUDIT_COLUMNS:
        issues.append(['R03', 'audit columns not excluded from numeric facts'])
    if audit.get('audit_hash_scope') != 'AUDIT_SIDECAR_ONLY':
        issues.append(['R03', 'audit content hash not separate'])
    asset_row = next((line for line in json_section.splitlines() if line.startswith('| `input_assets_snapshot_json` |')), '')
    if 'source_audit_json' not in asset_row.split('。', 1)[0] or 'audit_source_fields' not in asset_row:
        issues.append(['R03', 'audit child object missing from the asset fixed keys'])
    for name in ['dim_competitor_sku_竞品SKU基础表.md', 'fact_competitor_sku_daily_snapshot_竞品每日快照表.md']:
        native = (repo_root / '03_data_contracts/external_data' / name).read_text()
        if AUDIT_LOCATION not in native:
            issues.append(['R03', name, 'native contract has no qualified audit path'])
    growth = contracts.get('conditional_growth_population', {})
    expected_growth = {
        'T_real_allowed': [1], 'growth_label_allowed': [0, 1],
        'excluded_T_real_values': [0, None], 'restricted_stages': CONDITIONAL_STAGES,
        'negative_rule': 'T_REAL_1_AND_DELTA_UPPER_LE_ZERO', 'prediction_label_filter': None,
        'future_labels_used_as_prediction_features': False,
        'joint_probability': 'E[p_real*p_grow_given_real]',
        'joint_evaluation_population': 'ALL_KNOWN_JOINT_LABELS',
    }
    for key, value in expected_growth.items():
        if key not in growth or not same_json(growth[key], value):
            issues.append(['R04', 'conditional-growth population contract mismatch', key])
    conditional_row = next((line for line in document.splitlines() if line.startswith('| `T_grow_given_real` |')), '')
    if '未持续采用为0' in conditional_row:
        issues.append(['R04', 'non-real samples can still be conditional negatives'])
    model_row = next((line for line in json_section.splitlines() if line.startswith('| `model_manifest_json` |')), '')
    if 'conditional_population_audit' not in model_row:
        issues.append(['R04', 'conditional cohort audit not declared in model manifest'])
    result = {'formal_tables_checked': len(tables), 'execution_contracts_checked': len(contracts),
              'checks': ['R01', 'R02', 'R03', 'R04'], 'issues': issues,
              'scope': 'DOCUMENT_CONTRACT_ONLY', 'production_model_tested': False}
    (output_dir / 'algo07_four_fix_validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    if issues:
        raise AssertionError(json.dumps(issues, ensure_ascii=False))
    return result

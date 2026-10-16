# 外部证据字段质量明细表

## 1. 表定位、粒度和主键

正式表名：`mart_external_evidence_quality_issue`。

用途：按字段保存外部证据的问题、依据和自动处理结果，支持异常统计和复算。质量问题数量不等于异常证据数量，也不等于商品数量；一条证据可以有多个问题。

一行代表：一个统一算法批次内，一条证据的一个字段的一种质量/用途/准入问题。

主键：`algorithm_batch_version + evidence_id + field_name + issue_code`。无具体单字段的行级问题，`field_name` 固定写 `__ROW__`；主键列不允许 NULL。同一问题重复检出更新审计时间，不新增重复问题。

该表是本批次当前问题明细，不维护独立问题版本。历史原始证据和每次输入锁定/修正记录保留于原始快照及 `mart_external_batch_input_manifest`。实际建表、生产样例与问题统计尚需数据开发验收。

## 2. 完整字段合同

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 统一算法批次版本 | `algorithm_batch_version` | varchar(32) | 必须 | `dwd_external_evidence_normalized.algorithm_batch_version` | 固定 `BATCH_YYYYMM`，不按检出次数升号 |
| 证据 ID | `evidence_id` | varchar(128) | 必须 | `dwd_external_evidence_normalized.evidence_id` | 与标准证据按 BATCH＋证据 ID 关联 |
| 问题字段 | `field_name` | varchar(128) | 必须 | 字段校验规则 | 正式英文字段名；行级问题为 `__ROW__` |
| 问题代码 | `issue_code` | varchar(64) | 必须 | 本合同问题代码登记 | 稳定机器代码，不能把中文长描述作为代码 |
| 问题层级 | `issue_layer` | varchar(32) | 必须 | 问题规则分类 | 分开技术质量、允许用途、商品映射、业务准入及信息统计 |
| 严重性 | `severity` | varchar(16) | 必须 | 校验规则 | ERROR/WARN/INFO；不单独决定整个算法停跑 |
| 问题状态 | `issue_status` | varchar(32) | 必须 | 自动校验/修正复算 | OPEN/RESOLVED/INFORMATIONAL；不是业务批准按钮 |
| 来源 ID | `source_id` | varchar(128) | 必须 | `dwd_external_evidence_normalized.source_id` | 用于来源对账 |
| 数据集 ID | `dataset_id` | varchar(128) | 必须 | `dwd_external_evidence_normalized.dataset_id` | 用于数据集对账 |
| 原始快照 ID | `raw_snapshot_id` | varchar(128) | 必须 | `dwd_external_evidence_normalized.raw_snapshot_id` | 回溯原始响应 |
| 原始行定位 | `raw_record_locator` | varchar(1024) | 必须 | `dwd_external_evidence_normalized.raw_record_locator` | 找回原始字段 |
| 原始字段值 | `raw_field_value` | string | 可选 | 原始快照被检字段 | 原样保存 NULL/缺报/混合单位等差别；敏感凭据不落库 |
| 预期合同约束 | `expected_constraint` | string | 必须 | 本字段合同及解释规则 | 写清期望单位、日期、唯一性或允许值，不把假设写成已确认事实 |
| 处理动作 | `handling_action` | varchar(32) | 必须 | 自动降级规则 | 留空数值、隔离、食品排除、信息统计或重处理 |
| 受限用途列表 | `blocked_uses_json` | json | 必须 | 用途准入校验 | 标准证据允许用途枚举的字符串数组，表示本问题阻断哪些用途；无业务阻断写 `[]` |
| 解释规则 ID | `interpretation_rule_id` | varchar(128) | 可选 | `dim_external_evidence_interpretation_rule.rule_id` | 有实际命中或发生冲突的规则时记录；多规则冲突具体 ID 进入依据对象 |
| 校验依据 | `basis_json` | json | 必须 | 字段校验过程 | 对象，至少含 contract_path、raw_snapshot_id、raw_record_locator；规则场景补 rule_ids 数组、basis_url、basis_hash；不得只写“系统判断” |
| 首次检出时间 | `detected_at` | datetime | 必须 | 质量任务 | UTC；同一主键首次检出后不变 |
| 最近复算时间 | `checked_at` | datetime | 必须 | 质量任务 | UTC；表示当前问题判定时间 |
| 本次运行 ID | `run_id` | varchar(64) | 必须 | 标准化调度 | 审计实际运行，不生成新的业务版本 |
| 处理说明 | `resolution_note` | string | 可选 | 自动处理或结果复核记录 | 说明新依据、源修正或持续隔离原因；不能用备注取代状态字段 |

## 3. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `issue_layer` | 问题层级 | `TECHNICAL` | 技术质量 | 数值、单位、时间或血缘不满足适用字段合同 |
| `issue_layer` | 问题层级 | `USAGE` | 用途约束 | 用途规则、覆盖率或延迟门槛未确定/未达到 |
| `issue_layer` | 问题层级 | `MAPPING` | 商品映射 | 商品身份、类别或内部分类未可靠映射 |
| `issue_layer` | 问题层级 | `ADMISSION` | 食品业务准入 | 范围排除或业务准入约束 |
| `issue_layer` | 问题层级 | `INFORMATIONAL` | 信息统计 | 表头、休市或源说明等非业务记录 |
| `severity` | 严重性 | `ERROR` | 错误 | 相关字段或用途不可计算；影响单条还是整批按具体合同判断 |
| `severity` | 严重性 | `WARN` | 警示 | 可保留证据，但存在用途降级或需要结果核查 |
| `severity` | 严重性 | `INFO` | 信息 | 仅处理统计，不当作业务需修复异常 |
| `issue_status` | 问题状态 | `OPEN` | 未解决 | 缺依据、字段异常或用途未开放仍存在 |
| `issue_status` | 问题状态 | `RESOLVED` | 已解决 | 有依据的补全/修正后字段复算通过 |
| `issue_status` | 问题状态 | `INFORMATIONAL` | 仅记录信息 | INFO 类非业务问题 |
| `handling_action` | 处理动作 | `KEEP_NULL` | 缺失数值保持空 | 源缺报或无法合法解析，不补 0 |
| `handling_action` | 处理动作 | `QUARANTINE` | 隔离受影响用途 | 身份、单位、日期或规则尚未确定 |
| `handling_action` | 处理动作 | `EXCLUDE_FOOD` | 排除食品业务 | 已确证花卉或其他明确非食品 |
| `handling_action` | 处理动作 | `INFO_ONLY` | 只计处理统计 | 表头、休市等信息记录 |
| `handling_action` | 处理动作 | `REPROCESS` | 按锁定规则重处理 | 源修正可由原锁定规则解释时沿用原 BATCH；新增字典/单位/日期/用途规则默认下一完整月启用，不自动改历史规则 |
| `issue_code` | 问题代码 | `IDENTITY_MISSING` | 商品身份缺失 | 商品名缺失且权威代码字典未补全 |
| `issue_code` | 问题代码 | `UNKNOWN_CATEGORY` | 类别未知 | 不能证明食品/花卉类别，不自动排除 |
| `issue_code` | 问题代码 | `CATEGORY_MAPPING_GAP` | 内部分类缺口 | 外部身份可知但无可靠内部小分类 |
| `issue_code` | 问题代码 | `UNIT_UNRESOLVED` | 单位未确定 | 单位缺失、冲突或混合表头无逐商品依据 |
| `issue_code` | 问题代码 | `DATE_UNRESOLVED` | 日期未确定 | 相对日期无锚点/区间，或变化率基期不明 |
| `issue_code` | 问题代码 | `SOURCE_NOT_REPORTED` | 来源未报告 | 原始值为来源缺报标识 |
| `issue_code` | 问题代码 | `INVALID_VALUE` | 非法数值 | 解析失败、绝对价量负数等 |
| `issue_code` | 问题代码 | `INFO_RECORD` | 信息记录 | 表头、休市或非业务说明 |
| `issue_code` | 问题代码 | `RULE_CONFLICT` | 规则冲突 | 同一适用范围/有效期/优先级命中矛盾解释 |
| `issue_code` | 问题代码 | `DUPLICATE_OBSERVATION` | 重复观测 | 同次读取同一观测存在重复或修订候选，必须去重选择 |
| `issue_code` | 问题代码 | `COVERAGE_UNKNOWN` | 覆盖率未知 | 无可复算的预期观测分母 |
| `issue_code` | 问题代码 | `COVERAGE_BELOW_THRESHOLD` | 覆盖不足 | 按已锁定分母和门槛计算后未达到最低覆盖率 |
| `issue_code` | 问题代码 | `DELAY_THRESHOLD_MISSING` | 延迟门槛未定 | 需要时效门槛的用途尚未确定最大延迟 |
| `issue_code` | 问题代码 | `SOURCE_STALE` | 数据过期 | 按已确定数据期和已锁定延迟门槛判定超期 |
| `issue_code` | 问题代码 | `BUSINESS_USE_UNCONFIRMED` | 用途未确定 | 商务趋势等业务用途未登记生效规则 |
| `issue_code` | 问题代码 | `OUT_OF_FOOD_SCOPE` | 非食品范围 | 已有权威类别证明为花卉或其他明确非食品 |
| `issue_code` | 问题代码 | `LINEAGE_MISSING` | 来源血缘缺失 | 原始响应、原始行定位或依据无法回溯 |
| `issue_code` | 问题代码 | `OUTSIDE_BATCH_WINDOW` | 超出批次边界 | 真实数据期超过当批月末，或正常输入的采集/来源发布时间超过 cutoff |
| `blocked_uses_json` | 受限用途列表 | `ABSOLUTE_PRICE` | 绝对价格受限 | 本问题阻断绝对价格比较 |
| `blocked_uses_json` | 受限用途列表 | `TREND` | 趋势受限 | 本问题阻断相应趋势计算 |
| `blocked_uses_json` | 受限用途列表 | `SUPPLY` | 供需受限 | 本问题阻断数量/供需计算 |
| `blocked_uses_json` | 受限用途列表 | `HISTORICAL_REFERENCE` | 历史资料受限 | 无血缘或明确禁用等导致资料也不可使用 |
| `blocked_uses_json` | 受限用途列表 | `CANDIDATE_ATTRIBUTE` | 候选属性受限 | 本问题阻断具体商品属性来源用途 |

## 4. 聚合规则和自动运行边界

1. 问题行数使用本表主键计数；异常证据数按 BATCH＋证据 ID 去重；技术问题、业务用途问题和 INFO 分开统计。
2. 生成标准证据 `quality_status` 时，只聚合该证据仍 OPEN 的适用 TECHNICAL 问题；其他层分别影响匹配、准入和用途，不能混成一个 PASS 即全通过的开关。
3. 关联标准证据前，先按 `algorithm_batch_version + evidence_id` 汇总问题代码、问题数及受限用途，确保每条证据仅一行；禁止用问题明细直接关联价量明细后 SUM 或 COUNT。
4. INFO 不进入业务异常待修数、缺报率或覆盖率分母。缺报率的分子是源缺报观测数，分母是同源同指标本应有报告的明确观测集合，不是本表问题数。
5. 算法按已发布规则自动处理。业务结果复核可补充规则依据或提出源修正，不要求对每条 OPEN 问题人工点通过才能让其他有效来源计算。

## 5. 缺失、降级和验收

| 场景 | 处理 |
|---|---|
| 主键重复 | 阻断本表发布，修复重复更新；不任意保留一行 |
| 一条证据多个问题 | 分字段/代码保留，逐证据汇总后关联；问题总数可以大于证据总数 |
| 没有问题 | 本表可以无该证据记录；标准证据质量需由完整适用校验得出，不能以未运行校验当 PASS |
| 未取得官方字典 | 身份问题保持 OPEN，原值和原始快照保留；技术侧获取/验证字典后重处理 |
| 花卉与未知类别共批 | 花卉记范围排除，未知类别记隔离，两者不能合并为“花卉异常”删除 |
| 问题修复 | 原锁定规则下的源修正有依据且复算通过后 RESOLVED，随本次完整包原子发布；新增规则默认下一完整月启用。源修正前后引用及本次质量明细快照由输入锁定清单保留 |

验收提交主键重复数、逐层问题数、去重证据数、INFO 统计、一个证据至少两种问题样例、关联前后价量/证据行数不变证明，以及 `-`/0/负数/未知单位/未知日期/花卉/类别未知的处理结果。未有这些生产证据时不标记生产验收通过。

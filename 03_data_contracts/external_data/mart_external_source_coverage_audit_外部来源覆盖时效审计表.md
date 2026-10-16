# 外部来源覆盖时效审计表

正式表名：`mart_external_source_coverage_audit`。

一行代表：一个统一算法批次的一次运行，一个来源/数据集/市场/覆盖范围/指标角色/用途在一个评价窗口的覆盖、缺报和时效结果。属于正式审计与能力闸门；下游可读取，不能当候选结果。

主键：`algorithm_batch_version + run_id + source_id + dataset_id + source_market + coverage_scope_key + metric_type + metric_role + usage + period_start + period_end`。

## 1. 完整字段合同

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 统一算法批次版本 | `algorithm_batch_version` | varchar(32) | 必须 | 全链路调度 | BATCH_YYYYMM，进入主键 |
| 运行ID | `run_id` | varchar(64) | 必须 | external_trend_run.run_id | 本次运行审计，按发布包读取，不能多运行累加 |
| 来源ID | `source_id` | varchar(128) | 必须 | external_trend_run.source_snapshot_json来源登记 | 来源无返回也必须有审计行 |
| 数据集ID | `dataset_id` | varchar(128) | 必须 | 来源注册及dim_external_evidence_interpretation_rule.dataset_id | 原始数据集身份 |
| 来源市场 | `source_market` | varchar(64) | 必须 | 来源注册 | 真实数据市场 |
| 覆盖范围键 | `coverage_scope_key` | varchar(128) | 必须 | 覆盖步骤C1规范范围定义SHA256 | 完整应报业务维度的范围键；不是内部虚构品类 |
| 指标类型 | `metric_type` | varchar(64) | 必须 | 来源登记/标准证据metric_type | 一个指标；不混价量 |
| 指标角色 | `metric_role` | varchar(64) | 必须 | 来源登记/标准证据metric_role | 会员、日常、促销等分别统计 |
| 业务用途 | `usage` | varchar(64) | 必须 | 当批用途登记 | ABSOLUTE_PRICE/TREND/SUPPLY/CANDIDATE_ATTRIBUTE/HISTORICAL_REFERENCE |
| 评价周期开始 | `period_start` | date | 必须 | 当批来源覆盖参数 | 审计评价窗口起点，不冒充未知交易日 |
| 评价周期结束 | `period_end` | date | 必须 | 当批来源覆盖参数 | 审计评价窗口终点，不超过月末 |
| 应报集合引用 | `expected_set_reference` | string | 条件必须 | C1按expected_observation_scope_json展开并冻结 | 精确应报键列表的受控不可变引用；未知NULL |
| 应报集合哈希 | `expected_set_hash` | varchar(64) | 条件必须 | C1规范应报键排序SHA256 | 复算分母与排除日历，未知NULL |
| 应报观测数 | `expected_observation_count` | bigint | 条件必须 | C1精确应报集合COUNT DISTINCT | 未知NULL；休市不应报按日历排除 |
| 实报观测数 | `reported_observation_count` | bigint | 必须 | C2应报集合内收到记录按观测键去重 | 包括合法值、源缺报和隔离记录；无返回真实0 |
| 有效观测数 | `valid_observation_count` | bigint | 必须 | C3逐用途核实关键字段的去重观测 | 目标用途物理语义合格数，不含业务许可和整体门槛；避免循环 |
| 源缺报观测数 | `source_missing_value_count` | bigint | 必须 | C2 value_status=SOURCE_NOT_REPORTED去重 | 例如-；不重复累计一个观测多个问题 |
| 已报无效观测数 | `invalid_reported_count` | bigint | 必须 | C3对已报观测分类 | 身份/单位/时间/值等物理语义不满足，不含源缺报 |
| 未收到观测数 | `absent_observation_count` | bigint | 条件必须 | C2 expected−reported | 未知分母NULL；不能等同已返回的- |
| 范围外观测数 | `unexpected_observation_count` | bigint | 必须 | C2收到键不在应报集合 | 不扩大分母；分母未知时只记未分类收到记录并写诊断 |
| 处理信息记录数 | `info_record_count` | bigint | 必须 | C2原始INFO行去重 | 不进入应报、实报或异常业务分母 |
| 实报率 | `reporting_rate` | decimal(18,8) | 条件必须 | C4 reported/expected | 分母未知或0时NULL |
| 有效覆盖率 | `valid_coverage_rate` | decimal(18,8) | 条件必须 | C4 valid/expected | 技术PASS率不能代替此值 |
| 源缺报率 | `source_missing_value_rate` | decimal(18,8) | 条件必须 | C4 source_missing_value/expected | 未知或0分母NULL，未收到另统计 |
| 时效计算依据 | `delay_basis` | varchar(32) | 必须 | 当批COVERAGE规则delay_basis | 与证据时间含义一致；不适用写NOT_APPLICABLE |
| 时效评价日期 | `freshness_reference_date` | date | 必须 | 当批COVERAGE规则或批次月末 | 同批重跑不读今天 |
| 最新有效业务日期 | `latest_valid_business_date` | date | 条件必须 | C5按delay_basis取有效观测最新日期 | 统计期末、零售实测日或发布时间；未知NULL |
| 实际数据延迟天数 | `actual_delay_days` | int | 条件必须 | C5 max(0,评价日−最新有效业务日期) | 静态不适用或未知NULL；不取采集日替代交易日 |
| 最低覆盖率 | `minimum_coverage_rate` | decimal(18,8) | 条件必须 | 当批COVERAGE规则minimum_coverage_rate | 未确认NULL，不自设90%/95% |
| 最大延迟天数 | `max_delay_days` | int | 条件必须 | 当批COVERAGE规则max_delay_days | 未确认NULL，不自设1/2发布周期 |
| 覆盖判定状态 | `coverage_status` | varchar(32) | 必须 | C4门槛比较 | 见状态约束 |
| 时效判定状态 | `freshness_status` | varchar(32) | 必须 | C5门槛比较 | 见状态约束 |
| 用途闸门状态 | `usage_gate_status` | varchar(32) | 必须 | C6用途/逐记录语义/覆盖/时效 | 见状态约束，不替代商品候选准入 |
| 用途规则ID | `usage_rule_id` | varchar(128) | 条件必须 | dim_external_evidence_interpretation_rule.rule_id | 对应USAGE规则；未发布NULL |
| 覆盖规则ID | `coverage_rule_id` | varchar(128) | 条件必须 | dim_external_evidence_interpretation_rule.rule_id | 对应COVERAGE规则；未发布NULL |
| 诊断原因 | `diagnostic_reason` | string | 条件必须 | C1-C6执行步骤 | 未知范围、分母、门槛、时间及关闭原因 |
| 计算时间 | `calculated_at` | datetime | 必须 | 系统生成 | UTC运行审计 |

## 2. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `coverage_status` | 覆盖判定状态 | `PASS` | 通过 | 分母>0且有效覆盖率≥已登记门槛 |
| `coverage_status` | 覆盖判定状态 | `BELOW_THRESHOLD` | 覆盖不足 | 有效覆盖率低于已登记门槛 |
| `coverage_status` | 覆盖判定状态 | `DENOMINATOR_UNKNOWN` | 分母未知 | 无权威应报集合 |
| `coverage_status` | 覆盖判定状态 | `THRESHOLD_UNSET` | 门槛未登记 | 有分母但无已发布覆盖率参数 |
| `coverage_status` | 覆盖判定状态 | `NOT_APPLICABLE` | 不适用 | 已确证应报集合为0或该逐记录用途不需覆盖门槛 |
| `freshness_status` | 时效判定状态 | `PASS` | 通过 | 实际延迟≤已登记上限 |
| `freshness_status` | 时效判定状态 | `STALE` | 超时效 | 实际延迟大于上限 |
| `freshness_status` | 时效判定状态 | `DATE_UNKNOWN` | 业务日期未知 | 无有依据的时效日期 |
| `freshness_status` | 时效判定状态 | `THRESHOLD_UNSET` | 门槛未登记 | 无已发布最大延迟 |
| `freshness_status` | 时效判定状态 | `NOT_APPLICABLE` | 不适用 | 静态事实且无趋势用途 |
| `usage_gate_status` | 用途闸门状态 | `OPEN` | 允许该用途 | 用途已发布、逐记录语义及适用覆盖/时效门槛均通过 |
| `usage_gate_status` | 用途闸门状态 | `CLOSED` | 关闭该用途 | 语义、覆盖或时效明确不通过 |
| `usage_gate_status` | 用途闸门状态 | `UNCONFIRMED` | 用途/门槛未确认 | 允许用途或必要门槛尚未登记 |
| `usage_gate_status` | 用途闸门状态 | `NOT_APPLICABLE` | 无本期观测义务 | 确证应报为0且无可算指标 |
| `usage` | 业务用途 | `ABSOLUTE_PRICE` | 绝对价格 | 同口径价格参考 |
| `usage` | 业务用途 | `TREND` | 趋势 | 同口径趋势 |
| `usage` | 业务用途 | `SUPPLY` | 供需 | 供应/交易数量 |
| `usage` | 业务用途 | `CANDIDATE_ATTRIBUTE` | 候选属性 | 可靠商品事实 |
| `usage` | 业务用途 | `HISTORICAL_REFERENCE` | 历史参考 | 不作同期趋势 |
| `delay_basis` | 时效依据 | `DATA_PERIOD_END` | 统计期末 | 统计价量 |
| `delay_basis` | 时效依据 | `RETAIL_OBSERVED_AT` | 零售观测日 | 零售报价/在架 |
| `delay_basis` | 时效依据 | `SOURCE_PUBLISHED_AT` | 原生发布时间 | 文章事件 |
| `delay_basis` | 时效依据 | `NOT_APPLICABLE` | 不适用 | 静态事实 |
| `metric_role` | 指标角色 | `CURRENT_OFFER` | 当前报价 | 来源只说明当前售价，不自动当日常价 |
| `metric_role` | 指标角色 | `REGULAR_PRICE` | 已确证日常价 | 来源明确非促销常规售价 |
| `metric_role` | 指标角色 | `LIST_PRICE` | 划线/市场价 | 不冒充真实成交价 |
| `metric_role` | 指标角色 | `MEMBER_PRICE` | 会员价 | 有会员资格价格 |
| `metric_role` | 指标角色 | `PROMOTION_PRICE` | 促销价 | 原文明示促销条件 |
| `metric_role` | 指标角色 | `UNSPECIFIED_PRICE` | 未明确价格角色 | 保留原值，相关比较关闭 |
| `metric_role` | 指标角色 | `PRICE_CHANGE_RATE` | 价格变化率 | 独立百分比证据 |
| `metric_role` | 指标角色 | `TRANSACTION_VOLUME` | 交易数量 | 真实交易量 |
| `metric_role` | 指标角色 | `SUPPLY_VOLUME` | 供应数量 | 真实供应或来货量 |
| `metric_role` | 指标角色 | `VOLUME_CHANGE_RATE` | 数量变化率 | 真实数量变化百分比 |
| `metric_role` | 指标角色 | `PERIOD_SALES` | 周期销量 | 有明确销售统计期及单位 |
| `metric_role` | 指标角色 | `CUMULATIVE_SALES` | 累计销量 | 截至时点累计值，不直接加总/差分 |
| `metric_role` | 指标角色 | `POS_RANK` | 榜单序号 | 有榜单、周期和长度说明 |
| `metric_role` | 指标角色 | `STORE_COVERAGE` | 覆盖店数 | 真实覆盖店/点位数，不等于比例 |
| `metric_role` | 指标角色 | `PRODUCT_ATTRIBUTE` | 商品属性 | 名称、规格和卖点事实 |
| `metric_role` | 指标角色 | `TEXT_CLAIM` | 文章结论 | 原生文章或新闻主张 |
| `metric_role` | 指标角色 | `POS_AVERAGE_PRICE` | POS观察均价 | 真实POS统计期平均售价，不能默认当日常标价/促销价 |
| `metric_role` | 指标角色 | `WHOLESALE_REFERENCE_PRICE` | 批发行情参考价 | 有原文明示的批发层级，不给零售SKU直接分三档 |
| `metric_role` | 指标角色 | `PRODUCER_REFERENCE_PRICE` | 产地参考价 | 有原文明示的产地报价，不混零售 |
| `metric_role` | 指标角色 | `RETAIL_REFERENCE_PRICE` | 门市参考价 | 行情中的门市层级参考，不等同具体SKU常规价 |
| `metric_role` | 指标角色 | `MARKET_AVERAGE_REFERENCE_PRICE` | 市场统计均价 | 统计对象/样本明确的市场均价，保留原口径 |
| `metric_role` | 指标角色 | `INFO` | 处理信息 | 表头、休市等 |
| `metric_type` | 指标类型 | `PRICE` | 价格 | 绝对价格 |
| `metric_type` | 指标类型 | `PRICE_CHANGE_RATE` | 价格变化率 | 比例 |
| `metric_type` | 指标类型 | `TRANSACTION_VOLUME` | 交易量 | 数量 |
| `metric_type` | 指标类型 | `SUPPLY_VOLUME` | 供应量 | 数量 |
| `metric_type` | 指标类型 | `VOLUME_CHANGE_RATE` | 量变化率 | 比例 |
| `metric_type` | 指标类型 | `PRODUCT_FACT` | 商品事实 | 属性 |
| `metric_type` | 指标类型 | `TEXT_CLAIM` | 文本结论 | 文章 |
| `metric_type` | 指标类型 | `INFO` | 处理信息 | 信息统计 |
| `metric_type` | 指标类型 | `SALES_QUANTITY` | 商品销量 | PERIOD_SALES/CUMULATIVE_SALES，不能充当Binomial次数 |
| `metric_type` | 指标类型 | `POS_RANK` | POS名次 | 序号而非销量，越小越靠前 |
| `metric_type` | 指标类型 | `STORE_COVERAGE` | 覆盖门店数 | 店/点位数；无总数不计算比例 |

## 3. ETL、聚合安全和降级

C1从锁定来源注册、发布日历、权威商品/市场范围与指标角色展开精确应报集合，排除有依据的不应报日及食品范围外对象；不按实际成功采集列表构造分母，不盲做商品×市场笛卡尔积。应报集合在本run输入资产冻结；整个来源失败仍产审计行。未知集合时expected及所有依赖比率NULL，已收到记录按唯一键统计并在diagnostic_reason说明无法判定范围内/范围外；此时reported为全部去重收到业务观测，unexpected=0仅表示尚未分类，不证明不存在范围外记录。

C2先按观测键选唯一源修订，再统计收到记录；缺报标识、隔离记录均属于“收到”，不能只数SELECTED。无身份/时间无法构造观测键的收到行单独记诊断和处理行数，不强凑入应报键。C3只按该用途物理语义（身份/单位/时间/值）将已收到业务观测互斥分为valid、source_missing_value、invalid_reported；业务用途许可另由C6判断，未确认许可不将物理合格数伪造为0，reported=三者之和；一个字段多个问题不重复扣减。C4覆盖率分母为expected，不是技术PASS条数或收到记录数。expected>0时absent=expected−reported（范围内计数）；expected=0时比率NULL、NOT_APPLICABLE。INFO不计业务分母。

C5按delay_basis计算实际业务日期至冻结评价日的差，不使用今天或采集日代交易日。C6先做逐记录语义判定，再比较已登记整体门槛；valid计数不反向依赖OPEN，避免循环。门槛或用途未知为UNCONFIRMED；缺报/单位不明/相对日期不能因整体覆盖通过而被洗成有效。逐记录静态属性可不依赖整体覆盖与时效，但须身份/来源/适用期及CANDIDATE_ATTRIBUTE用途有依据。

正式读取只取external_trend_run定位的单个BATCH发布run；失败运行审计保留但不计入当前业务。真实值0与未知NULL分开。未知业务门槛不得用建议值代填。

## 4. 验收样例

应报10个观测，收到8个：6有效、1源缺报、1已报无效；未收到2。reporting_rate=0.8、valid_coverage_rate=0.6、source_missing_value_rate=0.1。源缺报与未收到分别为1和2。若一个无效观测有三个问题，仍只计1无效。门槛未登记时coverage_status=THRESHOLD_UNSET、usage_gate_status=UNCONFIRMED，不把0.6自动判为可用。来源完全失败但应报10时reported=valid=0、absent=10；应报分母未知时expected/absent/各比率NULL。验收还覆盖日常/会员/促销分别统计、休市应报为0、静态属性不要求交易期及同批重跑评价日不漂移。

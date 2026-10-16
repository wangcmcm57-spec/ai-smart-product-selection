# 外部证据解释规则表

## 1. 表定位、粒度和主键

正式表名：`dim_external_evidence_interpretation_rule`。

用途：将官方商品代码字典、数值单位、日期解释、食品范围、允许用途、覆盖率/延迟及来源修订选择沉淀为可追溯参数，供外部采集标准化和算法 07 自动读取。不用商品属性字典代替官方代码字典，不把未经核实的解释写成来源事实。

一行代表：一个统一算法批次内，一条具有明确适用条件、依据及有效期的外部证据解释规则快照。

主键：`algorithm_batch_version + rule_id`。同一批次、同类型、同来源/数据集/市场/指标、同匹配条件、有效期重叠且同优先级不能有冲突的 ACTIVE 规则。

这是本项目当批正式参数表，包含唯一业务批次 `algorithm_batch_version = BATCH_YYYYMM`；不另建规则业务版本。上游官方字典自身的发布日期/资产标识仅是来源追溯。规则首次随当批输入锁定，之后完整内容及哈希不变；重跑历史批次读取原锁定规则。新规则默认下一完整月批次生效。

当前合同只定义结构和执行边界，未导入权威完整字典，未声称生产规则已发布或样例已验收。字段中的实例仅用于理解，不代表实际启用的数据。

## 2. 已确认范围和未确认边界

算法 07 面向食品业务；已由权威类别/代码字典确定为花卉的记录排除食品业务，原始快照保留。类别未知记录独立隔离，不按花卉删除，不按代码前缀或相近名称推断花卉类别。

获取、验证官方商品代码字典及逐商品单位/日期解释依据属于技术交付验收。业务不需要逐代码补品名，也不需要逐条审批标准证据。未取得依据的解释规则保持 DRAFT，不自动启用。

仍需业务登记的参数集中为：商务百分比的趋势允许用途；香港额外业务用途/可接受时效；按来源用途确定的最低覆盖率、最大延迟及规则/发布责任。未确认时保持相关用途隔离或明确的历史资料用途，不能用推荐选项默认开放。

## 3. 完整字段合同

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 统一算法批次版本 | `algorithm_batch_version` | varchar(32) | 必须 | 全链路调度 | 固定 `BATCH_YYYYMM`，正式参数与算法结果共用 |
| 规则 ID | `rule_id` | varchar(128) | 必须 | 规则导入任务 | 本批次稳定规则标识，不带独立业务版本含义 |
| 规则类型 | `rule_type` | varchar(32) | 必须 | 规则适用分类 | 身份、单位、日期、范围、用途、覆盖/延迟或修订策略 |
| 来源 ID | `source_id` | varchar(128) | 必须 | 原始来源配置或依据 | 与原始快照 source_id 一致；全来源食品范围规则使用明确值 `__ALL__` |
| 数据集 ID | `dataset_id` | varchar(128) | 必须 | 原始来源配置或依据 | 具体数据集；通用食品范围规则可为 `__ALL__`，不能任意跨数据集套单位 |
| 来源市场 | `source_market` | varchar(64) | 必须 | 原始来源配置或依据 | 地区/市场范围；全局食品规则为 `__ALL__`，其他通用范围必须有依据 |
| 指标角色 | `metric_role` | varchar(64) | 必须 | 规则适用范围登记 | 对应标准证据角色或__ALL__；价格角色有不同用途/口径时必须分别登记 |
| 指标类型 | `metric_type` | varchar(64) | 必须 | 本规则适用指标 | 标准证据指标枚举或 `__ALL__`；单位规则必须针对具体数值指标 |
| 匹配方式 | `match_method` | varchar(32) | 必须 | 规则适用条件 | 精确代码、精确原始名称、权威类别或数据集范围，不做模糊相似匹配 |
| 匹配商品代码 | `match_product_code` | varchar(128) | 条件必须 | 权威字典原始代码 | PRODUCT_CODE 时必填，原样保留来源代码 |
| 匹配原始名称 | `match_product_name` | varchar(512) | 条件必须 | 原始报表商品名 | PRODUCT_NAME 时必填；“其中：”等原始限定不可擅自删除 |
| 匹配权威类别 | `match_category_name` | varchar(256) | 条件必须 | 官方分类字典或已确认食品范围 | CATEGORY 时必填；未确证类别不能命中 |
| 来源数据适用期开始 | `source_period_start` | date | 可选 | 规则依据的适用数据期 | 仅作用于依据明确的历史报表/商品时期；未限制可为 NULL |
| 来源数据适用期结束 | `source_period_end` | date | 可选 | 规则依据的适用数据期 | 右闭；日期未知时不能命中一个必须有明确数据期的限制规则 |
| 优先级 | `priority` | int | 必须 | 规则导入校验 | 非负整数，大值优先；同类型同匹配范围优先级冲突不得任取一条 |
| 标准外部商品名 | `resolved_product_name` | varchar(512) | 条件必须 | PRODUCT_IDENTITY 权威字典 | 身份补全结果；不能用商品代码本身当品名 |
| 标准外部类别 | `resolved_category_name` | varchar(256) | 条件必须 | PRODUCT_IDENTITY 权威字典 | 官方类别；和内部小分类不是同一个字段 |
| 原始单位匹配文本 | `source_unit_text` | varchar(256) | 条件必须 | UNIT 原始列头/表注及官方说明 | 记录本规则解释的实际单位文本，包括歧义原表头 |
| 标准单位 | `metric_unit` | varchar(64) | 条件必须 | UNIT 单位依据 | 例如 CNY/kg、TWD/kg、kg、ratio；绝对价与百分比规则分开 |
| 币种 | `currency_code` | char(3) | 条件必须 | UNIT 原始币种及官方说明 | 价格规则必须明确；不自动汇率转换 |
| 单位变换因子 | `unit_conversion_factor` | decimal(24,10) | 条件必须 | UNIT 可解释换算 | 标准值＝解析原值×因子；百分号转比例为 0.01，恒等为 1；无依据不得填 |
| 日期变换定义 | `date_transform_json` | json | 条件必须 | DATE 官方日期说明 | 严格对象结构见第 4 节；明确锚点、时区、相对偏移及区间，不能只写“按昨天” |
| 食品范围判定 | `food_scope_decision` | varchar(32) | 条件必须 | BUSINESS_SCOPE 已确认业务范围及权威类别 | FOOD/FLOWER/OTHER_NON_FOOD；未知类别不生成肯定判定 |
| 允许用途列表 | `allowed_uses_json` | json | 条件必须 | USAGE 来源能力及已确认业务用途 | 标准证据用途字符串数组，未确认写空数组且规则 DRAFT；不能默认全用途 |
| 预期观测范围 | `expected_observation_scope_json` | json | 条件必须 | COVERAGE 来源实际发布范围和调度期 | 对象结构见第 4 节，用于生成独立于实际已抓取记录的分母 |
| 最低覆盖率 | `minimum_coverage_rate` | decimal(10,8) | 可选 | COVERAGE 业务确认参数 | 0～1；未确认 NULL，不自定阈值 |
| 最大数据延迟天数 | `max_delay_days` | int | 可选 | COVERAGE 业务确认参数 | 非负整数，按delay_basis的有依据时点到本批固定评价日计算；未知 NULL |
| 时效计算依据 | `delay_basis` | varchar(32) | 条件必须 | COVERAGE业务口径及来源实际时间含义 | DATA_PERIOD_END/RETAIL_OBSERVED_AT/SOURCE_PUBLISHED_AT/NOT_APPLICABLE；未知时不启用最大延迟判断 |
| 时效评价日期 | `freshness_reference_date` | date | 条件必须 | COVERAGE 当批调度锁定 | 当批固定评价日，重跑不随当前日期变化 |
| 修订选择方法 | `revision_selection_method` | varchar(32) | 条件必须 | REVISION 官方修订语义 | 仅同内容去重或按来源有依据的修订序选择；不能按采集时间猜修订 |
| 修订排序定义 | `revision_order_json` | json | 条件必须 | REVISION 来源修订说明 | 结构见第 4 节；来源真正提供的字段及类型/排序，不创造修订号 |
| 依据类型 | `basis_type` | varchar(32) | 必须 | 规则依据登记 | 官方发布、已确认业务规则或 PENDING；PENDING 只能为 DRAFT |
| 依据链接 | `basis_url` | string | 条件必须 | 官方字典、单位说明、日期说明 | OFFICIAL_PUBLISHED 必填，链接应定位直接依据而非搜索页 |
| 依据文件或确认记录 | `basis_reference` | string | 条件必须 | 已确认业务范围/用途/参数记录 | BUSINESS_CONFIRMED 必填，写正式路径或可访问记录标识，不伪造来源确认 |
| 依据快照 ID | `basis_raw_snapshot_id` | varchar(128) | 条件必须 | `ods_external_source_raw_snapshot.raw_snapshot_id` | 官方依据必有可追溯原始快照；业务依据可保存受控确认记录 |
| 依据短摘录 | `basis_quote` | string | 条件必须 | 依据原文 | ACTIVE 时必填；DRAFT 未取得依据时 NULL，不伪造引文；只保存必要短摘录 |
| 依据内容哈希 | `basis_hash` | varchar(64) | 条件必须 | 依据快照/确认记录内容 SHA-256 | ACTIVE 时必填，确保依据可复核；DRAFT 无依据时 NULL，不写虚假哈希 |
| 源资产追溯标识 | `source_asset_reference` | varchar(256) | 可选 | 官方字典或源文件自身标识 | 来源发布日期/资产 ID 等，仅追溯，不构成第二套算法版本 |
| 生效开始日期 | `effective_start_date` | date | 条件必须 | 规则发布登记 | ACTIVE 时必填，随当前 BATCH 锁定；未确定的 DRAFT 可为 NULL，不据此启用 |
| 生效结束日期 | `effective_end_date` | date | 可选 | 规则发布登记 | 右闭，未结束 NULL；历史冻结记录不随当前资产修改 |
| 规则状态 | `rule_status` | varchar(32) | 必须 | 规则依据及参数校验 | ACTIVE/DRAFT/DISABLED；属于规则发布状态，不是逐条证据人工批准 |
| 责任人或责任角色 | `owner` | varchar(256) | 条件必须 | 规则维护责任登记 | 覆盖/时效/用途发布规则必须明确；未知不编造人员 |
| 规则内容哈希 | `rule_hash` | varchar(64) | 必须 | 规则冻结任务 | 对除 rule_hash 自身、run_id/locked_at 外的全部规则业务字段规范化 SHA-256 |
| 冻结运行 ID | `run_id` | varchar(64) | 必须 | 当批初始化调度 | 审计实际运行，不改变 BATCH |
| 冻结时间 | `locked_at` | datetime | 必须 | 规则冻结任务 | UTC；历史重跑不改原规则快照 |

## 4. 条件字段和 JSON 合同

| 规则类型 | 必填输出/参数 | 其余类型专属字段 |
|---|---|---|
| PRODUCT_IDENTITY | 精确商品代码或精确原名、resolved_product_name、resolved_category_name及官方字典依据 | 不相关单位/日期/用途参数 NULL |
| UNIT | source_unit_text、metric_unit、unit_conversion_factor；PRICE 还必须 currency_code | 不相关字段 NULL；重量与体积不可无依据转换 |
| DATE | date_transform_json、具体数据集/来源市场和日期说明依据 | 不相关字段 NULL |
| BUSINESS_SCOPE | 权威类别匹配、food_scope_decision、业务范围确认依据 | 全局食品规则可匹配已确证 FLOWER；无类别不命中 |
| USAGE | allowed_uses_json、具体来源/数据集/指标、用途依据、owner | 历史资料与四种业务计算用途分别登记 |
| COVERAGE | expected_observation_scope_json、freshness_reference_date；涉及开放门槛的最低覆盖率/最大延迟及 owner | 未确认门槛保留 NULL/DRAFT，不当作 0 或无限制 |
| REVISION | revision_selection_method；来源修订排序方法还必须 revision_order_json | 没有来源修订语义时只能同内容去重 |

`date_transform_json` 对象必须含 `kind`、`timezone`、`observation_period` 和 `comparison_period`：

- `kind` 仅允许 `ABSOLUTE`、`RELATIVE_DAY`、`RELATIVE_WEEK`。ABSOLUTE 的 observation_period 含原始开始/结束字段路径和明确格式；不以修订字段冒充数据字段。
- RELATIVE_DAY 的 observation_period 含 `anchor_field_path`、`anchor_basis`、整数 `offset_days` 和正整数 `length_days`。锚点必须来自来源明确解释的字段，不能默认用 captured_at。
- RELATIVE_WEEK 另含整数 `offset_weeks`、1～7 的 `week_start_iso_day` 和正整数 `length_days`；只有官方明确 Last Week 含义时才登记。
- `timezone` 为有依据的 IANA 时区。时间先在该来源时区确定数据日期；存储时间戳转换 UTC，不改变业务日期。
- `comparison_period` 为 NULL 或对象。变化率用途必须有该对象，含 `method`（仅 `SOURCE_FIELDS` 或 `EXPLICIT_OFFSETS`）。SOURCE_FIELDS 列原始基期开始/结束路径及格式；EXPLICIT_OFFSETS 给出相对观测期的整数 day_offset 或 week_offset、区间长度及官方依据。不能只凭“环比”字样填推测周期；不支持的周期保持未解析，不使用固定天数代替自然月。
- `anchor_basis` 和 comparison_period 的依据均能定位本规则 basis_raw_snapshot_id/依据摘录；任何必要成员缺失，规则不能 ACTIVE。

`expected_observation_scope_json` 对象含 `source_id`、`dataset_id`、`source_market`、`metric_type`、`metric_role`、`usage`、`period_start`、`period_end`、`reporting_calendar`、`product_codes`、`market_codes`、`excluded_non_reporting_periods` 及 `basis_reference`。商品/市场是来源定义的精确列表或受控字典引用；发布日历和休市/不报告区间有依据；不能用实际采集成功记录生成分母。若来源无法提供完整预期范围，不生成此对象，覆盖率 NULL。

`revision_order_json` 对象含 `field_path`、`value_type`、`order`、`basis_reference`。value_type 仅 `INTEGER`、`DATETIME` 或 `ORDERED_LIST`；ORDERED_LIST 还含明确有序 `values` 数组；order 固定 `MAX_IS_NEWER`。必须有官方修订含义，不能把普通采集时间用作字段。相同最高修订但内容冲突时隔离，不任取一条。

## 5. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `rule_type` | 规则类型 | `PRODUCT_IDENTITY` | 商品身份 | 权威代码/原名补品名类别 |
| `rule_type` | 规则类型 | `UNIT` | 单位解释 | 数值单位、币种及因子 |
| `rule_type` | 规则类型 | `DATE` | 日期解释 | 明确交易期/基期和相对日期含义 |
| `rule_type` | 规则类型 | `BUSINESS_SCOPE` | 食品范围 | 已确证类别的食品范围判断 |
| `rule_type` | 规则类型 | `USAGE` | 允许用途 | 来源证据允许用于哪些业务 |
| `rule_type` | 规则类型 | `COVERAGE` | 覆盖/时效参数 | 预期分母、最低覆盖率和最大延迟 |
| `rule_type` | 规则类型 | `REVISION` | 修订选择 | 同观测多份来源内容的选取规则 |
| `match_method` | 匹配方式 | `PRODUCT_CODE` | 精确代码 | 来源/数据集/市场及原始代码完全匹配 |
| `match_method` | 匹配方式 | `PRODUCT_NAME` | 精确原始名称 | 原始名称完全匹配，保留限定前缀 |
| `match_method` | 匹配方式 | `CATEGORY` | 已确证类别 | 权威字典或原文明确类别匹配 |
| `match_method` | 匹配方式 | `DATASET` | 数据集范围 | 原始来源和数据集范围匹配且有通用依据 |
| `metric_type` | 指标类型 | `PRICE` | 绝对价格 | 针对价格指标 |
| `metric_type` | 指标类型 | `PRICE_CHANGE_RATE` | 价格变化率 | 针对价格百分比 |
| `metric_type` | 指标类型 | `TRANSACTION_VOLUME` | 交易量 | 针对交易数量 |
| `metric_type` | 指标类型 | `SUPPLY_VOLUME` | 供应量 | 针对供应数量 |
| `metric_type` | 指标类型 | `VOLUME_CHANGE_RATE` | 数量变化率 | 针对交易/供应变化比例 |
| `metric_type` | 指标类型 | `PRODUCT_FACT` | 商品事实 | 针对非数值商品事实 |
| `metric_type` | 指标类型 | `TEXT_CLAIM` | 文本结论 | 针对文章/新闻结论 |
| `metric_type` | 指标类型 | `INFO` | 信息记录 | 仅处理统计 |
| `metric_type` | 指标类型 | `__ALL__` | 全指标 | 仅有明确通用范围的规则使用，单位规则不得使用 |
| `food_scope_decision` | 食品范围判定 | `FOOD` | 食品 | 权威类别证明为食品且业务范围接受 |
| `food_scope_decision` | 食品范围判定 | `FLOWER` | 花卉 | 权威类别证明为花卉，食品业务排除 |
| `food_scope_decision` | 食品范围判定 | `OTHER_NON_FOOD` | 其他非食品 | 明确非食品，食品业务排除 |
| `revision_selection_method` | 修订选择方法 | `IDENTICAL_ONLY` | 仅同内容去重 | 无不同内容的有效修订排序依据，完全相同内容才自动去重 |
| `revision_selection_method` | 修订选择方法 | `SOURCE_REVISION_ORDER` | 按源修订顺序 | 来源明确修订字段、类型及顺序规则 |
| `basis_type` | 依据类型 | `OFFICIAL_PUBLISHED` | 官方发布依据 | 权威字典或官方单位/日期/修订说明 |
| `basis_type` | 依据类型 | `BUSINESS_CONFIRMED` | 已确认业务规则 | 食品范围、允许用途、门槛及责任已有可追溯确认记录 |
| `basis_type` | 依据类型 | `PENDING` | 尚未取得依据 | 只能保留 DRAFT；basis_quote/basis_hash 不造值，不参与正式解释 |
| `rule_status` | 规则状态 | `ACTIVE` | 当批可读取 | 依据、必要参数、生效期、冲突检查及规则哈希全部通过并锁定 |
| `rule_status` | 规则状态 | `DRAFT` | 不启用 | 依据未取得、业务用途/门槛未确定或参数不完整 |
| `rule_status` | 规则状态 | `DISABLED` | 停用 | 不参与当前批次解释，仍保留追溯 |
| `allowed_uses_json` | 允许用途列表 | `ABSOLUTE_PRICE` | 绝对价格参考 | 逐商品单位/币种/数据期和业务用途明确 |
| `allowed_uses_json` | 允许用途列表 | `TREND` | 同口径趋势 | 观测期、基期、指标和业务用途明确 |
| `allowed_uses_json` | 允许用途列表 | `SUPPLY` | 供需参考 | 量纲、统计范围及用途明确 |
| `allowed_uses_json` | 允许用途列表 | `HISTORICAL_REFERENCE` | 历史资料 | 只保存资料，不开放同期业务计算 |
| `allowed_uses_json` | 允许用途列表 | `CANDIDATE_ATTRIBUTE` | 商品属性线索 | 有具体商品及属性披露，仍执行字典/入名约束 |

JSON 内部 kind、method、value_type 等封闭成员的逐值语义和必填条件已在第 4 节定义；未知值校验失败，不静默扩展。

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `metric_role` | 指标角色 | `__ALL__` | 适用全部角色 | 有统一依据的通用规则 |
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
| `delay_basis` | 时效计算依据 | `DATA_PERIOD_END` | 统计期结束日 | 统计数值有真实数据期 |
| `delay_basis` | 时效计算依据 | `RETAIL_OBSERVED_AT` | 零售观测日 | 真实在架/报价快照 |
| `delay_basis` | 时效计算依据 | `SOURCE_PUBLISHED_AT` | 原生发布时间 | 原生文章或上市事件 |
| `delay_basis` | 时效计算依据 | `NOT_APPLICABLE` | 不适用时效 | 静态属性不计趋势时效 |
| `metric_type` | 指标类型 | `SALES_QUANTITY` | 商品销量 | PERIOD_SALES/CUMULATIVE_SALES，不能充当Binomial次数 |
| `metric_type` | 指标类型 | `POS_RANK` | POS名次 | 序号而非销量，越小越靠前 |
| `metric_type` | 指标类型 | `STORE_COVERAGE` | 覆盖门店数 | 店/点位数；无总数不计算比例 |

## 6. ETL、唯一性和自动化执行

1. 依据先保存可访问原始快照或受控业务确认记录，再导入规则。数据开发自动加载官方代码字典，校验商品代码、名称、类别、市场及有效期；未匹配代码保持隔离。
2. 每类规则按先精确来源/数据集/市场/指标、再 PRODUCT_CODE、PRODUCT_NAME、CATEGORY、DATASET 的适用层级定位。在相同精确程度内按 priority 选取。通用食品范围规则只判食品范围，不越权覆盖单位/日期规则。相同最高层级及 priority 的冲突命中写 RULE_CONFLICT，不任取一条。
3. PRODUCT_IDENTITY 只补权威身份；内部小分类仍由现有竞对分类映射规则和 dim_sku 决定；不得把“蔬菜”这类品类概念硬变成具体商品。
4. UNIT 规则必须按报表/商品/指标/时期验证；不能用台湾农产通用元/公斤覆盖已有证据的花卉元/把，不把所有油类推断为升。采用本次已确认食品范围规则的新批次排除花卉食品用途，原始单位证据保留；该业务范围调整默认下一完整月生效，历史批次重跑仍读取原范围规则。
5. DATE 规则不能把采集日前一天当 Yesterday，也不能把修订日当交易日；没有官方锚点/时区/周期定义则日期未解析。来源只报告百分比时独立保留，不伪造绝对值和基期分子分母。
6. 业务只登记一次规则/参数及后续更新，算法自动读取当批 ACTIVE 快照。DRAFT 不参与正式计算，相关字段降级，其余有效来源继续；不要求人工逐条确认标准证据才运行。
7. 算法批次初始化时按规则有效期、依据的来源数据适用期和匹配范围锁定实际内容。规则生效期按锁定日期校验，source_period_start/end 另校验原始观测期；日期尚未知时不能越过一个有明确来源时期限制的单位/身份规则。DATE 规则先按有依据的来源条件解析，再验证解析后的数据期满足其来源时期限制。
8. 每批 `rule_id` 唯一，哈希以稳定字段顺序和规范 JSON 生成。被锁定的内容及有效期不能被最新资产覆盖；新规则下一完整月 BATCH 生效，历史重跑读取原快照。

## 7. 缺失、降级和验收

| 场景 | 写法和处理 |
|---|---|
| 未取得官方完整字典 | 对应身份规则 DRAFT；标准证据品名/类别保持 NULL、未匹配，技术验收补字典覆盖，不要求业务逐代码命名 |
| 商务单位未确证 | 单位规则 DRAFT；绝对价格不比较。百分比独立判断，商务 TREND 用途未确认不启用 |
| 香港相对日期无锚点 | 日期规则 DRAFT；只保留可追溯历史资料，业务日趋势/同期比较不启用 |
| 覆盖分母或门槛未知 | 覆盖率/阈值 NULL，不填 0、不假设 100%；相关门槛用途保持未启用 |
| 花卉类别已确证 | 已确认食品范围规则排除；未知类别不命中该规则，另写隔离 |
| 无修订规则而内容不同 | 不按最新 SUCCESS 选取，相关观测冲突隔离 |
| 规则重叠/同级冲突 | 不取任意规则，记录 RULE_CONFLICT，阻断受影响解释用途 |

数据开发至少提交权威依据快照和 hash、官方代码唯一性/覆盖率、适用期和市场验证、规则冲突零重复证明、单位因子和日期/基期转换复算、花卉与未知类别分别处理、百分比独立用途、覆盖分母来源、同批规则快照不变和源修正不带入新规则的验收。仅有字段合同或导入行数不能替代生产验收。

预期观测集合必须包含来源完整业务维度，不能把商品×市场全笛卡尔积当成实际应报范围。集合以受控资产保存精确键与内容hash；单个期望观测的单位是商品/统计口径×指标角色×应报周期。缺分母时保留NULL，不从已采集记录反推。商品事实用途可逐记录验证；需要来源完整覆盖/时效的渠道、价量或趋势能力仍须对应已发布门槛。

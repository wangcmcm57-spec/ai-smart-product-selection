# 标准化外部证据表

## 1. 表定位、粒度和主键

正式表名：`dwd_external_evidence_normalized`。

用途：把公开原始来源转换为算法 07 可读取的单指标证据，分别保存技术质量、允许用途、商品匹配和食品业务准入；技术 PASS 不代表可比较价格、已完成商品匹配或可进入新品候选。

一行代表：一个统一算法批次内，一条原始来源记录派生的一种指标或文本事实。原始商品行同时含价格和数量时拆为两条证据，用 `observation_group_id` 关联，不把价量多列混成一条可加总事实。

主键：`algorithm_batch_version + evidence_id`。

`evidence_id` 按来源、数据集、原始快照、原始行定位及 `metric_type + metric_role` 确定性生成；同一原始行的价格证据和数量证据必须不同，当前/日常/划线/会员/促销价格角色也必须不同。新增角色键的迁移仅用于新批次，旧批次沿用其原锁定序列化及ID；迁移时旧新证据ID映射保存在受控输入资产，不改写原始快照。`JQ_` 前缀为久谦原生证据快照索引保留，本公开标准化表不能使用该前缀；既有公开证据ID如冲突须在开发迁移时保留旧新ID映射及原始血缘，不改原始快照。`observation_key` 表示不含采集/修订号的同一来源观测业务键，用于替代来源修订，不是结果版本。正式读取必须通过本次已原子发布的 `mart_external_batch_input_manifest` 选择集合，不能累计全部证据行或全部成功采集批次。

当前合同是算法 07 的 V1 数据适配，不证明生产已建表或服务器已有记录已经通过验收。算法输出仍须按算法卡执行映射、内部适配和趋势准入；本表不自行输出正式增长结论。

## 2. 完整字段合同

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 统一算法批次版本 | `algorithm_batch_version` | varchar(32) | 必须 | 全链路调度 | 唯一业务批次，固定 `BATCH_YYYYMM`，算法 01～10 共用 |
| 计算结束日期 | `calculation_end_date` | date | 必须 | 全链路调度 | 该批次自然月月末，月份与 BATCH 一致 |
| 证据 ID | `evidence_id` | varchar(128) | 必须 | 标准化步骤 E1 生成 | 原始快照＋原始行＋指标的稳定标识，不表示商品数量 |
| 观测业务键 | `observation_key` | varchar(128) | 必须 | 标准化步骤 E2 生成 | 同源、同数据集、市场、商品、按时间类型确定的观测期/时点、指标及角色和其他原始统计维度的规范哈希；不含采集批次或来源修订号 |
| 原始行分组 ID | `observation_group_id` | varchar(128) | 必须 | 标准化步骤 E1 生成 | 同一原始快照及原始商品行派生的价格、数量共用，禁止当证据唯一键 |
| 原始快照 ID | `raw_snapshot_id` | varchar(128) | 必须 | `ods_external_source_raw_snapshot.raw_snapshot_id` | 关联完整原始响应 |
| 采集批次号 | `collection_batch_id` | varchar(128) | 必须 | `ods_external_source_raw_snapshot.collection_batch_id` | 采集技术血缘，不能替代 BATCH |
| 原始行定位 | `raw_record_locator` | varchar(1024) | 必须 | 标准化步骤 E1 定位 | JSON 路径、文件行号或表格行列；足以从原始响应找回该值 |
| 观测维度 | `observation_dimensions_json` | json | 必须 | 标准化步骤 E2 提取 | 对象，保存原始市场编码、品种、等级、供应来源、统计口径等原始维度；键排序后参与观测键，不随意补值 |
| 来源 ID | `source_id` | varchar(128) | 必须 | `ods_external_source_raw_snapshot.source_id` | 来源稳定标识 |
| 来源名称 | `source_name` | varchar(256) | 必须 | `ods_external_source_raw_snapshot.source_name` | 来源名称 |
| 数据集 ID | `dataset_id` | varchar(128) | 必须 | `ods_external_source_raw_snapshot.dataset_id` | 报表、接口或数据集标识 |
| 来源类型 | `source_type` | varchar(64) | 必须 | `ods_external_source_raw_snapshot.source_type` | 与原始快照合同保持一致 |
| 来源市场 | `source_market` | varchar(64) | 必须 | `ods_external_source_raw_snapshot.source_market` | 原数据所属地区，不是国内目标算法区域 |
| 原始链接 | `source_url` | string | 必须 | `ods_external_source_raw_snapshot.source_url` | 回溯原文、接口或文件 |
| 证据对象类型 | `evidence_object_type` | varchar(32) | 必须 | 原始来源粒度及已锁定身份解释 | 区分具体商品、品类汇总、文本主题及 INFO；不能将“蔬菜”品类汇总硬当商品 |
| 外部商品代码 | `external_product_code` | varchar(128) | 可选 | 原始快照商品行 | 官方商品代码或外部 SKU，原样保留，不能直接当商品名 |
| 外部商品名称 | `external_product_name` | varchar(512) | 条件必须 | 原始快照商品行或已锁定 `PRODUCT_IDENTITY` 规则 | 原文名称优先；权威代码字典补全时必须有规则依据，未知时 NULL |
| 外部分类名称 | `external_category_name` | varchar(256) | 可选 | 原始快照分类或已锁定 `PRODUCT_IDENTITY` 规则 | 未知写 NULL，不凭代码前缀或名称相似猜分类 |
| 品牌名称 | `brand_name` | varchar(128) | 可选 | 原始快照商品行 | 仅保留来源明确披露的品牌 |
| 原始规格 | `spec_text` | varchar(256) | 可选 | 原始快照商品行 | 原样规格，不由价格单位推测商品包装规格 |
| 文章标题 | `article_title` | varchar(1024) | 可选 | 原始快照文章 | 文章证据填写 |
| 文章正文 | `article_text` | string | 可选 | 原始快照文章及可追溯正文抽取 | 用于属性/线索解析；保留原始快照定位，引用仍按授权约束 |
| 图片链接列表 | `image_urls_json` | json | 必须 | 原始快照图片及本行归属抽取 | URL字符串数组，只保留已返回且可定位归属的链接；无图片[]。V1其他外部源不单独找图/抓图，久谦为主要图片来源；匹配和授权另验 |
| 指标角色 | `metric_role` | varchar(64) | 必须 | 标准化步骤E1按原始字段/表头拆分 | 与metric_type共同进入证据/观测键；价格角色、销量性质、排名含义分开 |
| 指标类型 | `metric_type` | varchar(64) | 必须 | 标准化步骤 E1 拆分 | 价格、涨跌率、交易量、供应量、商品事实、文本结论或 INFO |
| 原始值文本 | `raw_value_text` | string | 可选 | 原始快照原始单元格或文本 | 原样保存 `-`、百分号和原始数值，不改写原文 |
| 原始单位文本 | `raw_unit_text` | varchar(256) | 可选 | 原始单元格、列头及表注 | `公斤/升` 等混合表头必须原样保存，不能当确定单位 |
| 标准指标值 | `metric_value` | decimal(24,10) | 条件必须 | 标准化步骤 E3 数值解析及已锁定单位规则 | 同一行唯一数值；缺报、非法、不适用写 NULL；价格单位未确证时不得产生可比较标准价格 |
| 标准指标单位 | `metric_unit` | varchar(64) | 条件必须 | 已锁定 `UNIT` 规则或原文明确单位 | 例如 `CNY/kg`、`HKD/kg`、`CNY/pack`、`kg`、`L`、`ratio`、`rank`、`store`；无法确证写 NULL |
| 币种 | `currency_code` | char(3) | 条件必须 | 原始币种或已锁定单位规则 | 绝对价格必须填来源币种，例如 CNY/HKD/TWD；不自动汇率换算 |
| 单位变换因子 | `unit_conversion_factor` | decimal(24,10) | 条件必须 | 已锁定 `UNIT` 规则或明确同单位恒等变换 | `metric_value = parsed_raw_value * unit_conversion_factor`；同单位为 1；百分数转比例为 0.01，必须有原文百分号/规则依据 |
| 单位解释状态 | `unit_resolution_status` | varchar(32) | 必须 | 标准化步骤 E3 | 有依据、未解决或本指标不适用 |
| 单位依据 ID | `unit_basis_id` | varchar(128) | 条件必须 | 原始快照 ID 或已锁定单位规则 `rule_id` | 单位已确证时必填，定位到依据快照/规则，不只写“官网” |
| 证据时间类型 | `evidence_time_type` | varchar(32) | 必须 | 标准化步骤E4按来源物理时间含义判定 | 四分支读取；不把静态属性强制转成交易期 |
| 零售观测时间 | `observed_at` | datetime | 条件必须 | 原始零售响应的实际快照时点/本次采集观测 | UTC；RETAIL_OBSERVATION必填，采集可证明当时可见，不证明交易发生日 |
| 来源日期原文 | `source_date_text` | varchar(256) | 可选 | 原始快照日期单元格或表头 | 原样保存绝对日期、Yesterday、Last Week 等 |
| 数据期开始日期 | `data_period_start` | date | 条件必须 | STATISTICAL_PERIOD的真实统计期或已锁定DATE规则 | 左闭区间开始；无法转换时 NULL，不用采集日代替 |
| 数据期结束日期 | `data_period_end` | date | 条件必须 | STATISTICAL_PERIOD的真实统计期或已锁定DATE规则 | 右闭区间结束，日数据与开始日相同 |
| 比较基期开始日期 | `comparison_period_start` | date | 条件必须 | 百分比指标原始比较说明或已锁定日期规则 | 涨跌率的独立 BASE 周期开始；不是本行观测期 |
| 比较基期结束日期 | `comparison_period_end` | date | 条件必须 | 百分比指标原始比较说明或已锁定日期规则 | 基期结束；百分比用于趋势前必须明确观测期及基期 |
| 日期解释状态 | `date_resolution_status` | varchar(32) | 必须 | 标准化步骤 E4 | 按时间类型评价交易期、零售观测或文章发布时间；有依据、未解决或静态属性不适用 |
| 日期依据 ID | `date_basis_id` | varchar(128) | 条件必须 | 原始快照 ID 或已锁定日期规则 `rule_id` | 日期已确证时必填，能定位相对日期锚点、时区及区间规则 |
| 来源发布时间 | `source_published_at` | datetime | 可选 | 原始发布时间及有依据的日期转换 | UTC 时间；不等于交易日 |
| 来源修订时间 | `source_revised_at` | datetime | 可选 | 原始修订时间及有依据的日期转换 | UTC 时间；不等于发布时间或交易日 |
| 采集时间 | `captured_at` | datetime | 必须 | `ods_external_source_raw_snapshot.captured_at` | UTC 时间，独立于来源数据期 |
| 数值状态 | `value_status` | varchar(32) | 必须 | 标准化步骤 E3 | 数值、文本、源缺报、非法或不适用 |
| 技术质量状态 | `quality_status` | varchar(32) | 必须 | 字段质量校验汇总 | PASS 只证明本条技术质量；多问题先按证据聚合，不能据此直接准入 |
| 商品匹配状态 | `product_mapping_status` | varchar(32) | 必须 | 权威商品身份规则或原文明示身份/类别校验 | 仅表示来源商品身份/类别已可靠识别、未识别、歧义或不适用；不要求内部小分类映射完成 |
| 内部小分类编码 | `internal_leaf_category_code` | varchar(64) | 可选 | 已有 `dim_competitor_category_mapping_rule` 和 `dim_sku.category_level3_code` 明确映射 | 前置规则已有可靠映射时填写，否则 NULL；不能反向依赖尚未运行的 07 输出，候选映射由 07 再执行 |
| 食品业务准入状态 | `business_admission_status` | varchar(32) | 必须 | 已锁定食品范围及用途规则 | 有可用业务计算用途、隔离、范围排除或不适用；仅 HISTORICAL_REFERENCE 不写 ELIGIBLE，不代表候选已通过 08/09 |
| 允许用途列表 | `allowed_uses_json` | json | 必须 | 已锁定 `USAGE` 规则及字段有效性校验 | 去重字符串数组，取值受本合同约束；未允许用途写 `[]`，不是默认全用途 |
| 状态原因代码列表 | `reason_codes_json` | json | 必须 | 质量问题及准入判定汇总 | 去重字符串数组，代码来自质量合同；无原因 `[]`，不能用长段自由文本替代机器状态 |
| 应用解释规则 ID 列表 | `interpretation_rule_ids_json` | json | 必须 | `dim_external_evidence_interpretation_rule.rule_id` | 当前 BATCH 锁定的实际命中规则 ID 数组；只依赖原文明示时可为空数组 |
| 生成运行 ID | `run_id` | varchar(64) | 必须 | 标准化调度 | 实际运行审计，不作为第二套业务版本 |
| 生成时间 | `updated_at` | datetime | 必须 | 标准化任务 | UTC 时间 |

## 3. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `source_type` | 来源类型 | `COMPETITOR_SKU` | 竞品 SKU | 外部竞品商品接口，继承原始快照类型 |
| `source_type` | 来源类型 | `RETAIL_SKU` | 零售 SKU | 零售商品页面或结构化商品源 |
| `source_type` | 来源类型 | `POS_RANKING` | POS 新品榜 | 真实零售 POS 榜单 |
| `source_type` | 来源类型 | `OFFICIAL_PRICE_VOLUME` | 官方价量 | 官方价格/交易量，不进入竞品渠道分母 |
| `source_type` | 来源类型 | `OFFICIAL_SUPPLY` | 官方供需 | 官方供应/来货量，不进入竞品渠道分母 |
| `source_type` | 来源类型 | `INDUSTRY_ARTICLE` | 行业文章 | 行业机构或行业媒体文章 |
| `source_type` | 来源类型 | `PUBLIC_NEWS` | 公开新闻 | 可追溯公开新闻 |
| `evidence_object_type` | 证据对象类型 | `PRODUCT` | 具体商品 | 原文明示或权威字典证明具体商品/品种身份 |
| `evidence_object_type` | 证据对象类型 | `CATEGORY` | 品类统计 | 蔬菜等品类级汇总，保留原始统计粒度，不生成具体商品属性 |
| `evidence_object_type` | 证据对象类型 | `TEXT` | 文本主题 | 行业/新闻事实，尚未落到具体商品或品类 |
| `evidence_object_type` | 证据对象类型 | `INFO` | 信息记录 | 表头、休市或非业务说明 |
| `metric_type` | 指标类型 | `PRICE` | 绝对价格 | 原文有价格指标 |
| `metric_type` | 指标类型 | `PRICE_CHANGE_RATE` | 价格变化率 | 原文提供带明确比较含义的价格百分比 |
| `metric_type` | 指标类型 | `TRANSACTION_VOLUME` | 交易量 | 原文提供交易数量 |
| `metric_type` | 指标类型 | `SUPPLY_VOLUME` | 供应量 | 原文提供供应或来货数量 |
| `metric_type` | 指标类型 | `VOLUME_CHANGE_RATE` | 数量变化率 | 原文提供交易/供应数量变化比例，具体含义保留在观测维度 |
| `metric_type` | 指标类型 | `PRODUCT_FACT` | 商品事实 | 名称、品牌、规格、卖点等非数值商品事实 |
| `metric_type` | 指标类型 | `TEXT_CLAIM` | 文本结论 | 可追溯文章或新闻结论 |
| `metric_type` | 指标类型 | `INFO` | 信息记录 | 表头、休市、说明文字等处理统计 |
| `unit_resolution_status` | 单位解释状态 | `VERIFIED` | 单位有依据 | 原文明示或唯一有效规则命中且可复算 |
| `unit_resolution_status` | 单位解释状态 | `UNRESOLVED` | 单位未解决 | 混合表头、单位冲突或无依据 |
| `unit_resolution_status` | 单位解释状态 | `NOT_APPLICABLE` | 不需要数值单位 | 纯文本、商品事实或 INFO |
| `date_resolution_status` | 日期解释状态 | `VERIFIED` | 周期有依据 | 相应时间类型有依据；统计期须明确，零售须observed_at，文章须source_published_at；变化率还须基期 |
| `date_resolution_status` | 日期解释状态 | `UNRESOLVED` | 周期未解决 | 只有无锚点相对日期、时间冲突或基期不明 |
| `date_resolution_status` | 日期解释状态 | `NOT_APPLICABLE` | 不适用交易周期 | INFO 或没有周期含义的静态商品事实 |
| `value_status` | 数值状态 | `NUMERIC` | 合法数值 | 可解释解析；单位未确定时保留原值但标准值仍可为 NULL |
| `value_status` | 数值状态 | `TEXT_ONLY` | 仅文本 | 文本事实或结论，无数值指标 |
| `value_status` | 数值状态 | `SOURCE_NOT_REPORTED` | 来源未报告 | 原文 `-` 或来源明确的缺报标识 |
| `value_status` | 数值状态 | `INVALID` | 非法数值 | 解析失败，绝对价格/数量负值或分母不合法 |
| `value_status` | 数值状态 | `NOT_APPLICABLE` | 不适用 | INFO 等不承载业务数值 |
| `quality_status` | 技术质量状态 | `PASS` | 技术质量通过 | 本条适用的关键字段校验通过，不等于商品或业务准入 |
| `quality_status` | 技术质量状态 | `REVIEW_REQUIRED` | 有未解决技术质量问题 | 适用的 OPEN TECHNICAL 问题存在；身份映射、用途及准入问题分别影响其对应状态，不自动反写技术质量 |
| `quality_status` | 技术质量状态 | `NOT_APPLICABLE` | 非业务信息 | INFO，不计入业务异常待修数 |
| `product_mapping_status` | 商品匹配状态 | `MAPPED` | 来源身份已可靠识别 | 原文明示或权威字典唯一识别商品/品类身份；CATEGORY 仍为品类，不要求内部小分类非空 |
| `product_mapping_status` | 商品匹配状态 | `UNMAPPED` | 来源身份未识别 | 商品身份/类别不全或权威代码字典未命中 |
| `product_mapping_status` | 商品匹配状态 | `AMBIGUOUS` | 来源身份冲突 | 命中多条冲突的来源身份规则 |
| `product_mapping_status` | 商品匹配状态 | `NOT_APPLICABLE` | 不适用商品匹配 | INFO、已确证非食品或未落到商品/品类的纯文本历史资料 |
| `business_admission_status` | 食品业务准入状态 | `ELIGIBLE` | 存在已允许业务计算用途 | ABSOLUTE_PRICE/TREND/SUPPLY/CANDIDATE_ATTRIBUTE 至少一项明确且相应字段有效；候选仍需 07 内部适配和后续算法 |
| `business_admission_status` | 食品业务准入状态 | `QUARANTINED` | 隔离 | 身份/类别未知、关键语义未解决或业务用途尚未确定 |
| `business_admission_status` | 食品业务准入状态 | `OUT_OF_SCOPE` | 排除食品业务 | 权威身份/类别证明是花卉或其他明确非食品；原始数据保留 |
| `business_admission_status` | 食品业务准入状态 | `NOT_APPLICABLE` | 非业务信息 | INFO |
| `allowed_uses_json` | 允许用途列表 | `ABSOLUTE_PRICE` | 绝对价格参考 | 价格角色、币种、单位、适用统计期或零售观测时点、商品和范围满足已发布用途规则 |
| `allowed_uses_json` | 允许用途列表 | `TREND` | 同口径趋势 | 商品/类别、观测期、比较基期、指标含义及用途均明确 |
| `allowed_uses_json` | 允许用途列表 | `SUPPLY` | 供需参考 | 数量单位、数据期、统计范围及用途明确 |
| `allowed_uses_json` | 允许用途列表 | `HISTORICAL_REFERENCE` | 历史资料 | 保留可追溯资料，不能据此做同期数值比较或候选属性赋值 |
| `allowed_uses_json` | 允许用途列表 | `CANDIDATE_ATTRIBUTE` | 候选属性线索 | 来源明确商品属性，商品身份可靠；仍按属性字典及入名规则处理 |
| `reason_codes_json` | 状态原因列表 | `IDENTITY_MISSING` | 商品身份缺失 | 无权威字典可补全缺失品名 |
| `reason_codes_json` | 状态原因列表 | `UNKNOWN_CATEGORY` | 来源类别未知 | 不能证明食品或花卉类别 |
| `reason_codes_json` | 状态原因列表 | `CATEGORY_MAPPING_GAP` | 内部分类缺口 | 已知来源身份但无内部小分类，只阻断相关候选用途 |
| `reason_codes_json` | 状态原因列表 | `UNIT_UNRESOLVED` | 单位未解决 | 缺失、混合或冲突单位无依据 |
| `reason_codes_json` | 状态原因列表 | `DATE_UNRESOLVED` | 日期未解决 | 相对日期无锚点或比较基期未知 |
| `reason_codes_json` | 状态原因列表 | `SOURCE_NOT_REPORTED` | 来源缺报 | 原始值为缺报标识 |
| `reason_codes_json` | 状态原因列表 | `INVALID_VALUE` | 非法值 | 解析失败或绝对价量负数 |
| `reason_codes_json` | 状态原因列表 | `INFO_RECORD` | 信息记录 | 表头、休市或源说明 |
| `reason_codes_json` | 状态原因列表 | `RULE_CONFLICT` | 规则冲突 | 同适用范围存在矛盾解释 |
| `reason_codes_json` | 状态原因列表 | `DUPLICATE_OBSERVATION` | 重复观测 | 存在同观测重复采集或修订 |
| `reason_codes_json` | 状态原因列表 | `COVERAGE_UNKNOWN` | 覆盖率未知 | 无明确预期观测分母 |
| `reason_codes_json` | 状态原因列表 | `COVERAGE_BELOW_THRESHOLD` | 覆盖不足 | 未达当批已锁定门槛 |
| `reason_codes_json` | 状态原因列表 | `DELAY_THRESHOLD_MISSING` | 延迟门槛未定 | 该用途尚无已登记最大延迟 |
| `reason_codes_json` | 状态原因列表 | `SOURCE_STALE` | 数据过期 | 明确数据期超过已登记门槛 |
| `reason_codes_json` | 状态原因列表 | `BUSINESS_USE_UNCONFIRMED` | 用途未确定 | 商务趋势等未登记生效用途 |
| `reason_codes_json` | 状态原因列表 | `OUT_OF_FOOD_SCOPE` | 非食品范围 | 已确证花卉或其他非食品 |
| `reason_codes_json` | 状态原因列表 | `LINEAGE_MISSING` | 血缘缺失 | 无可追溯原始响应/行定位/依据 |
| `reason_codes_json` | 状态原因列表 | `OUTSIDE_BATCH_WINDOW` | 超出批次边界 | 数据期超过当批月末，或正常输入的采集/来源发布时间超过锁定 cutoff |
| `evidence_time_type` | 证据时间类型 | `STATISTICAL_PERIOD` | 统计数据期 | 交易、供应或带明确统计期的数值 |
| `evidence_time_type` | 证据时间类型 | `RETAIL_OBSERVATION` | 零售实测时点 | 在架/报价/榜单快照，observed_at有依据 |
| `evidence_time_type` | 证据时间类型 | `PUBLICATION_EVENT` | 原生发布时间 | 文章或上市事件，无交易期含义 |
| `evidence_time_type` | 证据时间类型 | `STATIC_ATTRIBUTE` | 静态属性 | 无周期的商品事实，不计周趋势 |
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
| `metric_type` | 指标类型 | `SALES_QUANTITY` | 商品销量 | PERIOD_SALES/CUMULATIVE_SALES，不能充当Binomial次数 |
| `metric_type` | 指标类型 | `POS_RANK` | POS名次 | 序号而非销量，越小越靠前 |
| `metric_type` | 指标类型 | `STORE_COVERAGE` | 覆盖门店数 | 店/点位数；无总数不计算比例 |

## 4. 开发执行流程和聚合安全

1. **E1 原始定位和拆分：**读取已保存快照，定位每条源记录。价格、数量、涨跌率分别产出证据；INFO 单独标识；不删除原文中的“其中：”。
2. **E2 观测键：**依据来源实际粒度构造规范维度，包含市场、商品/类别、evidence_time_type对应的时间键、metric_type及metric_role。日期或商品身份未知时使用原始快照内容哈希＋稳定行定位并明确未知维度，禁止猜日期或把未知观测当同期修订合并。
3. **E3 数值/单位：**先保留原文，再按原文明示或本批次锁定规则解析标准值。百分比独立为比例指标，不换算成绝对价格。kg 与 L 不互转，不跨币种比较；不存在依据时不假设油类都按升。
4. **E4 日期：**先确定evidence_time_type；STATISTICAL_PERIOD读真实统计期，RETAIL_OBSERVATION读实际observed_at，PUBLICATION_EVENT读有依据发布时间，STATIC_ATTRIBUTE不要求交易期。分开来源发布时间、修订时间、采集时间和数据期。Yesterday/Last Week 无有依据锚点、时区和区间定义时，数据期 NULL。修订日不能自动替代交易日。观测期及基期都明确才允许变化率用于同期趋势。
5. **E5 分层校验：**按质量明细逐证据聚合，分别填写质量、来源商品身份匹配、准入和允许用途。不因 PASS 自动开放全部用途。已确证花卉写 OUT_OF_SCOPE；类别缺失独立 QUARANTINED，不能和花卉一起删除。来源身份/食品范围已确定的官方商品/品类价格或供应量可按有效单位/日期及已发布用途使用，不因内部小类缺失阻断；CATEGORY 只能按来源品类粒度计算，不生成具体商品属性。候选内部小分类仍由 07 external_attribute_mapping 单独完成。仅有 HISTORICAL_REFERENCE 时为 QUARANTINED，该资料不参与 07 趋势或候选计算。
6. **E6 输入冻结：**按本批次已登记的修订策略选观测，将选中和排除结果、规则快照和哈希写入输入锁定清单。正式结果只读取该次原子发布的 SELECTED 集合。重跑复用锁定清单；源数据修正记录新旧证据及原因，规则/区域仍复用原批次。

价格是单位价格，不能直接 SUM。涨跌率不是绝对价格的一部分，不能相加或平均后当官方变化率。交易量/供应量只有在单位、商品、市场、统计期和覆盖范围一致，且无父子品类/供应口径包含关系时才可加总；否则保留明细、不生成总量。数量变化率须保留本行观测期和比较基期，源只给涨跌率时不得伪造分子分母。

证据计数用 BATCH 内去重 `evidence_id`，源商品行计数用 `observation_group_id`，商品数量须另按可靠商品身份去重。质量问题表先聚合成每证据一行再关联；输入清单先过滤单次已发布运行及 SELECTED，不得多运行、多修订累加。

## 5. 缺失、异常和用途降级

| 场景 | 保留内容 | 必须写法及禁止用途 |
|---|---|---|
| 官方代码无品名/类别字典 | 代码、原始值、快照、行定位 | 品名/类别不猜；UNMAPPED、QUARANTINED；取得权威字典是技术交付验收，不要求业务逐代码填写 |
| 已确证花卉 | 原始快照及标准证据 | OUT_OF_SCOPE，允许用途 `[]`；食品业务统计不纳入 |
| 未知类别 | 原始记录及质量问题 | QUARANTINED；不凭同批花卉存在而排除 |
| 商务混合公斤/升表头 | 原文及原始值 | 标准绝对价格 NULL，单位 UNRESOLVED；百分比证据独立判断；商务趋势业务用途未确认时不自动加入 TREND |
| 香港只有相对日期 | 原始相对日期、修订日、采集日 | 数据期 NULL、日期 UNRESOLVED；保留 HISTORICAL_REFERENCE，不启用日趋势/跨源同期比较；额外用途或延迟门槛未确认不自动启用 |
| 来源 `-` 缺报 | 原始缺报文本 | SOURCE_NOT_REPORTED、标准数值 NULL，不补 0；缺报率单独对账，本轮不插值 |
| 合法 0 | 原值和合法标准值 0 | 只有来源真实报告且单位/周期合法时保留 0，不作为缺报替代 |
| 负值 | 原文和问题 | 绝对价格、交易量/供应量负值 INVALID；带明确基期的变化率可合法为负 |
| INFO | 原文、处理统计 | INFO、NOT_APPLICABLE；不计业务异常、缺报率或可用覆盖率分母 |
| 缺规则或规则冲突 | 证据及问题 | 对相关用途隔离，其他来源/独立有效指标继续运行；不把逐条人工复核设为算法前置 |

## 6. 验收要求

必须验证 BATCH 格式/月末、主键唯一、原始行定位、价量拆分、官方代码字典实际覆盖、日期/单位依据及因子复算、负变化率、缺报/真实 0、INFO、花卉和未知类别隔离、观测修订去重、来源币种保留、多问题关联不放大，以及同批重跑输入/规则哈希一致。

覆盖率和缺报率按来源、数据集、市场、指标及明确的预期观测范围分别计算。只有来源规则提供可复核预期观测集合或分母时才输出覆盖率；未知分母为 NULL。最低覆盖率、最大延迟、商务趋势用途及香港额外用途属于业务待决参数，未确定时保留隔离/历史资料，不臆造阈值。

真实数据验收应提交来源样例、过滤前后行数、证据数与问题数、规则命中/冲突明细、观测键去重前后数量、标准值复算和失败样例；本合同本身不是生产验收通过证明。

### V1时间/指标兼容验收

静态商品事实允许data_period_start/end=NULL且date_resolution_status=NOT_APPLICABLE，仍可进入CANDIDATE_ATTRIBUTE；文章有发布时间而无交易期可以进入原生事件用途。公开商品报价使用observed_at，不能将其冒充交易日。日期/时间类型未知仍隔离。验证同一SKU同日会员/日常/促销价不会被当修订互相覆盖；POS排名不作销量；累计销量不直接差分；无图不产生TECHNICAL错误。

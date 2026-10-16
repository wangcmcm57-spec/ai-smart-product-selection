# 外部候选价格交接输入表

正式表名：`mart_external_candidate_price_input`。

一行代表：一个BATCH内一个范围候选对应一个来源商品/规格事实的一种价格角色观测；无价格时保留一条SPEC_ONLY事实，便于05明确缺失。

主键：`algorithm_batch_version + scope_candidate_id + price_input_id`。

用途：07生产、05候选价格阶段消费；08注册后保存临时系统键与正式候选键的血缘。不是国内建议价、成本或可行性结果。

## 1. 完整字段合同

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 统一算法批次版本 | `algorithm_batch_version` | varchar(32) | 必须 | 全链路调度 | BATCH_YYYYMM，进入主键 |
| 运行ID | `run_id` | varchar(64) | 必须 | external_trend_run.run_id | 本次07发布包来源 |
| 范围候选ID | `scope_candidate_id` | varchar(128) | 必须 | 第17.11节范围键与概念键SHA256 | 含BATCH及完整范围，进入主键 |
| 价格输入ID | `price_input_id` | varchar(128) | 必须 | 第17.11节来源商品/规格/价格观测SHA256 | 含角色及时间键；无价格用有依据规格事实键 |
| 标准候选概念ID | `standard_candidate_id` | varchar(128) | 必须 | external_new_product_candidate.standard_candidate_id | 07概念键，64位SHA256 hex |
| 临时系统候选ID | `candidate_product_id` | varchar(80) | 必须 | 第17.11节确定性生成 | EXT07_加完整概念ID；08注册前系统键，不是销售SKU |
| 候选名称 | `candidate_product_name` | varchar(256) | 必须 | external_new_product_candidate.candidate_product_name | 仅有来源属性入名 |
| 范围类型 | `scope_type` | varchar(32) | 必须 | 同批内部适配scope_type | CITY/CITY_CLUSTER |
| 范围编码 | `scope_id` | varchar(64) | 必须 | 同批内部适配scope_id | 城市或算法区域编码 |
| 门店等级 | `final_level` | varchar(32) | 必须 | external_new_product_candidate.final_level | A/B/C/D实际等级 |
| 消费者画像 | `final_profile` | varchar(128) | 必须 | external_new_product_candidate.final_profile | 该范围真实画像 |
| 内部小分类编码 | `internal_leaf_category_code` | varchar(64) | 必须 | external_new_product_candidate.internal_leaf_category_code | 仅叶子小类 |
| 输入类型 | `price_input_kind` | varchar(32) | 必须 | 交接步骤P1 | PRICE_OBSERVATION或SPEC_ONLY |
| 来源提供方类型 | `provider_type` | varchar(32) | 必须 | 交接步骤P1按原生来源 | JIUQIAN/PUBLIC_SOURCE/CANDIDATE_FACT |
| 来源ID | `source_id` | varchar(128) | 必须 | 来源原生索引或公开证据source_id | 不混提供方与平台 |
| 数据集ID | `dataset_id` | varchar(128) | 条件必须 | 公开标准证据dataset_id | 公开商品时必填，久谦NULL |
| 数据提供方 | `data_provider` | varchar(64) | 条件必须 | dim_competitor_sku.data_provider | JIUQIAN时必填 |
| 竞品平台 | `competitor_platform` | varchar(64) | 条件必须 | dim_competitor_sku.competitor_platform | JIUQIAN时必填 |
| 竞品城市 | `city_name` | varchar(64) | 条件必须 | dim_competitor_sku.city_name | JIUQIAN时必填 |
| 竞品SKU | `competitor_sku_id` | varchar(128) | 条件必须 | dim_competitor_sku.competitor_sku_id | JIUQIAN时必填；公开ID不得填此列 |
| 公开商品代码 | `external_product_code` | varchar(128) | 条件必须 | dwd_external_evidence_normalized.external_product_code | 公开稳定SKU有则保留，不要求品类/文章虚构SKU |
| 来源市场 | `source_market` | varchar(64) | 必须 | 来源证据 | 真实市场，海外价格不汇率换国内价 |
| 源证据ID列表 | `evidence_ids_json` | json | 必须 | 公开标准证据或JQ_原生索引 | 字符串数组；可追到规格/价格及商品对 |
| 规格事实ID | `spec_fact_id` | varchar(128) | 必须 | 第17.11节规格事实来源规范hash | 有来源标准规格事实身份；未知规格仍保留NULL及状态 |
| 原始规格 | `spec_text` | varchar(256) | 条件必须 | 久谦specification或公开spec_text | 不由价格猜重量 |
| 净含量 | `net_content` | decimal(24,8) | 条件必须 | 第17.3节规格解析 | 重量/数量/体积分开 |
| 净含量单位 | `net_content_unit` | varchar(32) | 条件必须 | 第17.3节规格解析 | g/kg/枚/件/mL/L等有依据单位 |
| 包装形式 | `package_type` | varchar(128) | 可选 | 已验证候选属性/原始商品 | 自由文本有来源，未知NULL |
| 计量类型 | `measurement_type` | varchar(32) | 条件必须 | 第17.3节计量归一化 | WEIGHT/COUNT/VOLUME，未知NULL |
| 价格角色 | `metric_role` | varchar(64) | 必须 | 公开价格角色或久谦字段适配 | 无价格为PRODUCT_ATTRIBUTE，不能造日常价 |
| 来源价格 | `price_value` | decimal(24,10) | 条件必须 | 公开metric_value或久谦价格原生字段 | 保留原币种/计价单位，缺失NULL |
| 价格币种 | `currency_code` | char(3) | 条件必须 | 原始来源/注册币种规则 | CNY/HKD/TWD等有依据币种；久谦不能仅按城市名猜币种，不自动汇率转换 |
| 价格计价单位 | `price_unit` | varchar(64) | 条件必须 | 源单位依据/规格解析 | 元/包、元/kg等对应源币种单位 |
| 观测日期 | `price_observed_date` | date | 条件必须 | 久谦collection_date或公开observed_at来源时区日期 | 零售报价观测日，不是成交日 |
| 价格数据期结束 | `price_period_end` | date | 条件必须 | 公开统计价格data_period_end | 只有STATISTICAL_PERIOD填；零售观察不伪造 |
| 竞品关系 | `competitor_relation` | varchar(64) | 必须 | 第17.3节已验收商品对 | EXACT_EQUIVALENT/BUSINESS_HIGH_SIMILAR/SAME_TREND_DIRECTION/MATCH_UNRESOLVED/NOT_APPLICABLE |
| 05匹配类型 | `price_match_type` | varchar(32) | 必须 | 第17.11节固定关系转换 | EXACT/HIGHLY_SIMILAR/CATEGORY_REFERENCE/NO_MATCH |
| 匹配概率 | `match_probability` | decimal(18,8) | 条件必须 | 第17.3节匹配校准 | 未知NULL，不能以聚合覆盖率伪造概率 |
| 匹配资产哈希 | `match_asset_hash` | varchar(64) | 条件必须 | external_trend_run.model_manifest_json | 只追溯已锁定资产，不创建独立结果版本 |
| 价格可用状态 | `price_status` | varchar(32) | 必须 | 交接步骤P2 | AVAILABLE/MISSING/UNVERIFIED/NOT_COMPARABLE |
| 消费者接口状态 | `consumer_interface_status` | varchar(32) | 必须 | 调度05接口能力探测及联调记录 | READY/BLOCKED；不改07来源事实 |
| 接口诊断 | `diagnostic_reason` | string | 条件必须 | 交接步骤P1-P3 | 缺价格/规格/关系/05接口的原因 |
| 相对价格定位 | `relative_price_position` | varchar(64) | 条件必须 | 第17.11节来源市场可比分布 | BASIC/MAINSTREAM/PREMIUM；只有ASSIGNED时非空，不代替价格可用状态 |
| 价格定位状态 | `price_position_status` | varchar(64) | 必须 | 第17.14节逐价格观测判定 | 未运行、语义未核实、样本不足、分布不稳等均明确，不能默认主流 |
| 价格定位方法 | `price_position_method` | varchar(32) | 必须 | 第17.11/17.14节能力清单 | DISTRIBUTION_VALLEY或NOT_CALCULATED；不默认使用固定业务上下界 |
| 价格定位诊断 | `price_position_diagnostics_json` | json | 必须 | 第17.14节样本/边界/判定记录 | 固定比较范围、样本/证据、边界、目标价及缺失原因；未算保留原因，结构见17.14 |
| 生成时间 | `generated_at` | datetime | 必须 | 系统生成 | UTC |

## 2. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `price_input_kind` | 输入类型 | `PRICE_OBSERVATION` | 价格观测 | 有真实价格观测 |
| `price_input_kind` | 输入类型 | `SPEC_ONLY` | 规格事实 | 无可用价格但候选/规格事实可传递 |
| `provider_type` | 提供方类型 | `JIUQIAN` | 久谦 | 四列原生键齐全 |
| `provider_type` | 提供方类型 | `PUBLIC_SOURCE` | 公开商品源 | source_id/dataset_id/公开商品键 |
| `provider_type` | 提供方类型 | `CANDIDATE_FACT` | 候选事实 | 规格/文章事实，没有可比商品报价 |
| `price_status` | 价格可用状态 | `AVAILABLE` | 可用价格 | 币种/单位/时间/角色/用途合格 |
| `price_status` | 价格可用状态 | `MISSING` | 无价格 | 来源未提供或无对应商品 |
| `price_status` | 价格可用状态 | `UNVERIFIED` | 待核实 | 单位/角色/日期等未核实 |
| `price_status` | 价格可用状态 | `NOT_COMPARABLE` | 不可比 | 关系/计量/规格不支持本次比较 |
| `consumer_interface_status` | 消费者接口状态 | `READY` | 接口就绪 | 05通过统一批次/完整键/角色及原生价格联调 |
| `consumer_interface_status` | 消费者接口状态 | `BLOCKED` | 接口阻断 | 05仍读旧ID/独立版本或联调未通过 |
| `price_match_type` | 05匹配类型 | `EXACT` | 同款 | 已验收同款 |
| `price_match_type` | 05匹配类型 | `HIGHLY_SIMILAR` | 高相似 | 已验收高相似 |
| `price_match_type` | 05匹配类型 | `CATEGORY_REFERENCE` | 趋势属性参考 | 同方向，不能算同款价格指数 |
| `price_match_type` | 05匹配类型 | `NO_MATCH` | 无可确认匹配 | 未确认或无可比商品 |
| `measurement_type` | 计量类型 | `WEIGHT` | 重量 | 有依据重量规格 |
| `measurement_type` | 计量类型 | `COUNT` | 数量 | 有依据件/枚规格 |
| `measurement_type` | 计量类型 | `VOLUME` | 体积 | 有依据体积规格 |
| `scope_type` | 范围类型 | `CITY` | 城市 | 单城市 |
| `scope_type` | 范围类型 | `CITY_CLUSTER` | 算法区域 | 同批区域快照 |
| `final_level` | 实际门店等级 | `A` | A级 | 同批02实际等级 |
| `final_level` | 实际门店等级 | `B` | B级 | 同批02实际等级 |
| `final_level` | 实际门店等级 | `C` | C级 | 同批02实际等级 |
| `final_level` | 实际门店等级 | `D` | D级 | 同批02实际等级 |
| `competitor_relation` | 竞品关系 | `EXACT_EQUIVALENT` | 同款 | 硬边界/规格段与校准通过 |
| `competitor_relation` | 竞品关系 | `BUSINESS_HIGH_SIMILAR` | 高相似 | 同主体需求，差异保留 |
| `competitor_relation` | 竞品关系 | `SAME_TREND_DIRECTION` | 同方向 | 只有属性同向 |
| `competitor_relation` | 竞品关系 | `MATCH_UNRESOLVED` | 未确认 | 关键属性/路径未验收 |
| `competitor_relation` | 竞品关系 | `NOT_APPLICABLE` | 不适用 | 仅候选规格事实 |
| `metric_role` | 价格角色 | `CURRENT_OFFER` | 当前报价 | 来源只说明当前售价，不自动当日常价 |
| `metric_role` | 价格角色 | `REGULAR_PRICE` | 已确证日常价 | 来源明确非促销常规售价 |
| `metric_role` | 价格角色 | `LIST_PRICE` | 划线/市场价 | 不冒充真实成交价 |
| `metric_role` | 价格角色 | `MEMBER_PRICE` | 会员价 | 有会员资格价格 |
| `metric_role` | 价格角色 | `PROMOTION_PRICE` | 促销价 | 原文明示促销条件 |
| `metric_role` | 价格角色 | `UNSPECIFIED_PRICE` | 未明确价格角色 | 保留原值，相关比较关闭 |
| `metric_role` | 价格角色 | `PRICE_CHANGE_RATE` | 价格变化率 | 独立百分比证据 |
| `metric_role` | 价格角色 | `TRANSACTION_VOLUME` | 交易数量 | 真实交易量 |
| `metric_role` | 价格角色 | `SUPPLY_VOLUME` | 供应数量 | 真实供应或来货量 |
| `metric_role` | 价格角色 | `VOLUME_CHANGE_RATE` | 数量变化率 | 真实数量变化百分比 |
| `metric_role` | 价格角色 | `PERIOD_SALES` | 周期销量 | 有明确销售统计期及单位 |
| `metric_role` | 价格角色 | `CUMULATIVE_SALES` | 累计销量 | 截至时点累计值，不直接加总/差分 |
| `metric_role` | 价格角色 | `POS_RANK` | 榜单序号 | 有榜单、周期和长度说明 |
| `metric_role` | 价格角色 | `STORE_COVERAGE` | 覆盖店数 | 真实覆盖店/点位数，不等于比例 |
| `metric_role` | 价格角色 | `PRODUCT_ATTRIBUTE` | 商品属性 | 名称、规格和卖点事实 |
| `metric_role` | 价格角色 | `TEXT_CLAIM` | 文章结论 | 原生文章或新闻主张 |
| `metric_role` | 指标角色 | `POS_AVERAGE_PRICE` | POS观察均价 | 真实POS统计期平均售价，不能默认当日常标价/促销价 |
| `metric_role` | 指标角色 | `WHOLESALE_REFERENCE_PRICE` | 批发行情参考价 | 有原文明示的批发层级，不给零售SKU直接分三档 |
| `metric_role` | 指标角色 | `PRODUCER_REFERENCE_PRICE` | 产地参考价 | 有原文明示的产地报价，不混零售 |
| `metric_role` | 指标角色 | `RETAIL_REFERENCE_PRICE` | 门市参考价 | 行情中的门市层级参考，不等同具体SKU常规价 |
| `metric_role` | 指标角色 | `MARKET_AVERAGE_REFERENCE_PRICE` | 市场统计均价 | 统计对象/样本明确的市场均价，保留原口径 |
| `metric_role` | 价格角色 | `INFO` | 处理信息 | 表头、休市等 |
| `price_position_status` | 价格定位状态 | `ASSIGNED` | 已完成定位 | 语义/可比性/方法验收通过且有三个稳定峰和两条边界 |
| `price_position_status` | 价格定位状态 | `NOT_ENABLED` | 定位未启用 | 该批能力未开启，未算档位 |
| `price_position_status` | 价格定位状态 | `METHOD_NOT_VALIDATED` | 方法未验收 | 样本驱动工程实现或回测尚未通过 |
| `price_position_status` | 价格定位状态 | `PRICE_SEMANTICS_UNVERIFIED` | 价格性质未核实 | 当前/平均/批发等性质无法支持该定位用途 |
| `price_position_status` | 价格定位状态 | `PRICE_INPUT_INCOMPLETE` | 定位输入不完整 | 身份、币种、单位、规格、时间或血缘等关键输入缺失/零价 |
| `price_position_status` | 价格定位状态 | `COMPARISON_SET_INSUFFICIENT` | 有效可比样本不足 | 不足以形成三个可识别价位模式，包括K<3 |
| `price_position_status` | 价格定位状态 | `DISTRIBUTION_UNSTABLE` | 分布不稳定 | 无法辨识双谷或Bootstrap稳定性未通过 |
| `price_position_status` | 价格定位状态 | `MULTIPLE_POSITIONS` | 同范围存在多档 | 仅汇总行使用，单观测已分别定位但档位不唯一 |
| `price_position_status` | 价格定位状态 | `MULTIPLE_COMPARISON_SCOPES` | 存在多个比较范围 | 仅汇总行使用，不能将不同来源/价格角色的相对档位压成一个 |
| `price_position_status` | 价格定位状态 | `NOT_APPLICABLE` | 定位不适用 | 非当前零售分档用途，例如官方参考价/POS均价/纯规格事实 |
| `price_position_method` | 价格定位方法 | `DISTRIBUTION_VALLEY` | 样本驱动峰谷 | 依原文22.2；具体GMM工程基线需验收，不等于业务手填L/U |
| `price_position_method` | 价格定位方法 | `NOT_CALCULATED` | 未执行定位 | 未启用、不适用或输入/方法闸门未通过 |
| `relative_price_position` | 相对价格定位 | `BASIC` | 基础价位 | 本比较范围内已通过稳定峰谷的低价模式 |
| `relative_price_position` | 相对价格定位 | `MAINSTREAM` | 主流价位 | 本比较范围内已通过稳定峰谷的中价模式 |
| `relative_price_position` | 相对价格定位 | `PREMIUM` | 高端价位 | 本比较范围内已通过稳定峰谷的高价模式 |

## 3. 交接执行规则

P1从已通过07身份/组合/内部适配的范围候选逐来源商品展开；candidate_product_id=EXT07_加完整64位概念SHA256；scope_candidate_id=SHA256(BATCH+scope_type+scope_id+final_level+final_profile+leaf+concept_id的长度前缀规范序列)。price_input_id按来源完整商品键、spec_fact_id、metric_role、价格观测键生成，SPEC_ONLY按有依据的候选规格事实键生成。不能把一批候选×全部竞品做笛卡尔关联。

P2久谦逐data_provider+competitor_platform+city_name+competitor_sku_id关联冻结的基础表，再加collection_date关联日快照。current_sale_price→CURRENT_OFFER、list_price→LIST_PRICE、member_price→MEMBER_PRICE；discount_tags/flash_sale_info只有能证明作用于该报价时才能改为PROMOTION_PRICE，否则CURRENT_OFFER。当前价与划线价相等不自动证明日常价。公开源只读本BATCH已选证据，按source_id+dataset_id+external_product_code/原始商品键，禁止join久谦。角色、规格、单位、时间、用途任一未验证，价格NULL或UNVERIFIED，原始值留原证据。

P3转换关系：同款EXACT、高相似HIGHLY_SIMILAR、同方向CATEGORY_REFERENCE；同方向不能算同款价格指数。单条匹配概率及资产hash来自已校准商品对，不由覆盖率推测。缺价格但候选属性有效仍输出SPEC_ONLY、price_value=NULL、price_status=MISSING；缺规格时net_content等NULL并明确诊断，05可按其可行规格逻辑补方案，07不推测成本。候选范围键缺失时不造行。

05先检查接口READY再取价格方案；BLOCKED仅阻断该消费者链路，不删07候选事实。05旧卡的裸SKU展开/独立版本接口尚未联调时必须BLOCKED；07不保留双版本兼容。下游全链路发布同时验05/08/09统一批次，失败保留旧完整发布包。当前合同是可编码接口，不证明旧消费者已改造。

## 4. 验收

同一裸SKU分别出现在两个平台/城市时不得串价；同一SKU日常/会员/促销角色分行；公开SKU不得join久谦；相同概念跨两个范围临时candidate_product_id相同、scope_candidate_id不同且各有内部证据；同批重跑ID稳定；无价格保留SPEC_ONLY、价格NULL；05旧接口为BLOCKED且不能启动下游正式推荐。

## 5. 价格定位与价格输入分开

price_status=AVAILABLE只说明来源价格可供其允许用途读取，不证明可分基础/主流/高端。price_position_status与method按07开发卡17.14执行。每个price_input_id单独保留其角色/范围的定位，缺定位不阻断可靠价格/规格交给05，不阻断具备其他条件的候选；不能用不分档掩盖来源血缘未验收。

price_position_diagnostics_json固定键：comparison_scope（source_id/dataset_id或data_provider/competitor_platform/city_name、source_market、leaf、主体/形态/计量、currency_code、standard_price_unit、spec_segment、metric_role、window_start/end）、comparison_set_reference、comparison_set_hash、price_input_ids、sample_count、assigned_count、unassigned_count、target_standard_unit_price、lower_valley、upper_valley、selected_k、model_asset_hash、reason_codes。价格及谷值必须同币种/标准计价单位；未算数值null、ID数组[]，不能伪造边界。reason_codes为字段缺失/UNSUPPORTED_PRICE_ROLE/METHOD_DISABLED/MODEL_NOT_VALIDATED/LESS_THAN_THREE_STABLE_MODES/UNSTABLE_BOUNDARIES/MIXED_POSITIONS/MIXED_COMPARISON_SCOPES等受控原因，完整定义按17.14。

同商品同时有当前、会员、促销、POS均价等价格时分行保留，不先取最低价再赋档。POS_AVERAGE_PRICE和官方参考价角色只在其本身用途下读取，当前V1不混入REGULAR_PRICE分布。若要新增独立POS/批发行情分档，先登记用途和方法再开发，当前不能假装支持。固定人工L/U未在业务原文规定，本接口不因开发过程已有固定阈值配置就自动采用。

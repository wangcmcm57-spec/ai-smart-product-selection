# 算法卡_04_目标画像 SKU 表现算法

更新时间：2026-10-07

业务原始依据：`算法卡_04_目标画像SKU表现_业务提供最新原始版_20260731.md`

开发交付定位：将“目标画像现有高表现锚点商品识别算法”的业务原文和 2026-10-05 产品确认结论转成数据开发可建表、可计算、可验收的口径。

重要原则：

```text
业务原文中的算法逻辑不得压缩删除。
数据暂不满足的地方，只能按已确认的 V1 边界输出缺失状态，不能改写成另一套简单算法。
```

---

## 1. 算法目标与边界

### 1.1 算法目标

在指定城市或城市群、品类、门店品类等级群和消费者类型下，识别消费者实际购买且经营表现健康的现有高表现锚点商品。

算法 04 输出的锚点用于：

```text
后续购物篮分析默认锚点
新品候选标准化与合并的商品证据
新品机会证据合成与风险门禁的证据
新品推荐优先级与开发需求编排的解释证据
```

### 1.2 算法不做什么

算法 04 不直接回答：

```text
应该开发什么新品
新品应该增加什么配料
新品应该定什么价格
新品是否与现有货盘重复
```

候选新品必须由后续价格带算法、购物篮算法、竞品趋势、算法 08 候选标准化合并、算法 09 风险门禁和算法 10 推荐编排继续产生。

---

## 2. 上下游链路

```text
算法 01：会员画像 final_profile
        +
算法 02：门店品类等级 final_level
        +
算法 03：门店群消费者贡献和目标画像
        +
有效会员小票、商品、到货、订购、促销、毛利
        ↓
算法 04：识别现有高表现锚点商品
        ↓
后续购物篮、价格、竞品、趋势和新品机会算法
```

锚点与新品必须分开：

```text
现有锚点：黑椒牛柳丝 200g
购物篮关联：圆葱、青椒
候选新品：圆葱黑椒牛柳丝 200g、青椒黑椒牛柳丝 200g
```

算法 04 不得把候选新品提前写成已验证现有锚点。

---

### 2.1 编号、职责和运行顺序冻结

| 算法编号 | 算法名称 | 本算法做什么 | 本算法不做什么 | 上游读取谁 | 下游交给谁 | 正式运行顺序 |
|---|---|---|---|---|---|---|
| 04 | 目标画像 SKU 表现 | 对现有 SKU 和标准商品独立计算表现、统计证据、稳定性与锚点状态 | 不生成新品、不算购物篮关联、不判断新品价格带和最终优先级 | 算法 01 画像、算法 02 门店品类等级、算法 03 门店群汇总/画像贡献及基础经营数据 | 算法 05/06/07 直接读取；随后进入算法 08、09、10 | `01 -> 02 -> 03 -> 04 -> 05/06/07 -> 08 -> 09 -> 10` |

### 2.2 算法编号与上游依赖闸门

算法 04 只消费已经发布的上游正式结果，不在本算法内重算算法 01、02 或 03。

| 上游结果 | 可消费状态 | 不可消费状态/处理 | 版本和周期闸门 |
|---|---|---|---|
| `dim_customer_profile` | 同一 `algorithm_batch_version + customer_id` 唯一且 `final_profile` 非空 | 缺失、重复或画像批次与本算法不一致：阻断算法 04 整批发布 | 校验 `algorithm_batch_version`、`calculation_end_date` 和 `dim_customer_profile_region_param.published_flag = 1`；会员交易继承算法 01 固定过滤条件 |
| `mart_store_category_level` | 只使用同批次 `result_status = SUCCESS` 的门店品类行；读取 `promotion_discount_scope` 固定口径 | `NOT_CALCULABLE` 门店不得进入门店群 | 校验 `algorithm_batch_version`、`calculation_start_date/end_date`、范围、品类和门店唯一；上游成功状态由平台依赖调度保证，不读取算法 02 专用发布表 |
| `mart_store_group_consumer_summary` | 作为算法 04 应处理门店群骨架；读取合法门店群、`store_cnt`、周期和 `result_status` | `NOT_CALCULABLE` 表示合法门店群无有效会员消费；该组不伪造 `final_profile` 或算法 04 正式结果行 | 校验同批、同周期、门店群唯一；必须与贡献明细由算法 03 同批原子发布 |
| `mart_store_group_consumer_contribution` | 对汇总状态为 `SUCCESS`、`SINGLE_PROFILE`、`NO_OBVIOUS_MAIN` 的门店群，读取画像明细、主力标记和销售额 | 汇总表为 `NOT_CALCULABLE` 时明细应为 0 行；其他缺失或不一致属于上游交付失败 | 校验 `algorithm_batch_version`、`contribution_start_date/end_date`、门店群、`final_profile` 唯一，并与汇总表双向对账 |

平台未确认算法 01、02、03 同一批次成功发布，或算法 03 两张正式表未能证明整体可读时：

```text
不启动算法 04 正式计算；不重算上游、不跨范围回退、不写或覆盖任何算法 04 正式结果及参数。
失败原因进入平台现有调度审计或质量问题记录。
```

### 2.3 正式结果与过程表的边界

| 类型 | 表 | 是否下游正式读取 | 写入边界 |
|---|---|---:|---|
| 运行级过程数据集 | `mart_sku_repurchase_7d_pre19` | 否，仅由算法 04 本次运行读取 | 保留该逻辑名称；使用 CTE、临时表、临时分区或平台已有过程数据集实现，不要求新增持久化正式表 |
| 正式结果表 | `mart_target_profile_sku_performance` | 是 | 只写有合法 SKU 主键的明细；有画像但无合法 SKU 的组只写锚点汇总 `NO_VALID_SKU` |
| 正式结果表 | `mart_target_profile_product_performance` | 是 | 从交易级和门店日级过程数据按标准商品独立重算后写入 |
| 正式结果表 | `mart_target_profile_anchor_summary` | 是 | 每个合法范围/品类/门店群/画像一行；算法 03 无消费组不写行，有画像但无合法 SKU 时写 `NO_VALID_SKU` |
| 正式参数表 | `mart_target_profile_sku_performance_params` | 是（复算/验收） | 只写实际计算的动态参数、评分层、回退原因和 JSON 结构 |

### 2.4 运行流程和表关系

算法 04 是离线批量识别现有 SKU 锚点，不是前端查询时实时生成新品。

第一段：运行级暂存计算。

```text
触发：每月完整自然月批次调度；同批源数据修正按原批次重跑。
输入：有效会员小票、商品、门店群、目标画像。
过程对象：应处理门店群清单、mart_sku_repurchase_7d_pre19、SKU/标准商品/锚点汇总/动态参数暂存结果和质量检查结果。
以上对象不作为下游正式接口。
```

第二段：现有 SKU 表现和锚点识别。

```text
输入：算法 01-03 正式结果 + 前置复购结果 + 小票 + 商品 + 到货/订购 + 毛利 + 可订可售。
输出：
mart_target_profile_sku_performance
mart_target_profile_product_performance
mart_target_profile_anchor_summary
mart_target_profile_sku_performance_params
```

第三段：前端查询读取结果。

```text
采购前端只传入城市、消费者画像、品类、门店群等筛选条件。
系统读取已经计算好的锚点结果和解释字段。
算法 04 不生成候选新品，也不判断候选新品是否值得开发。
```

运行写入边界（必须按本顺序执行）：

```text
1. 上游闸门未通过：任务失败，不写或覆盖任何正式结果；失败原因写平台现有调度审计或质量问题记录。
2. 算法 03 汇总表已形成合法门店群但 `result_status = NOT_CALCULABLE`：把该键登记为应处理对象中的正常排除项；算法 04 不伪造 `final_profile`，不写 SKU、标准商品、锚点汇总或参数行。
3. 算法 03 存在合法画像明细但没有合法 SKU：按该 `final_profile` 写 `anchor_summary.result_status = NO_VALID_SKU`，锚点 JSON 写 `[]`；不伪造 SKU 或标准商品行。
4. 有合法 SKU 但某 SKU 的非阻断解释字段不可用：按字段合同写 NULL 和质量状态；核心评分字段不可计算时写 `DATA_INCOMPLETE`，不得进入正式锚点。
5. 全批暂存结果完成后执行第 29.5.1、32 章全部自行验收。所有阻断检查通过后，按 `algorithm_batch_version` 原子发布三张正式结果表和本批首次计算或重跑复用的动态参数；任一可靠性检查失败时整批不发布、不追加、不覆盖。
```

同批已有可靠正式结果时，失败重跑保持旧结果不变。下游只在平台标记算法 04 同批次成功后启动。

---

## 3. 正式范围与结果粒度

### 3.1 计算范围

沿用算法 02、03 的正式范围：

```text
CITY：单城市
CITY_CLUSTER：业务配置城市群
```

门店群支持：

```text
指定 final_level
ALL_RATED
```

禁止在数据不足时自动扩大到其他城市、城市群或华东大区。

### 3.2 消费者类型范围

底层对算法 03 中全部有有效消费的 `final_profile` 计算 SKU 表现。

产品默认：

```text
算法 03 存在正式主力
-> 展示 is_main_profile = 1 的消费者类型

算法 03 为 NO_OBVIOUS_MAIN
-> 展示相对主力候选，并明确没有明显主力

前端筛选其他消费者类型
-> 读取已计算结果，但不能称为主力人群
```

捡漏型沿用算法 01 终止标签：

```text
final_profile = 捡漏型
family_level = NOT_APPLICABLE
frequency_level = NOT_APPLICABLE
price_attitude = NOT_APPLICABLE
```

### 3.3 SKU 明细唯一粒度

```text
algorithm_batch_version
+ performance_start_date
+ performance_end_date
+ scope_type
+ scope_id
+ category_granularity
+ category_code
+ store_group_type
+ final_level
+ final_profile
+ sku_id
```

只输出区域门店群正式结果，不生成单门店正式综合得分。

### 3.4 大中小分类

大、中、小分类分别从小票明细重新筛选、聚合、标准化和评分：

```text
大分类结果 != 下属中分类结果平均
中分类结果 != 下属小分类结果平均
```

采购选择“全部小分类”时：

```text
每个小分类独立计算 CRITIC、综合得分和锚点组
最后合并展示
```

禁止将全部小分类 SKU 放入同一评分池。

---

## 4. 数据周期与版本

### 4.1 正式周期

每月使用最近 3 个数据完整自然月，与算法 02、03 周期一致。

例如 2026 年 7 月运行：

```text
performance_start_date = 2026-04-01
performance_end_date   = 2026-06-30
```

### 4.2 统一批次与上游锁定

全链路调度传入 `algorithm_batch_version = 'BATCH_' + DATE_FORMAT(performance_end_date, 'yyyyMM')`。`performance_end_date` 必须是本批次统一数据截止月份的最后一天；算法 01～04、城市算法区域映射快照和本批正式参数使用同一个批次。

首次运行必须由全链路调度和平台输入血缘锁定：

```text
algorithm_batch_version
category_level_start_date / category_level_end_date
consumer_contribution_start_date / consumer_contribution_end_date
dim_algorithm_batch_city_region_snapshot 的本批映射
算法 01、02、03 同批平台成功状态和实际输入血缘
算法 02、03 与算法 04 使用的同一份 dim_sku 分类输入
listing_snapshot_date
run_id
```

`algorithm_batch_version` 是唯一业务版本；`run_id` 只区分实际运行，不参与业务主键。固定业务规则直接按本卡执行，不复制到固定配置 JSON 或独立运行参数表：

```text
listing_scope_aggregation_method = ANY_ACTIVE_STORE
standard_product_listing_method = ANY_ACTIVE_MEMBER
first_purchase_scope = WITHIN_PERFORMANCE_WINDOW
禁止销售额占比分摊进入正式毛利
profile_sales_reconciliation_tolerance = 绝对差 0.01 元，金额保留 2 位
promotion_discount_scope = TOTAL_DISCOUNT_INCL_TIME
```

平台现有任务血缘负责记录本次实际读取的表、分区和代码运行；算法 04 正式表只保留业务复算所需字段和运行 ID，不重复保存平台已有的源版本、输入血缘、代码发布标识或固定配置快照。同一完整月重跑沿用原批次、原城市区域快照、原 `listing_snapshot_date` 和原正式动态参数；验收通过后以新 `run_id` 原子替换该批三张正式结果表及参数表。规则变化默认从下一完整月生效。

算法 01、02、03 同批正式结果或源数据发生修正时，平台按依赖链重跑算法 04；算法 04 仍按整个 `algorithm_batch_version` 原子替换，不得把不同上游运行的结果拼成同一正式批次。

禁止同一批结果混用不同周期、不同画像结果或不同门店群结果。

周期闸门：

```text
dim_customer_profile.calculation_end_date    = performance_end_date
算法02 calculation_start_date/end_date       = performance_start_date/end_date
算法03 contribution_start_date/end_date      = performance_start_date/end_date
算法01/02/03 algorithm_batch_version         = 算法04 algorithm_batch_version
```

任一周期无法证明一致时，本次任务失败并写平台质量记录，不发布或覆盖算法 04 正式结果。

### 4.3 当前在售快照

历史表现使用正式 3 个月周期。当前在售状态使用本批锁定的正式可订可售快照；商品基础表和门店基础表读取范围由平台任务血缘锁定，不在历史重跑时读取今天的最新记录。

```text
首次运行：在平台确认已完整交付的状态分区中，选择不晚于本次运行数据截止时点的最大 business_date。
分区验收：该日期分区必须完整交付，当前有效门店范围可核对且主键唯一；分区不完整或同键冲突时批次不发布。个别门店 SKU 没有有效状态行时不回退到旧日期，按第 10.1 节写 `NULL + DATA_INSUFFICIENT`。
同批重跑：复用该批上一份可靠正式结果记录的 listing_snapshot_date，不重新选择今天的最新日期。
```

下一个完整月批次重新锁定当前状态。历史批次不得因后来的商品状态变化而改写。

## 5. 输入数据与字段合同

### 5.1 必需数据集

| 逻辑数据集 | 是否必需 | 用途 | V1 来源说明 |
|---|---|---|---|
| 算法 01 正式会员画像 | 必须 | 取得每名会员唯一 `final_profile` 和统一批次 | `dim_customer_profile`；按 `algorithm_batch_version + customer_id` 唯一 |
| 算法 02 正式门店品类等级 | 必须 | 取得正式门店成员、`final_level` 和促销折扣口径 | `mart_store_category_level`；只读取同批 `result_status = SUCCESS` 行，不读取算法 02 专用发布表 |
| 算法 03 门店群汇总 | 必须 | 形成算法 04 应处理门店群骨架，并区分合法无会员消费与上游缺失 | `mart_store_group_consumer_summary`；必须与贡献明细同批原子发布 |
| 算法 03 消费者贡献明细 | 必须 | 取得消费者画像、主力/相对主力标记和画像销售额 | `mart_store_group_consumer_contribution`；与汇总表按门店群键双向对账 |
| 小票商品明细 | 必须 | 销售、数量、小票、会员及购买时间 | `data_agent.dws_member_order_item_detail_df_all_new` |
| 商品基础表 | 必须 | 商品编码、名称、品类、单位、单位重量和 SPU | `dim_sku`；读取平台全链路任务锁定的同一份商品分类输入，独立换码/替代关系不作为 V1 输入 |
| 门店基础表/区域映射 | 必须 | 门店、城市、营业状态和算法范围 | `dim_store` + 同批 `dim_algorithm_batch_city_region_snapshot`；算法 04 不重建范围 |
| 实际到货/订购明细 | 必须 | 有效在售 SKU 日、实际收货量、订购覆盖 | `mart_sku_margin_loss`（物理 `data_analysis.dwd_mart_sku_margin_loss`）+ 可订可售表 |
| 商品毛利明细 | 必须 | SKU 总销售额、全链路毛利额；目标画像成本按 V1 单位成本口径分摊 | `mart_sku_margin_loss`；缺字段不得补零 |
| 折扣代理字段 | 必须 | 非促销 SKU 日、实付价格和折扣阶梯 | V1 不接促销活动表，用有效交易行 `discount_amt > 0` 代理，并写方法状态 |
| 门店商品日价格表 | 条件必须 | 原价、成交价和成本备选 | `mart_store_sku_daily_price`；按完整主键验收，含税出库到店成本缺失或映射不唯一时不得启用成本备选 |
| 商品状态表 | 解释性 | 历史锚点季节/停售原因 | `dim_product_status`；V1 不参与评分，版本、区域或商品不能唯一命中时写不可用状态 |
| 7 天复购运行级过程数据 | 必须 | 复购分子、分母、原始复购率 | V1 在算法 04 运行内先生成逻辑数据集 `mart_sku_repurchase_7d_pre19`；不要求独立持久化正式表 |

### 5.1.1 逻辑表与物理表映射硬规则

共享范围快照数据合同已经明确为 `dim_algorithm_batch_city_region_snapshot`。算法 04 按下列物理字段映射读取，不引入历史范围版本字段或历史范围快照：

```text
algorithm_region_code AS scope_id
algorithm_region_name AS scope_name
scope_type             AS scope_type
```

```text
逻辑 mart_sku_margin_loss
-> 当前物理映射：data_analysis.dwd_mart_sku_margin_loss

逻辑 Doris 小票
-> 当前物理表：data_agent.dws_member_order_item_detail_df_all_new
```

上游正式结果由平台依赖调度确认成功后读取，不得自行创建临时替代结果冒充 `mart_store_category_level`、`mart_store_group_consumer_contribution` 或 `mart_store_group_consumer_summary`。

`dim_sku`、`dim_store` 物理源若带 `inc_day`、`dt` 或其他快照字段，必须读取平台本次全链路任务锁定的表和分区，再按数据合同主键检查唯一；不能把所有快照直接连接到交易明细，也不能按更新时间任取一行掩盖冲突。

### 5.1.2 算法 03 字段映射（物理字段名与本卡别名）

算法 03 两张正式表的周期字段名均为 `contribution_start_date` / `contribution_end_date`。算法 04 为区分自身表现周期，内部映射为：

```text
contribution_start_date AS consumer_contribution_start_date
contribution_end_date   AS consumer_contribution_end_date
```

上游接口验收仍以算法 03 物理字段名为准。算法 03 汇总表先确定门店群键和 `result_status`；仅对汇总状态为 `SUCCESS`、`SINGLE_PROFILE`、`NO_OBVIOUS_MAIN` 的门店群读取贡献明细。汇总状态为 `NOT_CALCULABLE` 时贡献明细必须为 0 行，算法 04 不构造 `final_profile`。两列周期必须分别等于本批 `performance_start_date` / `performance_end_date`。

### 5.2 Doris 小票商品明细字段

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 订单商品明细ID | `order_item_id` | varchar(64) | 必须 | Doris `data_agent.dws_member_order_item_detail_df_all_new.order_item_id` | 商品行唯一键；按本卡第 6.1 节去重并检查冲突 |
| 小票ID | `order_id` | varchar(64) | 必须 | Doris `data_agent.dws_member_order_item_detail_df_all_new.order_id` | 公司级小票唯一编码，可作为 `ticket_key` |
| 门店编码 | `store_id` | varchar(64) | 必须 | Doris `data_agent.dws_member_order_item_detail_df_all_new.store_id` | 与 `dim_store.store_id` 和算法 02 对齐 |
| 会员ID | `customer_id` | varchar(64) | 必须 | Doris `data_agent.dws_member_order_item_detail_df_all_new.customer_id` | 与算法 01 会员画像对齐；画像会员需通过有效会员过滤 |
| 是否会员 | `is_customer` | int | 必须 | Doris `data_agent.dws_member_order_item_detail_df_all_new.is_customer` | 会员交易过滤必须为 `1`；不能用 `customer_id` 非空替代 |
| 销售SKU编码 | `sku_id` | varchar(64) | 必须 | Doris `article_id` | 与 `dim_sku.sku_id` 对齐 |
| 营业日期 | `business_date` | date | 必须 | Doris `business_date` | 交易营业日期；需与 `DATE(inc_time)` 一致 |
| 销售时间 | `sale_time` | datetime | 必须 | Doris `inc_time` | 判断 19:00 复购和 19:30 自然动销 |
| 商品行实付金额 | `line_transaction_amt` | decimal(18,6) | 必须 | Doris `usual_amt` | 目标画像 SKU 销售额；有效交易要求大于 0 |
| 商品行优惠金额 | `discount_amt` | decimal(18,6) | 条件必须 | Doris `discount_amt` | V1 促销/折扣代理；缺失时不伪造促销状态 |
| 销售标准量 | `sales_standard_qty` | decimal(18,6) | 必须 | Doris `weight` | 算法统一使用 `sales_standard_qty = weight`；计量类型和单位由 `dim_sku` 解释 |
| 是否时段促销 | `is_hour_promotion` | int | 可选 | Doris `is_hour_promotion` | 折扣解释字段 |
| 小时优惠金额 | `hour_discount_amt` | decimal(18,6) | 可选 | `data_agent.dws_member_order_item_detail_df_all_new.hour_discount_amt` | 会员当天同小时累计优惠金额，不是商品行金额，不得与商品行 `discount_amt` 相加 |
| 订单状态 | `order_status` | varchar(64) | 必须 | Doris `order_status` | 有效交易过滤，V1 保留 `os.completed` |
| 是否退货 | `is_return` | int | 必须 | Doris `is_return` | 有效交易过滤，V1 保留 `0` |
| 退款类型 | `refund_type` | varchar(64) | 条件必须 | Doris `refund_type` | 退款/冲销过滤辅助字段；枚举未冻结前仅做质量检查 |
| 业务来源 | `business_source` | varchar(64) | 可选 | Doris `business_source` | 测试交易或特殊来源过滤辅助字段 |
| 订单更新时间 | `update_time` | datetime | 必须 | Doris `update_time` | `order_item_id` 去重时按最新记录保留，并用于源数据追溯 |

### 5.3 商品基础表字段

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 交易商品编码 | `sku_id` | varchar(64) | 必须 | `dim_sku.sku_id` | 与 Doris `article_id` 对齐 |
| 商品编码 | `product_id` | varchar(64) | 可选 | `dim_sku.product_id` | 商品主数据追溯编码；不参与标准商品主键判定 |
| 商品名称 | `sku_name` | varchar(256) | 必须 | `dim_sku.sku_name` | SKU 展示名称 |
| 规格原文 | `specification` | varchar(128) | 可选 | `dim_sku.specification` | 商品主数据原始规格；不自动解析为净含量 |
| SPU编码 | `spu_id` | varchar(64) | 可选 | `dim_sku.spu_id` | 标准商品层聚合；无有效值时使用 `SKU_ONLY` |
| 大类编码 | `category_level1_code` | varchar(64) | 必须 | `dim_sku.category_level1_code` | 大类计算；按数据合同不能为空 |
| 大类名称 | `category_level1_name` | varchar(128) | 必须 | `dim_sku.category_level1_name` | 大类计算；按数据合同不能为空 |
| 中类编码 | `category_level2_code` | varchar(64) | 必须 | `dim_sku.category_level2_code` | 中类计算；按数据合同不能为空 |
| 中类名称 | `category_level2_name` | varchar(128) | 必须 | `dim_sku.category_level2_name` | 中类计算；按数据合同不能为空 |
| 小类编码 | `category_level3_code` | varchar(64) | 必须 | `dim_sku.category_level3_code` | 小类计算；按数据合同不能为空 |
| 小类名称 | `category_level3_name` | varchar(128) | 必须 | `dim_sku.category_level3_name` | 小类计算；按数据合同不能为空 |
| 销售单位 | `sale_unit` | varchar(32) | 必须 | `dim_sku.sale_unit` | 计量标准化 |
| 单位重量 | `unit_weight_kg` | decimal(18,6) | 条件必须 | `dim_sku.unit_weight_kg` | 定量包装、件转重量时使用 |
| 存储温层 | `temperature_layer` | varchar(64) | 可选 | `dim_sku.temperature_layer` | 商品属性输出，缺失不阻断经营表现 |
| 品牌 | `brand_name` | varchar(128) | 可选 | `dim_sku.brand_name` | 商品属性输出，缺失不阻断经营表现 |

### 5.4 毛利损耗表字段

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 营业日期 | `business_date` | date | 必须 | `mart_sku_margin_loss.business_date` | 日期 |
| 门店编码 | `store_id` | varchar(64) | 必须 | `mart_sku_margin_loss.store_id` | 门店 |
| 交易商品编码 | `sku_id` | varchar(64) | 必须 | `mart_sku_margin_loss.sku_id` | 销售 SKU |
| 销售额 | `sales_amt` | decimal(18,6) | 必须 | `mart_sku_margin_loss.sales_amt` | 日门店 SKU 总销售额 |
| 销售数量 | `sales_qty` | decimal(18,6) | 条件必须 | `mart_sku_margin_loss.sales_qty` | 计件商品总量校验 |
| 销售重量 | `sales_weight_kg` | decimal(18,6) | 条件必须 | `mart_sku_margin_loss.sales_weight_kg` | 称重商品总量校验 |
| 门店进货数量 | `receipt_qty` | decimal(18,6) | 条件必须 | `mart_sku_margin_loss.receipt_qty` | 实际验收数量；计件商品售罄率分母优先使用 |
| 门店进货重量 | `receipt_weight_kg` | decimal(18,6) | 条件必须 | `mart_sku_margin_loss.receipt_weight_kg` | 实际验收重量；称重商品售罄率分母优先使用 |
| 门店进货金额 | `receipt_amt` | decimal(18,6) | 可选 | `mart_sku_margin_loss.receipt_amt` | 到货金额解释 |
| 门店订购数量（订购单位） | `order_qty` | decimal(18,6) | 可选 | `mart_sku_margin_loss.order_qty` | 原订购单位数量；计件商品订购量优先使用 |
| 门店订购数量（重量口径） | `order_weight_kg` | decimal(18,6) | 可选 | `mart_sku_margin_loss.order_weight_kg` | 订购数量换算重量；称重商品订购量优先使用 |
| 门店订购额 | `order_amt` | decimal(18,6) | 可选 | `mart_sku_margin_loss.order_amt` | 订购覆盖 |
| 全链路毛利额 | `full_link_margin_amt` | decimal(18,6) | 必须 | `mart_sku_margin_loss.full_link_margin_amt` | SKU 整体毛利优先口径 |
| 全链路毛利率 | `full_link_margin_rate` | decimal(18,8) | 可选 | `mart_sku_margin_loss.full_link_margin_rate` | SKU 整体毛利率 |
| 门店毛利额 | `store_margin_amt` | decimal(18,6) | 可选 | `mart_sku_margin_loss.store_margin_amt` | 门店口径解释 |
| 总折扣额 | `discount_amt` | decimal(18,6) | 条件必须 | `mart_sku_margin_loss.discount_amt` | 门店 SKU 日总折扣，与 Doris 商品行同名字段粒度不同；本批按算法 02 已锁定的包含关系读取，不与时段折扣相加 |
| 促销折扣额 | `promotion_discount_amt` | decimal(18,6) | 可选 | `mart_sku_margin_loss.promotion_discount_amt` | 若可到 SKU 日粒度，优先用于非促销判断 |
| 时段折扣额 | `time_period_discount_amt` | decimal(18,6) | 可选 | `mart_sku_margin_loss.time_period_discount_amt` | 若可到 SKU 日粒度，折扣阶梯解释 |

### 5.5 门店 SKU 可订可售表字段

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 日期 | `business_date` | date | 必须 | `mart_store_sku_daily_sale_order_status.business_date` | 状态日期 |
| 门店编码 | `store_id` | varchar(64) | 必须 | `mart_store_sku_daily_sale_order_status.store_id` | 门店 |
| 销售商品编码 | `sku_id` | varchar(64) | 必须 | `mart_store_sku_daily_sale_order_status.sku_id` | 销售 SKU |
| 订购商品编码 | `order_sku_id` | varchar(64) | 必须 | `mart_store_sku_daily_sale_order_status.order_sku_id` | 订购 SKU，可能与销售 SKU 不一致 |
| 是否可售 | `is_saleable` | tinyint | 必须 | `mart_store_sku_daily_sale_order_status.is_saleable` | `1` 可售，`0` 不可售 |
| 是否可订 | `is_orderable` | tinyint | 必须 | `mart_store_sku_daily_sale_order_status.is_orderable` | `1` 可订，`0` 不可订 |
| 数据更新时间 | `data_update_time` | datetime | 必须 | `mart_store_sku_daily_sale_order_status.data_update_time` | 快照更新时间 |

`orderable_sellable_flag` 可按以下规则生成：

```text
is_saleable = 1 AND is_orderable = 1 -> orderable_sellable_flag = 1
is_saleable / is_orderable 均为明确 0/1，且不同时为 1 -> orderable_sellable_flag = 0
任一字段缺失或无法映射 -> orderable_sellable_flag = NULL，并写平台质量记录
```

当前物理源若无法提供合同要求的 `order_sku_id`、`is_saleable` 或 `is_orderable`，必须在平台质量记录中登记缺失字段并阻断本批发布，不得用收货、销量或其他代理字段补写订购状态。

### 5.6 门店商品日价格表字段

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 日期 | `business_date` | date | 必须 | `mart_store_sku_daily_price.business_date` | 日期 |
| 门店编码 | `store_id` | varchar(64) | 必须 | `mart_store_sku_daily_price.store_id` | 门店 |
| 仓编码 | `warehouse_id` | varchar(64) | 必须 | `mart_store_sku_daily_price.warehouse_id` | 门店对应供货仓编码；先用于仓商品日成本校验 |
| 仓名称 | `warehouse_name` | varchar(128) | 可选 | `mart_store_sku_daily_price.warehouse_name` | 门店对应供货仓名称，展示和对账使用 |
| 销售商品编码 | `sku_id` | varchar(64) | 必须 | `mart_store_sku_daily_price.sku_id` | 销售 SKU |
| 验收商品编码 | `receipt_sku_id` | varchar(64) | 必须 | `mart_store_sku_daily_price.receipt_sku_id` | 验收/进货 SKU |
| 出库到店成本含税 | `outbound_arrival_cost_tax_included` | decimal(18,6) | 条件必须 | `mart_store_sku_daily_price.outbound_arrival_cost_tax_included` | 成本备选口径；缺失时不得用其他价格字段替代 |
| 出库到店金额含税 | `outbound_arrival_amt_tax_included` | decimal(18,6) | 可选 | `mart_store_sku_daily_price.outbound_arrival_amt_tax_included` | 到店金额解释 |
| 销售原价 | `original_sale_price` | decimal(18,6) | 可选 | `mart_store_sku_daily_price.original_sale_price` | 折扣率和价格解释 |
| 商品平均售价 | `avg_sale_price` | decimal(18,6) | 可选 | `mart_store_sku_daily_price.avg_sale_price` | 成交均价 |
| 19点前平均售价 | `pre19_avg_sale_price` | decimal(18,6) | 可选 | `mart_store_sku_daily_price.pre19_avg_sale_price` | 价格解释 |
| 19点后售价 | `post19_sale_price` | decimal(18,6) | 可选 | `mart_store_sku_daily_price.post19_sale_price` | 折扣阶梯解释 |

---

## 6. 前置过滤与对账

### 6.1 全量有效交易与会员有效交易分层

算法 04 必须拆成两套事实集，不能用会员过滤后的交易去计算全量自然动销或 SKU 整体经营：

```text
valid_all_txn：全量有效正向销售，用于 SKU 总销售、自然动销、折扣阶梯、覆盖诊断和与经营日表对账。
valid_profiled_member_txn：在 valid_all_txn 上继承算法01/03会员过滤并成功关联画像，用于目标画像销售、偏好、复购和目标画像毛利。
```

两套事实集都先执行：

```text
按 order_item_id 去重：同一键按 update_time 降序保留最新记录；时间相同但字段冲突时阻断正式发布
business_date = DATE(inc_time)，不一致进入异常清单
order_id、inc_time、store_id、article_id 非空
order_status = 'os.completed'
is_return = 0
usual_amt > 0
weight > 0
```

`valid_profiled_member_txn` 继续增加：

```text
is_customer = 1
customer_id 非空且不以“6”开头
同一 customer_id + business_date 的有效小票数 > 5 时，剔除该会员当日全部交易
剔除算法 01 已标记的异常会员日
customer_id 能关联本次锁定的 algorithm_batch_version，且 final_profile 非空
```

`refund_type（退款类型）`、`business_source（业务来源）`等字段只在已确认枚举后增加精确过滤；未确认的枚举不能被开发自行扩大为删除条件。过滤条件调整必须同步修改算法 01～04 的算法卡、公共实现和固定验收样例，并从下一个 `algorithm_batch_version（统一算法批次版本）`生效；实际代码运行由平台任务血缘追溯。

过滤方式字段：

```text
valid_transaction_filter_method = SOURCE_TABLE_CLEANED
或 RULE_FILTERED
```

算法 04 的会员画像、偏好、复购和目标画像毛利必须直接继承算法 01 固定的有效会员过滤条件，并调用与算法 01、02、03 相同的公共实现；不建立或传递独立会员过滤版本字段。上述会员指标只能使用 `valid_profiled_member_txn（已贴标有效会员交易集）`；全量 SKU 销售、19:30 前自然动销和折扣阶梯不得误用该集合。

### 6.2 商品映射

```text
商品编码必须关联唯一正式商品记录
SKU 必须成功映射到目标品类
交易发生时只能命中一条有效品类映射
```

商品分类读取必须使用平台全链路调度为算法 02、03、04 锁定的同一份 `dim_sku` 表和分区；同批源数据补数或商品属性更新不得只让算法 04 改用今天的分类重新划分历史比较组。实际表和分区由平台任务血缘追溯，不新增分类读取绑定 JSON。

V1 商品分类使用当前商品基础表分类；商品分类历史变化概率极低，暂不做历史分类回溯。

如果一对多或品类冲突：

```text
判定为输入主键或商品映射质量失败
阻断算法 04 整批发布，由平台质量记录保存冲突键和来源分区
```

### 6.3 小票内相同 SKU 合并

同一小票内相同 SKU 多行先合并：

```text
ticket_key + sku_id
```

V1：

```text
ticket_key = order_id
```

合并字段：

```text
line_transaction_amt = SUM(usual_amt)
discount_amt = SUM(discount_amt)
sales_standard_qty = SUM(weight)
sale_time = MIN(inc_time)
```

同一会员同一天拆成多张小票不能被误判为 7 天复购。

### 6.4 上游金额对账

同一门店群、品类和消费者类型下：

```text
算法 04 各 SKU 销售额合计
= 算法 03 对应消费者类型销售额
```

同时必须做两层对账：

```text
valid_all_txn SKU 销售额合计
= 毛利损耗表同日门店 SKU 销售额（允许数据合同登记的金额误差）

valid_profiled_member_txn 目标画像销售额合计
= 算法03对应门店群、品类、消费者画像的 profile_sales_amt
```

画像层统一使用同一币种和 `DECIMAL`，按相同舍入规则保留 2 位小数，并在运行级验收结果中记录两侧金额、绝对差、相对差、金额精度和过滤/去重行数。V1 固定绝对差小于等于 0.01 元为通过；不得用浮点误差、缩小范围或平均值自动“对平”。全量经营表对账使用其数据合同登记的容差，不能沿用画像层阈值。

每个处理单元先独立计算对账结论，用于定位影响范围；任一处理单元对账失败都表示本批暂存结果未通过可靠性验收，算法 04 整批不发布、不追加、不覆盖。批次级公共根因和处理单元定位键写入平台质量记录，不把失败状态伪装成正式结果行。

全量经营表对账失败时记录自然动销与 SKU 总经营链路根因；画像层对账失败时记录目标画像链路根因。两类失败都会使整批验收不通过，不能只删除受影响字段后继续发布。

## 7. 全天行为与时间窗口

### 7.1 全天指标

以下目标画像指标使用 `valid_profiled_member_txn` 全天会员交易：

```text
销售额
销量
小票数
购买会员数
目标画像会员渗透率
目标画像相对偏好
近 7 天 19 点前复购
目标画像商品毛利
```

以下整体经营指标使用 `valid_all_txn` 或合同经营日表，不受会员画像过滤影响：

```text
SKU 总销售额、SKU 总销售量、19:30 前自然动销、19:30 后折扣阶梯、全量 SKU 销售对账
```

### 7.2 自然动销

自然动销使用非促销 SKU 日 19:30 前数据：

```text
非促销 19:30 前售罄率
19:30 前每有效在售门店日标准销售量
```

### 7.3 时间点

```text
复购第二次购买：19:00 前
自然动销售罄：19:30 前
```

两个时间点不能混用。

---

## 8. SKU 基础表现指标

在同一比较组、同一 `final_profile` 下计算：

```text
sku_sales_amt
= SUM(目标画像购买该 SKU 的 line_transaction_amt)

sku_sales_qty
= SUM(目标画像购买该 SKU 的 sales_standard_qty)

sku_ticket_cnt
= COUNT(DISTINCT ticket_key WHERE 目标画像购买该 SKU)

sku_buyer_cnt
= COUNT(DISTINCT customer_id WHERE 目标画像购买该 SKU)

sku_sales_share
= sku_sales_amt / 目标画像在该品类的销售额

sku_buyer_penetration
= sku_buyer_cnt / 目标画像在该品类的去重会员数

sku_ticket_penetration
= sku_ticket_cnt / 目标画像在该品类的去重小票数

sku_avg_paid_price
= sku_sales_amt / sku_sales_qty
```

分母为 0 或空时，不填 0，输出 `NULL` 和状态。

---

## 9. 近 7 天 19 点前复购

### 9.1 业务口径

```text
首次购买：必须发生在本次 3 个月表现周期内，当天时刻不限
第二次购买：首次购买后的第 1 到第 7 个自然日内，且发生在 19:00 前
同一天多张小票不算复购
周期结束前不足 7 天才首次购买的会员不进入分母
```

V1 固定 `first_purchase_scope = WITHIN_PERFORMANCE_WINDOW`：“时间不限”只表示首购当天不受 19:00 限制，不回扫表现周期开始前的历史首购。复购分子必须从同一批具备完整 7 天观察期的首购会员中产生，保证 `0 <= repeat_buyer_cnt_7d_pre19 <= eligible_first_buyer_cnt_7d`。观察不足者不进入正式分子或分母，另输出观察不足首购人数和其中已观察到复购的人数作为诊断；诊断人数不得混入复购率。

### 9.2 V1 前置表

业务原文要求读取现有正式复购结果。

现有指标平台不能稳定支持 SKU 维度复购，所以 V1 必须先按同一口径产出：

```text
mart_sku_repurchase_7d_pre19
```

输出字段：

```text
repeat_buyer_cnt_7d_pre19
eligible_first_buyer_cnt_7d
insufficient_observation_first_buyer_cnt
insufficient_observation_observed_repeat_buyer_cnt_pre19
repurchase_rate_7d_pre19
algorithm_batch_version
```

公式：

```text
repurchase_rate_7d_pre19
= repeat_buyer_cnt_7d_pre19 / eligible_first_buyer_cnt_7d
```

只有复购率、没有分子分母的结果不能进入正式评分。

`repurchase_calc_status` 按以下顺序唯一判定，避免分母为 0 时同时命中两个状态：

```text
eligible_first_buyer_cnt_7d > 0
-> OK

eligible_first_buyer_cnt_7d = 0
AND insufficient_observation_first_buyer_cnt > 0
-> INSUFFICIENT_WINDOW

eligible_first_buyer_cnt_7d = 0
AND insufficient_observation_first_buyer_cnt = 0
-> DENOMINATOR_ZERO
```

`OK` 不要求所有首购会员都具备完整窗口；只要求正式分母大于 0。观察不足会员始终只进入两个诊断人数。

---

## 10. 有效在售、订购与铺货

### 10.1 当前在售

```text
is_saleable = 1 AND is_orderable = 1
    -> orderable_sellable_flag = 1 -> listing_status = ACTIVE
is_saleable / is_orderable 均有明确 0/1，且不同时为 1
    -> orderable_sellable_flag = 0 -> listing_status = INACTIVE
字段缺失或快照不一致
    -> orderable_sellable_flag = NULL -> listing_status = NULL
主键重复或同键状态冲突
    -> 输入质量失败，阻断本批发布
```

当前在售不以近期是否实际到货判断。

#### 10.1.1 门店群集合、当前有效门店集合和覆盖完整性

算法 04 必须分开两个门店集合：

```text
historical_group_store_set：算法 03 汇总对应的算法 02 SUCCESS 门店集合，用于三个月历史表现和 store_cnt。
current_effective_store_set：historical_group_store_set 与本批锁定 dim_store 当前快照关联后 is_open = 1 的门店集合，只用于 listing_snapshot_date 的当前在售判断。
```

生成规则：

1. 以 `mart_store_group_consumer_summary` 的同批门店群键作为应处理骨架；`store_group_type = FINAL_LEVEL` 时读取算法 02 对应 `final_level` 的 `SUCCESS` 门店，`ALL_RATED` 时读取该品类全部 A/B/C/D `SUCCESS` 门店并集。
2. `historical_group_store_set` 必须与算法 03 汇总的 `store_cnt` 一致。门店重复、等级冲突、周期/品类不一致或数量对不上时，阻断本批发布。
3. 当前状态判断再把历史门店集合与平台本次任务锁定的 `dim_store` 输入关联；每个门店必须唯一命中。`is_open = 1` 进入 `current_effective_store_set`，明确 `is_open = 0` 的门店作为当前闭店排除，但不改写历史 `store_cnt`。
4. `dim_store` 缺失、重复、`is_open` 无法解析、当前有效门店为空或状态快照覆盖不足时，当前在售不可计算并阻断正式锚点发布；问题写平台质量记录。
5. 两个集合均按 `algorithm_batch_version + scope_type + scope_id + category_granularity + category_code + store_group_type + final_level` 唯一确定。

V1 固定 `listing_scope_aggregation_method = ANY_ACTIVE_STORE`。状态表在同一 `listing_snapshot_date` 覆盖全部当前有效门店和待判断 SKU、且主键唯一后：

```text
至少一个当前有效门店 is_saleable = 1 AND is_orderable = 1
    -> orderable_sellable_flag = 1
    -> listing_status = ACTIVE

所有当前有效门店均覆盖，且没有任何门店同时可售可订
    -> orderable_sellable_flag = 0
    -> listing_status = INACTIVE

覆盖不足、没有有效状态行、快照不一致或门店状态未知
    -> orderable_sellable_flag = NULL
    -> listing_status = NULL
    -> 不进入正式锚点，问题写平台质量记录
主键重复或同键状态冲突
    -> 输入质量失败，阻断本批发布
```

当前在售不使用历史收货或销量代理。规则调整默认从下一完整月批次生效，同批重跑沿用原方法和原 `listing_snapshot_date`。

### 10.2 有效在售 SKU 日

```text
有效在售 SKU 日 = 门店当天该 SKU 实际收货重量或数量 > 0
```

```text
available_store_day_cnt
= COUNT(DISTINCT store_id + business_date)

sales_per_available_store_day
= sku_sales_amt / available_store_day_cnt

buyers_per_available_store_day
= sku_buyer_cnt / available_store_day_cnt
```

### 10.3 门店订购率

订购覆盖是三个月表现周期指标，分子和分母必须使用同一 `performance_start_date` / `performance_end_date`，不得用当前在售快照分母除以周期分子。

```text
ordered_standard_qty
= CASE
    WHEN measurement_type = WEIGHT THEN order_weight_kg
    ELSE order_qty
  END

eligible_orderable_store_day_cnt
= COUNT(DISTINCT store_id + business_date)
  WHERE performance_start_date <= business_date <= performance_end_date
    AND store_id 属于 historical_group_store_set
    AND is_orderable = 1

eligible_orderable_store_cnt
= COUNT(DISTINCT store_id)
  WHERE 该门店周期内至少有一个 eligible orderable store day

ordered_store_day_cnt
= COUNT(DISTINCT store_id + business_date)
  WHERE 同一门店日属于 eligible orderable store day
    AND ordered_standard_qty > 0

ordered_store_cnt
= COUNT(DISTINCT store_id)
  WHERE 该门店周期内至少有一个 ordered store day

store_order_rate = ordered_store_cnt / eligible_orderable_store_cnt
ordered_store_day_rate = ordered_store_day_cnt / eligible_orderable_store_day_cnt
```

`receipt_qty`、`receipt_weight_kg` 只用于实际收货、有效在售日和售罄率，不能冒充订购分子。商品计量类型对应的真实 `order_qty` 或 `order_weight_kg` 缺失时，四个订购覆盖数值和比率均写 NULL，`order_coverage_status = DATA_INSUFFICIENT`。

V1 门店级可订范围来自 `mart_store_sku_daily_sale_order_status`：

```text
orderable_scope = STORE_SKU_ORDERABLE
```

当前 V1 只使用门店 SKU 日级可订事实，不设置全门店回退分母；缺失或覆盖不全时阻断该指标并写平台质量记录。

订购率不进入综合得分，单独反映门店采用程度。

### 10.4 订购覆盖分组

订购率高低使用自身 Jenks+BIC 动态划分，不使用固定 50%。

```text
形成高低两组 -> 高组 order_coverage_status = HIGH，低组 = LOW
K=1 或没有稳定分割点 -> order_coverage_status = NO_OBVIOUS_SPLIT
订购分子、分母或适用计量字段不可用 -> order_coverage_status = DATA_INSUFFICIENT
```

| 综合表现 | 订购覆盖 | 解释 |
|---|---|---|
| 高 | 高 | 已验证成熟锚点 |
| 高 | 低 | 低铺货高表现，可能存在扩店机会 |
| 低 | 高 | 广泛订购但经营表现较弱 |
| 低 | 低 | 证据较少或整体较弱 |

---

## 11. 计量单位与数量指标

### 11.1 标准单位

```text
称重商品：kg
按件商品：件
定量包装：销售件数 * 单件净含量
液体商品：L 或 ml
蛋类：优先转换为枚；无法转换时按包装件
```

保存：

```text
measurement_type
sale_unit
standard_unit
conversion_factor
measurement_mapping_status
```

V1 单位识别：

```text
千克、kg、公斤、g、克 -> WEIGHT
件、份、盒、包、袋、瓶、个、只 -> QUANTITY
枚 -> PIECE_COUNT
L、ml、毫升、升 -> VOLUME
无法识别 -> UNKNOWN
```

算法 04 统一使用：

```text
sales_standard_qty = weight
```

`weight` 的字段事实和样例验证统一维护在 Doris 字段字典中。本算法卡只定义使用规则：读取有效交易中的 `weight`，再关联商品基础表取得 `sale_unit`、`unit_weight_kg`，由本算法生成 `measurement_type`、`standard_unit` 和必要的换算关系。

口径边界：

```text
weight > 0 但 sale_unit 无法识别 -> 保留金额/人数/复购等诊断值，数量类得分字段写 NULL，并标记 measurement_mapping_status = UNKNOWN。
weight 缺失或 weight <= 0 -> 按算法01/03有效交易规则不进入正式会员 SKU 聚合；不得以 0 补齐。
计量类型不同或无法互转 -> 售罄率、销售深度、标准化单价和单位成本只在同一 measurement_type 内计算。
```

### 11.2 混合计量

同一小分类存在无法互转的计量类型时：

```text
销售额、会员渗透率、偏好、复购和毛利：仍在小分类内比较
销售量深度、到货量和售罄率：只在相同 measurement_type 内标准化
```

禁止将无法互转的数量直接比较。

---

## 12. 目标画像相对偏好

### 12.1 对照组

参考组为：

```text
同一周期
+ 同一城市或城市群
+ 同一品类
+ 同一门店等级群
+ 同一 SKU 有效可购买门店日
+ 除目标画像外的全部有效消费者类型
```

禁止跨城市、跨等级或跨品类比较。

### 12.2 原始渗透率

```text
target_penetration
= 目标画像购买该 SKU 的会员数
  / 目标画像在该 SKU 可购买门店日内购买该品类的会员数

reference_penetration
= 其他画像购买该 SKU 的会员数
  / 其他画像在相同可购买门店日内购买该品类的会员数

preference_index_raw
= target_penetration / reference_penetration
```

### 12.3 Jeffreys 平滑

```text
smoothed_penetration
= (购买该 SKU 会员数 + 0.5)
  / (购买该品类会员数 + 1)

smoothed_preference_index
= target_smoothed_penetration / reference_smoothed_penetration
```

`0.5` 为 Jeffreys 统计先验，不是业务经验阈值。

### 12.4 无参考画像

算法 03 为 `SINGLE_PROFILE` 时：

```text
preference_index = NOT_APPLICABLE
preference_reference_status = NO_REFERENCE_PROFILE
```

该指标从整个比较组的 CRITIC 中移除，其他指标正常计算。

同一比较组存在至少一个其他有效消费者画像时：

```text
preference_reference_status = HAS_REFERENCE_PROFILE
```

---

## 13. 小样本与统计证据

### 13.1 原始值和证据值分开

比例指标保存：

```text
raw_rate
smoothed_rate
credible_lower_95
credible_upper_95
numerator_cnt
denominator_cnt
```

采购页面展示原始比例、分子和分母；正式综合得分使用 95% 下界。

### 13.2 单个比例的 Jeffreys 区间

对成功人数 `x`、总人数 `n`：

```text
posterior = Beta(x + 0.5, n - x + 0.5)

credible_lower_95 = BetaQuantile(0.025, posterior)
credible_upper_95 = BetaQuantile(0.975, posterior)
```

正式评分使用该规则处理：

```text
目标画像会员渗透率
近 7 天 19 点前复购率
```

### 13.3 偏好指数区间

使用 Jeffreys 修正后的目标组和参考组人数构造风险比。

V1 可复算近似：

```text
p_t = (x_t + 0.5) / (n_t + 1)
p_o = (x_o + 0.5) / (n_o + 1)

log_rr = ln(p_t / p_o)

se_log_rr
= sqrt(
    1/(x_t + 0.5) - 1/(n_t + 1)
  + 1/(x_o + 0.5) - 1/(n_o + 1)
  )

preference_lower_95 = exp(log_rr - 1.96 * se_log_rr)
preference_upper_95 = exp(log_rr + 1.96 * se_log_rr)
```

正式偏好指标使用 `preference_lower_95`。

### 13.4 不设置人工人数门槛

```text
存在有效销售的 SKU 全部保留原始结果
不使用“至少 10 人”或“至少 30 张小票”硬删除
```

低证据 SKU：

```text
evidence_status = LOW_EVIDENCE
is_formal_anchor = 0
不作为默认购物篮锚点
```

### 13.5 低证据可复算判断

计算两套分数：

```text
point_evidence_score
= 会员渗透率和复购率使用 Jeffreys 后验均值、
  偏好使用 smoothed_preference_index 时的综合得分

conservative_evidence_score
= 三个比例指标使用各自 95% 下界时的正式综合得分
```

正式表现分始终使用：

```text
sku_performance_score = conservative_evidence_score
```

判断：

```text
point_evidence_score 进入最高表现组
但 95% 下界得分未进入最高表现组
-> evidence_status = LOW_EVIDENCE
-> is_formal_anchor = 0

95% 下界得分仍进入最高表现组
-> evidence_status = SUFFICIENT
```

---

## 14. 19:30 前自然动销

### 14.1 非促销 SKU 日

业务理想口径：

```text
该 SKU 在该门店当天 19:30 前没有参加商品活动
并且 19:30 前没有商品促销折扣
-> non_promotion_sku_day = 1
```

V1 已确认没有促销活动表，使用：

```text
discount_amt > 0
```

作为折扣代理判断。

输出：

```text
promotion_identify_method = DISCOUNT_PROXY_V1
```

### 14.2 实际收货与异常

复用算法 02 日清口径：

```text
WEIGHT 商品：实际收货标准量 = 毛利损耗表.门店进货重量
QUANTITY / PIECE_COUNT 商品：实际收货标准量 = 毛利损耗表.门店进货数量
VOLUME 商品：能从商品基础表单位和规格稳定换算时，按标准体积口径换算；无法换算则标记 UNIT_CONVERSION_ERROR

实际收货标准量 <= 0
-> 不进入售罄率分母
```

异常：

```text
19:30 前销售量 / 实际收货量 > 1.10
-> 该门店 SKU 日不进入自然动销分子、分母
-> 仍有其他有效自然动销日时，只用剩余有效日重算，并在 data_quality_flags 写 DATA_INSUFFICIENT
-> 没有其他有效自然动销日时，对应 SKU / 标准商品自然动销指标写 NULL，natural_sales_status = DATA_INSUFFICIENT，result_status = DATA_INCOMPLETE
```

禁止把异常售罄率截断成 100% 后继续参与自然动销评分。

### 14.3 门店群售罄率

```text
pre1930_sell_through_rate
= SUM(有效 SKU 日 19:30 前标准销售量)
  / SUM(有效 SKU 日实际收货标准量)

non_promo_pre1930_sell_through_rate
= SUM(非促销有效 SKU 日 19:30 前标准销售量)
  / SUM(非促销有效 SKU 日实际收货标准量)
```

### 14.4 销售深度

```text
pre1930_sales_volume_per_available_store_day
= 19:30 前销售标准量 / available_store_day_cnt
```

### 14.5 目标画像吸收贡献

```text
target_profile_pre1930_absorption_rate
= 目标画像 19:30 前销售标准量
  / 该 SKU 实际收货标准量
```

该字段回答“目标画像在实际收货量中吸收了多少”，分母必须是同一范围、同一周期、同一 SKU 的实际收货标准量；不得使用门店群该 SKU 的销售量替代。门店群总销售标准量如需展示，单独保存为 `sku_total_pre1930_sales_standard_qty`，不能改变吸收率公式。

### 14.6 没有自然销售窗口

如果没有非促销自然销售窗口：

```text
natural_sales_status = NO_NATURAL_SALES_WINDOW
is_formal_anchor = 0
```

保留明细和解释，不删除原始表现。

---

## 15. 19:30 后折扣阶梯

本批从算法 02 正式结果 `mart_store_category_level.promotion_discount_scope` 读取并校验当前门店群所有行一致，V1 只接受 `TOTAL_DISCOUNT_INCL_TIME`。`mart_sku_margin_loss.discount_amt` 是门店 SKU 日总折扣，已包含时段折扣；Doris `discount_amt` 是商品行优惠额，`hour_discount_amt` 是会员同小时累计额。三者不能直接相加，也不能把 `hour_discount_amt` 当商品行时段折扣求和。口径缺失、不唯一或与 V1 固定值不一致时，本批不发布，问题写平台质量记录。

折扣阶梯只用于解释，不进入综合得分。

按实际时间和折扣档输出：

```text
19:30-20:00 销售量 / 增量售罄率 / 实际折扣率
20:00-20:30 销售量 / 增量售罄率 / 实际折扣率
20:30-21:00 销售量 / 增量售罄率 / 实际折扣率
```

公式：

```text
band_incremental_sell_through_rate
= 该折扣档销售标准量 / 当日实际收货标准量

cumulative_sell_through_rate_at_band_end
= 截至该折扣档结束累计销售标准量 / 当日实际收货标准量
```

建议存为：

```text
discount_ladder_json
```

---

## 16. 商品毛利

### 16.1 业务公式

```text
target_profile_sku_margin_amt
= target_profile_sku_sales_amt - target_profile_sku_cost_amt

target_profile_sku_margin_rate
= target_profile_sku_margin_amt / target_profile_sku_sales_amt

sku_total_cost_amt
= SUM(全部消费者购买该 SKU 的成本金额)

sku_total_margin_amt
= sku_total_sales_amt - sku_total_cost_amt

sku_total_margin_rate
= sku_total_margin_amt / sku_total_sales_amt
```

### 16.2 不重复扣损耗

```text
算法 04 不再减损耗
不输出损耗诊断
不将损耗分摊给消费者画像
```

### 16.3 V1 成本落地口径

业务原文给出毛利公式：

```text
目标画像 SKU 毛利额 = 目标画像 SKU 销售额 - 目标画像 SKU 成本金额
```

目标画像 SKU 成本金额不能优先按销售额占比分摊。商品单位成本在同一日门店 SKU 口径下应保持一致，因此 V1 优先按“目标画像标准销售量 × 日门店 SKU 单位成本”计算。

这是对业务公式的落地实现，不是新增一套毛利算法。业务公式定义了“毛利额 = 销售额 - 成本金额”，V1 的关键是用日门店 SKU 单位成本来计算目标画像成本金额。

V1 建议优先口径：

```text
daily_store_sku_cost_amt
= daily_store_sku_sales_amt - daily_store_sku_full_chain_margin_amt

daily_store_sku_unit_cost
= daily_store_sku_cost_amt / daily_store_sku_total_sales_standard_qty

target_profile_daily_store_sku_cost_amt
= target_profile_daily_store_sku_sales_standard_qty
 * daily_store_sku_unit_cost
```

然后汇总到算法 04 粒度：

```text
target_profile_sku_cost_amt
= SUM(target_profile_daily_store_sku_cost_amt)
```

输出标记：

```text
cost_source = FULL_CHAIN_MARGIN_DERIVED_COST
cost_allocation_method = UNIT_COST_BY_STANDARD_QTY
cost_allocation_status = COST_ALLOCATED_V1
```

由于算法 04 统一使用 `sales_standard_qty = weight`，V1 默认不启用销售额占比分摊成本。

V1 固定 `cost_fallback_policy = DISABLED`。当个别 SKU 或日期无法取得可信标准销售量时，不允许按销售额占比分摊成本进入正式结果；以下公式只可用于运行级敏感性诊断：

```text
target_profile_daily_store_sku_cost_amt
= daily_store_sku_cost_amt
 * target_profile_daily_store_sku_sales_amt
 / daily_store_sku_sales_amt

诊断结果只保留在本次运行过程数据中，不写正式毛利字段。
```

相关 SKU 按失败原因唯一输出：

```text
result_status = DATA_INCOMPLETE
cost_allocation_method = NOT_ALLOCATED

两个成本来源都没有有效值
-> cost_source = SOURCE_MISSING
-> cost_allocation_status = SOURCE_MISSING
-> profitability_status = COST_SOURCE_MISSING

含税到店成本存在多收货 SKU 不同成本值等业务冲突
-> cost_source = SOURCE_CONFLICT
-> cost_allocation_status = SOURCE_CONFLICT
-> profitability_status = COST_SOURCE_CONFLICT

成本来源有效，但日门店 SKU 总销售标准量为 0
-> cost_allocation_status = ZERO_DENOMINATOR
-> profitability_status = COST_NOT_CALCULABLE

成本来源有效且分母非 0，但计量映射或目标画像标准销售量无法可靠换算
-> cost_allocation_status = COST_NOT_ALLOCATED
-> profitability_status = COST_NOT_CALCULABLE
```

对应 `target_profile_sku_cost_amt`、毛利额、毛利率与毛利维度得分写 `NULL`，保留可验证的销售和会员诊断字段，并写 `data_quality_flags`；不得将缺失成本写成 0。未来若变更成本降级政策，必须另行修订字段合同和验收样例，并从下一完整月批次生效。

含税到店成本备选：

```text
cost_source = ARRIVAL_COST_TAX_INCLUDED
```

使用门店商品日价格表 `出库到店成本含税` 时，必须先按数据合同完整主键 `business_date + store_id + sku_id + receipt_sku_id` 验收唯一性。折叠到“日期 + 门店 + 销售 SKU”前必须满足：只有一个验收商品，或同一销售 SKU 对应的全部有效验收商品单位成本完全一致。完整物理主键重复属于输入质量失败，阻断整批发布；主键唯一但同一销售 SKU 对应多个不同单位成本属于业务冲突，不选择任意一行、不按平均值拼成本，按上表写 `SOURCE_CONFLICT` 和 `PRICE_SOURCE_CONFLICT`。没有有效备选成本时写 `SOURCE_MISSING` 和 `PRICE_SOURCE_MISSING`。

### 16.4 正式锚点毛利底线

```text
target_profile_sku_margin_amt > 0
并且
sku_total_margin_amt > 0
```

两项都大于 0 时：

```text
profitability_status = POSITIVE_MARGIN
```

任一不为正：

```text
profitability_status = NON_POSITIVE_MARGIN
is_formal_anchor = 0
```

毛利率较低但毛利额为正时不直接删除，由毛利维度得分反映。

---

## 17. 商品属性与商品编码

### 17.1 属性字段

V1 锚点 SKU 只输出 `dim_sku` 数据合同已有的属性：

```text
specification：原始规格文本，不等同于净含量
sale_unit：销售单位
unit_weight_kg：单位重量，用于可验证的计量换算
temperature_layer：温层
brand_name：品牌
```

业务原文要求的主材料、部位或形态、配料、口味、加工及烹饪方式、净含量、包装方式，当前商品基础表合同均未提供相应字段；BOM/规格书、审核属性字典和抽取规则也没有冻结为 V1 数据合同。V1 不把这些属性列为必备输入或正式输出，不从名称或规格猜测。它们需要后续规则资产和字段合同落地，才可为算法 06 及新品方向提供可靠属性；缺失不阻断算法 04 的经营表现计算。

### 17.2 来源与缺失写法

V1 仅按本批锁定的 `dim_sku` 快照读取上述字段。`attribute_source_json` 只允许以 `specification`、`sale_unit`、`unit_weight_kg`、`temperature_layer`、`brand_name` 为键；字段有值写 `MASTER_DATA`，无值写 `UNKNOWN`。`attribute_confidence_json` 使用相同的键，值均写 JSON `null`，表示当前没有经过验收的属性识别置信度，不能把“有主数据值”直接当成识别准确率。两列不得引入未冻结的字典、名称规则或 AI 推断值。

`sale_unit` 是商品基础表必填字段；其他属性允许 SQL `NULL`。当 `specification`、`unit_weight_kg`、`temperature_layer`、`brand_name` 任一缺失时，`attribute_status=ATTRIBUTE_INCOMPLETE`；均有值时写 `COMPLETE`。这个状态只描述 V1 可用字段的完整度，不代表业务原文要求的主材料、口味和形态已经可供新品组合使用。单位重量缺失而指标必须换算时，另按第 11 章计量规则降级。

### 17.3 商品编码核对

```text
同一商品编码在同一有效日期只能命中一条正式商品记录
商品编码命中后仍需校验商品名称和品类一致性
一对多或品类冲突禁止重复关联小票金额
```

### 17.4 SKU 与标准商品双层

```text
SKU 层：保留原始销售商品表现、得分、分组和锚点状态。
标准商品层：按商品基础表已稳定提供的 spu_id 聚合同一标准商品，并独立重算全部指标、得分、分组和锚点状态。
```

V1 只使用 `dim_sku.spu_id`，不新增独立换码或替代关系。映射规则是“每个 `sku_id` 必须唯一映射到零个或一个 `spu_id`”；多个 SKU 共享同一个 SPU 是正常聚合场景，不能把 SPU 重复出现误判为冲突。

```text
sku_id 唯一映射到有效 spu_id -> standard_product_key = spu_id，standard_product_mode = SPU_MAPPED
spu_id 缺失                   -> standard_product_key = sku_id，standard_product_mode = SKU_ONLY
同一 sku_id 映射多个 spu_id   -> 输入映射冲突，阻断本批发布
```

标准商品层不能由 SKU 汇总表的去重人数、小票数或得分简单相加得到。必须从本次运行级交易、门店日、成本和状态过程数据重新聚合：

1. 在“标准商品 + 会员 + 小票”键上重新去重小票和会员。
2. 重新计算销售占比、会员/小票渗透、7 天复购及 Jeffreys 区间。
3. 重新聚合有效门店日、自然动销、实际收货量、目标画像吸收率和毛利。
4. 重新运行稳健标准化、CRITIC、Jenks/BIC、正式锚点准入及留一门店/留一月验证。
5. 成员 SKU 计量类型或标准单位不一致且无法可靠换算时，金额、人数等可计算字段保留；数量、自然动销和依赖数量的得分写 NULL，`result_status = DATA_INCOMPLETE`，不得成为正式锚点。

SKU 表和标准商品表分别保存本层结论。SKU 行不得用标准商品层的 `performance_group`、`is_formal_anchor` 或锚点状态覆盖自身字段；下游通过 `standard_product_key` 关联标准商品层。锚点汇总按 canonical 规则选择：`SPU_MAPPED` 读取标准商品表，`SKU_ONLY` 读取 SKU 表，避免重复计数。

## 18. 价格指标、商品状态与算法 05 边界

算法 04 只输出现有 SKU 价格描述：

```text
original_price
target_profile_avg_paid_price
reference_profile_avg_paid_price
standardized_paid_price
before_after_promotion_price
actual_discount_rate
```

价格不进入算法 04 综合得分；目标画像可接受价格和候选新品价格带由算法 05 单独计算。

价格规则：

```text
target_profile_avg_paid_price = 目标画像实付金额 / 目标画像销售标准量
reference_profile_avg_paid_price = 参考画像实付金额 / 参考画像销售标准量
standardized_paid_price = 按 sale_unit、unit_weight_kg 和 standard_unit 换算后的标准化实付价
actual_discount_rate = 1 - after_price / before_price
```

`original_price` 从 `listing_snapshot_date` 的门店商品日价格表读取。该表完整主键包含 `receipt_sku_id`，因此必须先按完整主键验收，再在当前有效门店范围内检查同一销售 SKU 的 `original_sale_price`：

- 所有有效非空原价一致时输出该唯一值。
- 没有有效原价时写 NULL + `PRICE_SOURCE_MISSING`。
- 存在两个或以上不同原价时不选择任意门店、不求简单平均，写 NULL + `PRICE_SOURCE_CONFLICT`。

`before_after_promotion_price` 只在原价唯一且促销交易成交价可复算时输出对象：`before_price` 为唯一原价，`after_price` 为当前比较组促销代理交易的 `SUM(usual_amt) / SUM(weight)`，`price_source` 固定为 `PRICE_TABLE_ORIGINAL_DORIS_USUAL_AMT_PER_WEIGHT`。任一分母无效、来源缺失或原价冲突时整个对象写 JSON `null`；`actual_discount_rate` 同时写 NULL。

商品状态只作解释，不参与评分。平台为本批锁定一个 `dim_product_status.product_status_version` 和状态快照；先把 `region_code` 映射到本批 `scope_id`，再按“锁定版本 + 区域 + SKU”检查唯一：

- 唯一命中且 `status_snapshot_date <= listing_snapshot_date`：输出状态码和 `AVAILABLE`。
- CITY_CLUSTER 内多区域状态一致：输出该一致状态。
- 缺失、区域无法映射、版本/主键冲突、快照晚于在售快照或城市群成员状态不一致：`product_status_code = NULL`、`product_status_availability = NOT_AVAILABLE`。

不得根据销量季节性、商品名称或成员城市多数票编造商品状态。

## 19. 四个一级评分维度

### 19.1 目标画像贡献

```text
sku_sales_share
sku_buyer_penetration_lower_95
sales_per_available_store_day
```

### 19.2 目标画像偏好

```text
preference_lower_95
repurchase_rate_7d_pre19_lower_95
```

### 19.3 19:30 前自然动销

```text
non_promo_pre1930_sell_through_rate
pre1930_sales_volume_per_available_store_day
```

数量指标只在相同计量类型内标准化。

### 19.4 商品毛利

```text
target_profile_sku_margin_amt
target_profile_sku_margin_rate
sku_total_margin_amt
sku_total_margin_rate
```

### 19.5 不进入综合得分

```text
门店订购率和订购门店日率
19:30 后折扣阶梯
价格和价格带
损耗
商品属性完整度
当前在售状态
```

这些字段用于覆盖、解释、状态和后续算法，不与表现得分混合。

---

## 20. 稳健标准化

比较组：

```text
周期 + 城市或城市群 + 品类颗粒度 + 品类
+ 门店群范围 + final_profile
```

### 20.1 指标转换

```text
金额、每店日销售额、销售量深度：ln(1 + x)
偏好指数下界：ln(x)
比例和毛利率：保留原值
```

### 20.2 稳健 Z 分数

```text
z_j
= (x'_ij - median_j)
  / (1.4826 * MAD_j)

indicator_score_ij
= 100 * Phi(z_j)
```

其中 `Phi` 为标准正态累计分布函数。

### 20.3 MAD 回退

```text
MAD > 0：使用 MAD
MAD = 0 且 IQR > 0：使用 IQR / 1.349
MAD = 0、IQR = 0、标准差 > 0：使用标准差
全部 SKU 取值完全相同：移除该指标
```

禁止使用普通 Min-Max。

---

## 21. 两级 CRITIC 动态赋权

### 21.1 两级结构

```text
先在每个一级维度内计算二级指标权重
再对四个一级维度计算权重
```

避免某个维度因为指标数量多而天然权重更高。

### 21.2 CRITIC 公式

对标准化后的指标：

```text
C_j
= sigma_j * SUM_k(1 - corr_jk)

w_j
= C_j / SUM(C_j)
```

维度分：

```text
dimension_score_d
= SUM(维度内 indicator_score_j * w_j)
```

综合分：

```text
sku_performance_score
= SUM(dimension_score_d * dimension_weight_d)
```

CRITIC 自动降低与其他指标高度重复的指标权重，不使用固定销售 30%、复购 20% 等经验权重。

### 21.3 不适用和缺失

整个比较组不适用的指标从 CRITIC 中移除并对全组重算。

例如上游结果为 `SINGLE_PROFILE` 时，当前比较组没有偏好参考组，写 `preference_reference_status = NO_REFERENCE_PROFILE`。

单个 SKU 的商品毛利、实际到货、商品编码等必需数据缺失时：

```text
result_status = DATA_INCOMPLETE
不填 0
不以同品类平均值替代
不生成正式综合得分
```

商品属性缺失不影响经营表现得分，但输出：

```text
attribute_status = ATTRIBUTE_INCOMPLETE
```

不能自动组合新品。

### 21.4 CRITIC 小样本回退

```text
有效 SKU 数 >= 3
-> 正常运行 CRITIC

有效 SKU 数 = 2
-> 不运行 CRITIC
-> 使用四维 Pareto 比较
-> 只有一个 SKU 在所有可用维度均不低于另一个，且至少一维更高，才是相对锚点候选

有效 SKU 数 = 1
-> result_status = SINGLE_SKU
-> 不生成综合得分和正式高表现组
```

所有可用指标没有差异时输出：

```text
NO_OBVIOUS_HIGH_SKU
```

不使用人工等权强制排名。

本节在两个评分层分别执行：SKU 层的样本数是有效销售 SKU 数；标准商品层的样本数是有效 `standard_product_key` 数。两个层各自产生动态参数、分组和行级 `result_status`，不能用 canonical 汇总层的实体数替代任一评分层样本数。

---

## 22. Jenks+BIC 动态锚点组

### 22.1 候选组数

SKU 层对同一比较组的 `sku_performance_score` 从低到高排序；标准商品层按相同方法对 `product_performance_score` 排序。两个评分层分别运行 Jenks+BIC：

```text
K_max = MIN(3, 综合得分去重值数量)
候选 K = 1 ... K_max
```

相同得分不得被拆到不同组。

### 22.2 Jenks

```text
SSE_K = SUM((score_i - 当前组均值)^2)
```

选择每个 K 下组内平方误差最小的连续切分。

### 22.3 BIC

```text
BIC(K) = N * ln(SSE_K / N + 1e-12) + K * ln(N)
```

BIC 越小越好；相同时选择更小 K。

### 22.4 分组结果

```text
K=3：高表现组 / 中表现组 / 低表现组
K=2：高表现组 / 低表现组
K=1：NO_OBVIOUS_HIGH_SKU，不强制产生正式高表现组
```

最高表现组进入正式锚点准入判断。

综合得分只允许在同一比较组内排序。

---

## 23. 正式锚点准入

### 23.1 必须同时满足

```text
1. 上游版本、商品编码、销售、到货和商品毛利数据完整
2. orderable_sellable_flag = 1
3. target_profile_sku_margin_amt > 0
4. sku_total_margin_amt > 0
5. 置信度校正后的综合得分进入 Jenks 最高表现组
6. evidence_status != LOW_EVIDENCE
7. natural_sales_status = VALID
```

全部满足：

```text
is_formal_anchor = 1
anchor_evidence_type = ACTIVE_STABLE_ANCHOR 或对应解释类型
```

### 23.2 不直接阻断

```text
门店订购率低
-> 低铺货高表现机会

依赖某个月
-> 时间敏感锚点，购物篮分月验证

依赖少数门店
-> 门店集中锚点，购物篮分店验证
```

### 23.3 非正式当前锚点

```text
不可订或不可售
只有 1 个 SKU 或 2 个 SKU 的相对候选
没有非促销自然销售窗口
消费者证据不足
目标画像或 SKU 整体商品毛利不为正
```

这些结果保留明细和解释，但：

```text
is_formal_anchor = 0
```

---

## 24. 当前锚点与历史锚点

```text
anchor_lifecycle_status = ACTIVE_ANCHOR
= 当前可订可售且通过正式锚点准入

anchor_lifecycle_status = HISTORICAL_ANCHOR
= 贡献周期内有真实销售且表现较好，且当前 listing_status = INACTIVE（已确认不可订或不可售）

`listing_status = NULL` 只表示当前状态未知，不能降级成 `HISTORICAL_ANCHOR`；该 SKU 写 `NOT_ANCHOR`/`DATA_INCOMPLETE` 并保留 `data_quality_flags`。
```

历史锚点进入新品或复开发前必须检查：

```text
停售原因
历史订购表现
相似商品表现
```

算法 04 不删除当前在售商品。

后续候选过滤删除的是与当前货盘重复的“新品候选”，不是现有锚点。

---

## 25. 门店稳定性

### 25.1 集中度

```text
top1_store_sales_share
= 该 SKU 销售额最高门店销售额 / 门店群该 SKU 销售额

store_sales_hhi
= SUM(各门店该 SKU 销售额占比^2)
```

### 25.2 留一门店

对每家覆盖该 SKU 的门店：

```text
删除该门店
-> 重新计算全部 SKU 指标
-> 重新计算 CRITIC 权重、综合得分和 Jenks 分组
```

```text
leave_one_store_anchor_rate
= 删除不同门店后仍进入锚点组的有效次数 / 有效验证次数
```

状态：

```text
全部有效验证均保持锚点 -> STABLE
任一次发生变化 -> STORE_CONCENTRATED
覆盖门店不足 -> INSUFFICIENT_STORE_SAMPLE
```

`STORE_CONCENTRATED` 不直接删除正式锚点。

---

## 26. 时间稳定性

保持正式消费者画像版本和门店群不变：

```text
验证 1：删除第 1 月，使用第 2 月 + 第 3 月重算
验证 2：删除第 2 月，使用第 1 月 + 第 3 月重算
验证 3：删除第 3 月，使用第 1 月 + 第 2 月重算
```

```text
leave_one_month_anchor_rate
= 仍进入锚点组的有效次数 / 有效验证次数
```

状态：

```text
全部有效验证均保持锚点 -> STABLE
任一次删除月份后不再是锚点 -> TIME_SENSITIVE
有效验证少于 2 次 -> INSUFFICIENT_TIME_SAMPLE
```

`pull_months_json` 记录每个有效留一月验证中“删除该月后不再进入锚点组”的月份，按 `YYYY-MM` 升序输出去重字符串数组；全部有效验证仍保持锚点写 `[]`，有效验证少于 2 次写 SQL `NULL`，不能把“无法判断”写成空数组。算法 06 只读取该字段及完整 3 个月锚点身份，自己计算分月购物篮关联。

完整 3 个月仍为正式结果。

时间敏感不直接删除锚点。

---

## 27. 时间敏感锚点的购物篮路径与算法 06 接口

稳定锚点：

```text
使用完整 3 个月小票进行购物篮分析
关联结果可作为常规商品开发证据
```

业务原文要求时间敏感锚点同时验证三组购物篮关联：

```text
完整 3 个月关联规则
拉动月份内关联规则
删除拉动月份后的关联规则
```

```text
删除拉动月后关联仍存在
-> 组合关系较稳定，可保留常规商品开发价值

关联只在拉动月成立
-> 季节性、节日性或促销场景机会，不作为全年常规推荐
```

门店集中锚点同理增加分店验证。V1 已确认购物篮关联规则由算法 06 负责计算；算法 04 只交付锚点身份、拉动月份和稳定性证据，供算法 06 按同一 `algorithm_batch_version` 读取。算法 04 没有购物篮规则结果表，不得声称已交付上述三组关联结论。

---

## 28. 结果状态设计

算法 04 不使用一个大而全的组合标签。计算结果、锚点资格、在售状态、盈利状态、证据状态、门店稳定性、时间稳定性、自然动销状态、订购覆盖状态和属性完整度必须拆成独立字段保存。

上游表缺失、批次或周期不一致、主键重复、商品一对多映射、画像销售额对账失败属于批次质量失败：整批不发布，由平台记录原因，不写成正式 `result_status`。

合法业务单元按以下顺序确定 `result_status`，先命中者优先：

```text
1. 已有合法 final_profile，但过滤后没有合法 SKU：锚点汇总写 NO_VALID_SKU，不写 SKU 或标准商品明细。
2. 有合法实体，但核心业务字段部分缺失且仍能保留诊断：实体行写 DATA_INCOMPLETE，不得成为正式锚点。
3. 所有核心业务分母均不可用：写 NOT_CALCULABLE，不伪造 0。
4. 当前结果层只有 1 个可计算实体：写 SINGLE_SKU；SKU 表按有效 SKU 数判断，标准商品表按有效 standard_product_key 数判断，汇总表按 canonical 实体数判断。
5. 当前结果层有多个可计算实体但 Jenks/BIC 未形成高表现组：写 NO_OBVIOUS_HIGH_SKU。
6. 其余正常完成：写 SUCCESS。
```

算法 03 汇总为 `NOT_CALCULABLE` 的门店群没有合法 `final_profile`，属于正常排除项，算法 04 不写任何正式行。正式输出字段和状态取值约束见第 29 章；缺失、不适用和异常不能写成 0。

---

## 29. 输出表

算法 04 正式交付三张结果表和一张动态参数表。复购、应处理对象、暂存结果和质量检查均为运行级过程数据，不新增独立发布表或专用审计表。

| 表名 | 表类型 | 一行代表什么 | 下游用途 |
|---|---|---|---|
| `mart_sku_repurchase_7d_pre19` | 运行级过程数据集 | 一个周期 + 一个范围 + 一个门店群 + 一个消费者画像 + 一个 SKU 的 7 天 19 点前复购结果 | 仅由本次算法 04 运行读取；保留逻辑名称，不要求持久化正式表 |
| `mart_target_profile_sku_performance` | 正式结果表 | 一个周期 + 一个范围 + 一个门店群 + 一个消费者画像 + 一个销售 SKU | 算法 04 SKU 层主表，给后续算法读取 |
| `mart_target_profile_product_performance` | 正式结果表 | 一个周期 + 一个范围 + 一个门店群 + 一个消费者画像 + 一个标准商品 | 标准商品层独立重算结果 |
| `mart_target_profile_anchor_summary` | 正式结果表 | 一个周期 + 一个范围 + 一个门店群 + 一个消费者画像的 canonical 锚点汇总 | 给业务验收和下游选择默认锚点 |
| `mart_target_profile_sku_performance_params` | 正式动态参数表 | 一个统一算法批次 + 一个参数作用范围 + 一个评分层 + 一个动态参数 | 复现稳健标准化、CRITIC 和 Jenks/BIC |

四张正式表必须按 `algorithm_batch_version` 整体可见或整体不可见。平台任务状态是下游启动依据，`run_id` 用于实际运行追溯。

### 29.1 运行级过程数据集：`mart_sku_repurchase_7d_pre19`

一行代表：一个周期、一个范围、一个门店群、一个消费者画像和一个 SKU 的 7 天 19 点前复购结果。该对象使用 CTE、临时表、临时分区或平台已有过程数据集实现，不作为下游接口。

主键：

```text
algorithm_batch_version
+ performance_start_date
+ performance_end_date
+ scope_type
+ scope_id
+ category_granularity
+ category_code
+ store_group_type
+ final_level
+ final_profile
+ sku_id
```

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 统一算法批次版本 | `algorithm_batch_version` | varchar(32) | 必须 | `调度运行清单` | 固定为 `BATCH_YYYYMM`；与算法 01～03 同批，并进入本表唯一键 |
| 运行ID | `run_id` | varchar(64) | 必须 | 调度系统 | 本次结果所属算法 04 实际运行；同批原子发布的三张结果表和一张参数表使用同一 `run_id` |
| 重跑原因 | `rerun_reason` | varchar(512) | 条件必须 | 调度运行清单 | 同批次修正重跑时必填；首次运行可为 NULL |
| 更新时间 | `updated_at` | datetime | 必须 | 系统生成 | 本批本处理单元最近一次成功写入时间 |
| 数据周期开始日期 | `performance_start_date` | date | 必须 | 调度参数 | 统计周期开始日期 |
| 数据周期结束日期 | `performance_end_date` | date | 必须 | 调度参数 | 统计周期结束日期 |
| 范围类型 | `scope_type` | varchar(32) | 必须 | `dim_algorithm_batch_city_region_snapshot` | `CITY` / `CITY_CLUSTER` |
| 范围编码 | `scope_id` | varchar(64) | 必须 | `dim_algorithm_batch_city_region_snapshot.algorithm_region_code` | 城市或城市群编码 |
| 范围名称 | `scope_name` | varchar(128) | 必须 | `dim_algorithm_batch_city_region_snapshot.algorithm_region_name` | 城市或城市群名称 |
| 品类颗粒度 | `category_granularity` | varchar(32) | 必须 | `dim_sku` + 本算法品类颗粒度映射 | 大类 / 中类 / 小类 |
| 品类编码 | `category_code` | varchar(64) | 必须 | `dim_sku.category_level1_code/category_level2_code/category_level3_code` + 本算法品类颗粒度映射 | 当前计算品类编码 |
| 品类名称 | `category_name` | varchar(128) | 必须 | `dim_sku.category_level1_name/category_level2_name/category_level3_name` + 本算法品类颗粒度映射 | 当前计算品类名称 |
| 门店群类型 | `store_group_type` | varchar(32) | 必须 | `mart_store_category_level.final_level` + 本算法第 3.1 节范围分组 | `FINAL_LEVEL` / `ALL_RATED` |
| 门店品类等级 | `final_level` | varchar(32) | 必须 | `mart_store_category_level.final_level` | A/B/C/D 或 ALL_RATED |
| 消费者画像 | `final_profile` | varchar(128) | 必须 | `dim_customer_profile.final_profile` | 算法 01 最终画像 |
| 门店品类等级开始日期 | `category_level_start_date` | date | 必须 | `mart_store_category_level.calculation_start_date` | 算法 02 结果周期开始日期 |
| 门店品类等级结束日期 | `category_level_end_date` | date | 必须 | `mart_store_category_level.calculation_end_date` | 算法 02 结果周期结束日期 |
| 消费者贡献开始日期 | `consumer_contribution_start_date` | date | 必须 | `mart_store_group_consumer_contribution.contribution_start_date`（本卡别名） | 算法 03 结果周期开始日期 |
| 消费者贡献结束日期 | `consumer_contribution_end_date` | date | 必须 | `mart_store_group_consumer_contribution.contribution_end_date`（本卡别名） | 算法 03 结果周期结束日期 |
| SKU 编码 | `sku_id` | varchar(64) | 必须 | `data_agent.dws_member_order_item_detail_df_all_new.article_id` / `dim_sku.sku_id` | 销售 SKU |
| 7 天复购会员数 | `repeat_buyer_cnt_7d_pre19` | bigint | 必须 | Doris 小票计算 | 首次购买后第 1-7 个自然日且 19:00 前再次购买该 SKU 的会员数 |
| 7 天可观察首购会员数 | `eligible_first_buyer_cnt_7d` | bigint | 必须 | Doris 小票计算 | 首次购买后具备完整 7 天观察窗口的会员数 |
| 观察不足首购会员数 | `insufficient_observation_first_buyer_cnt` | bigint | 必须 | Doris 小票计算 | 首购发生在表现周期最后 6 个自然日、无法获得完整 7 天观察窗口的去重会员数；无此类会员写 0 |
| 观察不足但已观察到复购会员数 | `insufficient_observation_observed_repeat_buyer_cnt_pre19` | bigint | 必须 | Doris 小票计算 | 上述观察不足会员中，在周期结束前已发生第 1-7 个自然日且 19:00 前再次购买的去重会员数；仅作诊断，不进入正式复购率分子；无此类会员写 0 |
| 7 天 19 点前复购率 | `repurchase_rate_7d_pre19` | decimal(18,8) | 条件必须 | 本表计算 | `repeat_buyer_cnt_7d_pre19 / eligible_first_buyer_cnt_7d` |
| 计算状态 | `repurchase_calc_status` | varchar(64) | 必须 | 本表计算 | 见第 29.6 节状态约束 |
| 计算时间 | `calculated_at` | datetime | 必须 | 系统生成 | 结果写入时间 |

### 29.2 SKU 表现明细：`mart_target_profile_sku_performance`

一行代表：一个周期、一个范围、一个门店群、一个消费者画像和一个销售 SKU 的表现结果。

主键：

```text
algorithm_batch_version
+ performance_start_date
+ performance_end_date
+ scope_type
+ scope_id
+ category_granularity
+ category_code
+ store_group_type
+ final_level
+ final_profile
+ sku_id
```

范围、版本与分组字段：

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 统一算法批次版本 | `algorithm_batch_version` | varchar(32) | 必须 | `调度运行清单` | 固定为 `BATCH_YYYYMM`；与算法 01～03 同批，并进入本表唯一键 |
| 运行ID | `run_id` | varchar(64) | 必须 | 调度系统 | 本次结果所属算法 04 实际运行；同批原子发布的三张结果表和一张参数表使用同一 `run_id` |
| 重跑原因 | `rerun_reason` | varchar(512) | 条件必须 | 调度运行清单 | 同批次修正重跑时必填；首次运行可为 NULL |
| 更新时间 | `updated_at` | datetime | 必须 | 系统生成 | 本批本处理单元最近一次成功写入时间 |
| 数据周期开始日期 | `performance_start_date` | date | 必须 | 调度参数 | 最近 3 个完整自然月开始日期 |
| 数据周期结束日期 | `performance_end_date` | date | 必须 | 调度参数 | 最近 3 个完整自然月结束日期 |
| 范围类型 | `scope_type` | varchar(32) | 必须 | `dim_algorithm_batch_city_region_snapshot` | `CITY` / `CITY_CLUSTER` |
| 范围编码 | `scope_id` | varchar(64) | 必须 | `dim_algorithm_batch_city_region_snapshot.algorithm_region_code` | 城市或城市群编码 |
| 范围名称 | `scope_name` | varchar(128) | 必须 | `dim_algorithm_batch_city_region_snapshot.algorithm_region_name` | 城市或城市群名称 |
| 品类颗粒度 | `category_granularity` | varchar(32) | 必须 | `dim_sku` + 本算法品类颗粒度映射 | 大类 / 中类 / 小类 |
| 大类编码 | `category_level1_code` | varchar(64) | 必须 | `dim_sku.category_level1_code` | 商品大类编码；按数据合同不能为空 |
| 大类名称 | `category_level1_name` | varchar(128) | 必须 | `dim_sku.category_level1_name` | 商品大类名称；按数据合同不能为空 |
| 中类编码 | `category_level2_code` | varchar(64) | 必须 | `dim_sku.category_level2_code` | 商品中类编码；按数据合同不能为空 |
| 中类名称 | `category_level2_name` | varchar(128) | 必须 | `dim_sku.category_level2_name` | 商品中类名称；按数据合同不能为空 |
| 小类编码 | `category_level3_code` | varchar(64) | 必须 | `dim_sku.category_level3_code` | 商品小类编码 |
| 小类名称 | `category_level3_name` | varchar(128) | 必须 | `dim_sku.category_level3_name` | 商品小类名称 |
| 品类编码 | `category_code` | varchar(64) | 必须 | `dim_sku.category_level1_code/category_level2_code/category_level3_code` + 本算法品类颗粒度映射 | 与 `category_granularity` 对应的当前计算品类编码 |
| 品类名称 | `category_name` | varchar(128) | 必须 | `dim_sku.category_level1_name/category_level2_name/category_level3_name` + 本算法品类颗粒度映射 | 与 `category_granularity` 对应的当前计算品类名称 |
| 门店群类型 | `store_group_type` | varchar(32) | 必须 | `mart_store_category_level.final_level` + 本算法第 3.1 节范围分组 | `FINAL_LEVEL` / `ALL_RATED` |
| 门店品类等级 | `final_level` | varchar(32) | 必须 | `mart_store_category_level.final_level` | 当前门店群等级 |
| 门店数 | `store_cnt` | bigint | 必须 | `mart_store_group_consumer_summary.store_cnt` + 本算法第 10.1.1 节历史门店群对账 | 本次三个月表现计算使用的门店群门店数；必须与算法 03 汇总一致，不改写为当前营业门店数 |
| 消费者画像 | `final_profile` | varchar(128) | 必须 | `dim_customer_profile.final_profile` | 目标消费者画像 |
| 是否主力画像 | `is_main_profile` | tinyint | 必须 | `mart_store_group_consumer_contribution.is_main_profile` | `1` 是正式主力画像，`0` 不是 |
| 是否相对主力候选 | `is_relative_main_candidate` | tinyint | 必须 | `mart_store_group_consumer_contribution.is_relative_main_candidate` | `1` 是相对主力候选，`0` 不是 |
| 在售快照日期 | `listing_snapshot_date` | date | 必须 | `mart_store_sku_daily_sale_order_status.business_date` | 当前可订可售快照日期 |
| 在售范围聚合方法 | `listing_scope_aggregation_method` | varchar(64) | 必须 | 调度参数 + 本算法第 10.1.1 节有效门店集合 | V1 固定 `ANY_ACTIVE_STORE`；用于追溯门店群聚合规则 |
| 门店品类等级开始日期 | `category_level_start_date` | date | 必须 | `mart_store_category_level.calculation_start_date` | 算法 02 结果周期开始日期 |
| 门店品类等级结束日期 | `category_level_end_date` | date | 必须 | `mart_store_category_level.calculation_end_date` | 算法 02 结果周期结束日期 |
| 消费者贡献开始日期 | `consumer_contribution_start_date` | date | 必须 | `mart_store_group_consumer_contribution.contribution_start_date`（本卡别名） | 算法 03 结果周期开始日期 |
| 消费者贡献结束日期 | `consumer_contribution_end_date` | date | 必须 | `mart_store_group_consumer_contribution.contribution_end_date`（本卡别名） | 算法 03 结果周期结束日期 |
| 有效交易过滤方式 | `valid_transaction_filter_method` | varchar(64) | 必须 | 本算法第 6.1 节交易过滤 | 见第 29.6 节状态约束 |

商品、在售和计量字段：

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| SKU 编码 | `sku_id` | varchar(64) | 必须 | `data_agent.dws_member_order_item_detail_df_all_new.article_id` / `dim_sku.sku_id` | 销售 SKU |
| 商品编码 | `product_id` | varchar(64) | 建议 | `dim_sku.product_id` | 商品主数据编码；可为空，缺失时标准商品主键回退 `sku_id` |
| SKU 名称 | `sku_name` | varchar(256) | 必须 | `dim_sku.sku_name` | 商品展示名称 |
| 规格原文 | `specification` | varchar(128) | 建议 | `dim_sku.specification` | 原始规格说明；没有规则资产时不推断净含量 |
| SPU 编码 | `spu_id` | varchar(64) | 建议 | `dim_sku.spu_id` | 商品基础表现有 SPU 编码 |
| SPU 名称 | `spu_name` | varchar(256) | 建议 | `dim_sku.spu_name` | 商品基础表现有 SPU 名称 |
| 标准商品主键 | `standard_product_key` | varchar(128) | 必须 | `dim_sku.spu_id` / `dim_sku.sku_id` + 本算法第 17.4 节标准商品归并 | SPU 有效时取 `spu_id`，否则取 `sku_id` |
| 标准商品模式 | `standard_product_mode` | varchar(64) | 必须 | 本算法第 17.4 节标准商品归并 | 见第 29.6 节状态约束 |
| 是否可订可售 | `orderable_sellable_flag` | tinyint | 必须 | `mart_store_sku_daily_sale_order_status.is_orderable` + `mart_store_sku_daily_sale_order_status.is_saleable` + 本算法第 10.1 节范围聚合 | 按同一快照日期聚合到范围 + 门店群 + SKU；门店覆盖不足、无有效状态行或快照不一致写 NULL；主键冲突阻断本批发布 |
| 在售状态 | `listing_status` | varchar(64) | 必须 | 本算法第 10.1 节范围聚合 | 见第 29.6 节状态约束；状态覆盖不足时不得发布正式锚点 |
| 计量类型 | `measurement_type` | varchar(32) | 必须 | `dim_sku.sale_unit` / `dim_sku.specification` / 本算法第 11.1 节 | `WEIGHT` / `QUANTITY` / `PIECE_COUNT` / `VOLUME` / `UNKNOWN` |
| 销售单位 | `sale_unit` | varchar(32) | 必须 | `dim_sku.sale_unit` | 商品基础表单位 |
| 标准单位 | `standard_unit` | varchar(32) | 必须 | `dim_sku.sale_unit` / 本算法第 11.1 节标准单位映射 | 算法计算使用的标准单位 |
| 单位换算系数 | `conversion_factor` | decimal(18,8) | 条件必须 | `dim_sku.unit_weight_kg` / 本算法第 11.1 节单位换算 | 从销售单位换算到标准单位的系数 |
| 计量映射状态 | `measurement_mapping_status` | varchar(64) | 必须 | 本算法第 11.1 节单位映射 | 见第 29.6 节状态约束 |
| 订购范围口径 | `orderable_scope` | varchar(64) | 必须 | `mart_store_sku_daily_sale_order_status` / 本算法第 10 章 | 见第 29.6 节状态约束 |
| 订购门店数 | `ordered_store_cnt` | bigint | 条件必须 | `mart_sku_margin_loss.order_qty/order_weight_kg`（按 `measurement_type` 选择）+ `mart_store_sku_daily_sale_order_status.is_orderable` | 周期内适用计量类型的真实订购数量大于 0 的门店数；适用字段缺失写 NULL |
| 允许订购门店数 | `eligible_orderable_store_cnt` | bigint | 条件必须 | `mart_store_sku_daily_sale_order_status.is_orderable` + 本算法第 10.3 节周期门店集合 | 表现周期内至少有一个可订门店日的去重门店数；不得使用当前在售快照分母 |
| 门店订购率 | `store_order_rate` | decimal(18,8) | 条件必须 | 本算法第 10.3 节订购率 | 订购门店数 / 允许订购该 SKU 的有效门店数 |
| 订购门店日数 | `ordered_store_day_cnt` | bigint | 条件必须 | `mart_sku_margin_loss.order_qty/order_weight_kg`（按 `measurement_type` 选择）+ 本算法第 10.3 节 | 表现周期内属于历史门店群、可订且真实订购数量大于 0 的去重门店日数；订购日率分子 |
| 允许订购有效门店日数 | `eligible_orderable_store_day_cnt` | bigint | 条件必须 | `mart_store_sku_daily_sale_order_status.is_orderable/business_date` + 本算法第 10.3 节 | 表现周期内属于历史门店群且 `is_orderable=1` 的去重门店日数 |
| 门店订购日率 | `ordered_store_day_rate` | decimal(18,8) | 条件必须 | `mart_sku_margin_loss.order_qty/order_weight_kg`（按 `measurement_type` 选择）+ 本算法第 10.3 节 | 有真实订购数量的门店日数 / 允许订购的有效门店营业日数 |

行为、偏好和复购字段：

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| SKU 销售额 | `sku_sales_amt` | decimal(18,6) | 必须 | Doris 小票 | 目标画像购买该 SKU 的有效销售额 |
| SKU 销售标准量 | `sku_sales_qty` | decimal(18,6) | 必须 | Doris `weight` | 目标画像购买该 SKU 的销售标准量，`weight` 为计价数量 |
| SKU 小票数 | `sku_ticket_cnt` | bigint | 必须 | Doris `order_id` | 目标画像购买该 SKU 的去重小票数 |
| SKU 购买会员数 | `sku_buyer_cnt` | bigint | 必须 | Doris `customer_id` | 目标画像购买该 SKU 的去重会员数 |
| SKU 销售占比 | `sku_sales_share` | decimal(18,8) | 必须 | 本算法第 8 节 SKU 基础表现 | 该 SKU 销售额 / 目标画像该品类销售额 |
| 目标画像品类总销售额 | `target_profile_category_sales_amt` | decimal(18,6) | 必须 | `data_agent.dws_member_order_item_detail_df_all_new` + 本算法第 8 节品类分母聚合 | 目标画像该品类有效销售额；作为销售占比分母 |
| SKU 小票渗透率 | `sku_ticket_penetration` | decimal(18,8) | 必须 | 本算法第 8 节 SKU 基础表现 | 购买该 SKU 的小票数 / 目标画像该品类小票数 |
| 目标画像品类总小票数 | `target_profile_category_ticket_cnt` | bigint | 必须 | 本算法第 8 节 SKU 基础表现 | 目标画像该品类去重小票数；作为小票渗透率分母 |
| SKU 会员渗透率原始值 | `sku_buyer_penetration_raw` | decimal(18,8) | 必须 | 本算法第 12.2 节原始渗透率 | 购买该 SKU 的会员数 / 目标画像该品类会员数 |
| 目标画像品类去重会员数 | `target_profile_category_buyer_cnt` | bigint | 必须 | 本算法第 12.2 节原始渗透率 | 目标画像在当前比较组、品类内的去重购买会员数；作为会员渗透率分母 |
| SKU 会员渗透率 95% 下界 | `sku_buyer_penetration_lower_95` | decimal(18,8) | 必须 | Jeffreys 区间 | 目标画像会员渗透率 95% 区间下界 |
| SKU 会员渗透率 95% 上界 | `sku_buyer_penetration_upper_95` | decimal(18,8) | 必须 | Jeffreys 区间 | 目标画像会员渗透率 95% 区间上界 |
| 目标画像渗透率 | `target_penetration` | decimal(18,8) | 必须 | 本算法第 12.2 节原始渗透率 | 目标画像购买该 SKU 的会员渗透率 |
| 目标画像渗透率分子 | `target_penetration_numerator` | bigint | 必须 | 本算法第 12.2 节原始渗透率 | 目标画像购买该 SKU 的去重会员数 |
| 目标画像渗透率分母 | `target_penetration_denominator` | bigint | 必须 | 本算法第 12.2 节原始渗透率 | 目标画像在相同可购买门店日内购买该品类的去重会员数 |
| 参考画像渗透率 | `reference_penetration` | decimal(18,8) | 条件必须 | 本算法第 12.2 节原始渗透率 | 非目标画像购买该 SKU 的会员渗透率 |
| 参考画像渗透率分子 | `reference_penetration_numerator` | bigint | 条件必须 | 本算法第 12.2 节原始渗透率 | 参考画像购买该 SKU 的去重会员数 |
| 参考画像渗透率分母 | `reference_penetration_denominator` | bigint | 条件必须 | 本算法第 12.2 节原始渗透率 | 参考画像在相同可购买门店日内购买该品类的去重会员数 |
| 偏好参考组状态 | `preference_reference_status` | varchar(64) | 必须 | `mart_store_group_consumer_contribution` + 本算法第 12.4 节对照组判断 | 见第 29.6 节状态约束 |
| 原始偏好指数 | `preference_index_raw` | decimal(18,8) | 条件必须 | 本算法第 12.3 节偏好指数 | 目标画像渗透率 / 参考画像渗透率 |
| 平滑偏好指数 | `smoothed_preference_index` | decimal(18,8) | 条件必须 | Jeffreys 平滑 | 小样本校正后的偏好指数 |
| 偏好指数 95% 下界 | `preference_lower_95` | decimal(18,8) | 条件必须 | Jeffreys 区间 | 正式评分使用下界 |
| 偏好指数 95% 上界 | `preference_upper_95` | decimal(18,8) | 条件必须 | Jeffreys 区间 | 偏好指数区间上界 |
| 7 天复购会员数 | `repeat_buyer_cnt_7d_pre19` | bigint | 必须 | `mart_sku_repurchase_7d_pre19` | 7 天内且 19:00 前复购该 SKU 的会员数 |
| 7 天可观察首购会员数 | `eligible_first_buyer_cnt_7d` | bigint | 必须 | `mart_sku_repurchase_7d_pre19` | 有完整 7 天观察窗口的首购会员数 |
| 观察不足首购会员数 | `insufficient_observation_first_buyer_cnt` | bigint | 必须 | `mart_sku_repurchase_7d_pre19` | 观察窗口不足的首购会员诊断人数；不进入复购率 |
| 观察不足但已观察到复购会员数 | `insufficient_observation_observed_repeat_buyer_cnt_pre19` | bigint | 必须 | `mart_sku_repurchase_7d_pre19` | 观察不足会员中周期结束前已观察到复购的诊断人数；不进入复购率 |
| 7 天 19 点前复购率原始值 | `repurchase_rate_7d_pre19_raw` | decimal(18,8) | 条件必须 | `mart_sku_repurchase_7d_pre19` | 原始复购率 |
| 7 天 19 点前复购率 95% 下界 | `repurchase_rate_7d_pre19_lower_95` | decimal(18,8) | 条件必须 | Jeffreys 区间 | 正式评分使用下界 |
| 7 天 19 点前复购率 95% 上界 | `repurchase_rate_7d_pre19_upper_95` | decimal(18,8) | 条件必须 | Jeffreys 区间 | 复购率区间上界 |

经营、毛利和价格字段：

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 有效门店 SKU 日数 | `available_store_day_cnt` | bigint | 必须 | `mart_sku_margin_loss` / `mart_store_sku_daily_sale_order_status` | 周期内有实际收货条件的门店 SKU 日数 |
| 每有效门店 SKU 日销售额 | `sales_per_available_store_day` | decimal(18,8) | 条件必须 | 本算法第 10.2 节有效在售 SKU 日 | 目标画像销售额 / 有效门店 SKU 日数 |
| 每有效门店 SKU 日购买会员数 | `buyers_per_available_store_day` | decimal(18,8) | 条件必须 | 本算法第 10.2 节有效在售 SKU 日 | 目标画像购买会员数 / 有效门店 SKU 日数 |
| 实际到货标准量 | `actual_arrival_standard_qty` | decimal(18,6) | 条件必须 | `mart_sku_margin_loss.receipt_qty` / `mart_sku_margin_loss.receipt_weight_kg` / `dim_sku.sale_unit` | 称重商品取门店进货重量；普通计件和枚数型商品取门店进货数量；体积商品可稳定换算时按标准体积口径换算 |
| 19:30 前销售标准量 | `pre1930_sales_standard_qty` | decimal(18,6) | 条件必须 | `data_agent.dws_member_order_item_detail_df_all_new.weight` | 有效 SKU 日 19:30 前销售标准量 |
| 非促销有效门店 SKU 日数 | `non_promo_available_store_day_cnt` | bigint | 条件必须 | `data_agent.dws_member_order_item_detail_df_all_new.discount_amt` + `mart_sku_margin_loss` | 19:30 前 `discount_amt = 0` 的有效门店 SKU 日数 |
| 非促销实际到货标准量 | `non_promo_actual_arrival_standard_qty` | decimal(18,6) | 条件必须 | `mart_sku_margin_loss.receipt_qty/receipt_weight_kg` + `dim_sku.sale_unit` + 本算法第 14.2 节非促销窗口过滤 | 非促销有效 SKU 日实际到货标准量 |
| 非促销 19:30 前销售标准量 | `non_promo_pre1930_sales_standard_qty` | decimal(18,6) | 条件必须 | `data_agent.dws_member_order_item_detail_df_all_new.weight` | 非促销有效 SKU 日 19:30 前销售标准量 |
| SKU 总 19:30 前销售标准量 | `sku_total_pre1930_sales_standard_qty` | decimal(18,6) | 条件必须 | `data_agent.dws_member_order_item_detail_df_all_new.weight` | 全量有效交易该 SKU 19:30 前销售标准量；用于经营解释，不作为目标画像吸收率分母 |
| 目标画像 19:30 前销售标准量 | `target_profile_pre1930_sales_standard_qty` | decimal(18,6) | 条件必须 | 本算法第 14.5 节 `valid_profiled_member_txn.weight` 聚合 | 目标画像吸收率分子；先按有效门店 SKU 日汇总，再按比较组聚合 |
| 19:30 前售罄率 | `pre1930_sell_through_rate` | decimal(18,8) | 条件必须 | `data_agent.dws_member_order_item_detail_df_all_new.weight` + `mart_sku_margin_loss.receipt_qty/receipt_weight_kg` | 19:30 前销售标准量 / 实际收货标准量 |
| 非促销 19:30 前售罄率 | `non_promo_pre1930_sell_through_rate` | decimal(18,8) | 条件必须 | `data_agent.dws_member_order_item_detail_df_all_new.weight` + `mart_sku_margin_loss.receipt_qty/receipt_weight_kg` | 剔除 `discount_amt > 0` 代理促销后的 19:30 前售罄率 |
| 每有效门店 SKU 日 19:30 前销售量 | `pre1930_sales_volume_per_available_store_day` | decimal(18,8) | 条件必须 | `data_agent.dws_member_order_item_detail_df_all_new.weight` | 19:30 前销售标准量 / 有效门店 SKU 日数 |
| 目标画像 19:30 前吸收率 | `target_profile_pre1930_absorption_rate` | decimal(18,8) | 条件必须 | 本算法第 14.5 节吸收贡献 | `target_profile_pre1930_sales_standard_qty / actual_arrival_standard_qty`；两项均保留以供复算 |
| 折扣阶梯 JSON | `discount_ladder_json` | json | 必须 | Doris 小票 + 本算法第 15 章 | JSON 数组；每项含 `band_start`、`band_end`、`sales_standard_qty`、`incremental_sell_through_rate`、`cumulative_sell_through_rate_at_band_end`、`actual_discount_rate`；无数据写 `[]` |
| 目标画像 SKU 销售额 | `target_profile_sku_sales_amt` | decimal(18,6) | 必须 | Doris 小票 | 目标画像该 SKU 销售额 |
| 目标画像 SKU 成本额 | `target_profile_sku_cost_amt` | decimal(18,6) | 条件必须 | `mart_sku_margin_loss.sales_amt/full_link_margin_amt` + 本算法第 16.3 节目标画像成本分摊 | 按标准量单位成本分摊到目标画像的 SKU 成本金额 |
| 目标画像 SKU 毛利额 | `target_profile_sku_margin_amt` | decimal(18,6) | 条件必须 | 本算法第 16.1 节毛利公式 | `target_profile_sku_sales_amt - target_profile_sku_cost_amt` |
| 目标画像 SKU 毛利率 | `target_profile_sku_margin_rate` | decimal(18,8) | 条件必须 | 本算法第 16.1 节毛利公式 | `target_profile_sku_margin_amt / target_profile_sku_sales_amt` |
| SKU 总销售额 | `sku_total_sales_amt` | decimal(18,6) | 必须 | `mart_sku_margin_loss.sales_amt` | 该 SKU 在比较组内全量销售额 |
| SKU 总成本额 | `sku_total_cost_amt` | decimal(18,6) | 条件必须 | `mart_sku_margin_loss.sales_amt` + `mart_sku_margin_loss.full_link_margin_amt` + 本算法第 16 章 | `sku_total_sales_amt - sku_total_margin_amt` |
| SKU 总毛利额 | `sku_total_margin_amt` | decimal(18,6) | 条件必须 | `mart_sku_margin_loss.full_link_margin_amt` | 该 SKU 在比较组内全链路毛利额 |
| SKU 总毛利率 | `sku_total_margin_rate` | decimal(18,8) | 条件必须 | 本算法第 16.1 节毛利公式 | `sku_total_margin_amt / sku_total_sales_amt` |
| 成本来源 | `cost_source` | varchar(64) | 必须 | 本算法第 16.3 节成本落地口径 | 见第 29.6 节状态约束 |
| 成本分摊方法 | `cost_allocation_method` | varchar(64) | 必须 | 本算法第 16.3 节成本落地口径 | V1 默认 `UNIT_COST_BY_STANDARD_QTY` |
| 成本分摊状态 | `cost_allocation_status` | varchar(64) | 必须 | 本算法第 16.3 节成本落地口径 | 见第 29.6 节状态约束 |
| SKU 实付均价 | `sku_avg_paid_price` | decimal(18,6) | 建议 | Doris 小票 | 目标画像该 SKU 实付销售额 / 销售标准量 |
| 销售原价 | `original_price` | decimal(18,6) | 条件必须 | `mart_store_sku_daily_price.original_sale_price` | 当前价格快照销售原价；缺失写 NULL + `PRICE_SOURCE_MISSING` |
| 目标画像平均实付价 | `target_profile_avg_paid_price` | decimal(18,6) | 条件必须 | `data_agent.dws_member_order_item_detail_df_all_new.usual_amt/weight` + 本算法第 18 节画像分组聚合 | 目标画像实付金额 / 目标画像销售标准量；分母无效写 NULL |
| 参考画像 SKU 实付金额 | `reference_profile_sku_sales_amt` | decimal(18,6) | 条件必须 | `valid_profiled_member_txn.line_transaction_amt` + 本算法第 18 节参考画像分组聚合 | 参考画像平均实付价分子；无参考画像写 NULL |
| 参考画像 SKU 销售标准量 | `reference_profile_sku_sales_standard_qty` | decimal(18,6) | 条件必须 | `valid_profiled_member_txn.sales_standard_qty` + 本算法第 18 节参考画像分组聚合 | 参考画像平均实付价分母；无参考画像或分母无效时写 NULL |
| 参考画像平均实付价 | `reference_profile_avg_paid_price` | decimal(18,6) | 条件必须 | `reference_profile_sku_sales_amt / reference_profile_sku_sales_standard_qty` | 无参考画像或分母无效时写 NULL |
| 标准化成交价格 | `standardized_paid_price` | decimal(18,6) | 条件必须 | 本算法第 18 节价格指标 | 按标准单位换算后的成交价格；单位不可解释写 NULL |
| 促销前后价格 JSON | `before_after_promotion_price` | json | 条件必须 | 价格表 + Doris 小票 | JSON 对象，键为 `before_price`、`after_price`、`price_source`；`price_source` 只允许 `PRICE_TABLE_ORIGINAL_DORIS_USUAL_AMT_PER_WEIGHT`；任一来源缺失时整个对象写 `NULL` 并标记 `PRICE_SOURCE_MISSING` |
| 实际折扣率 | `actual_discount_rate` | decimal(18,8) | 条件必须 | 本算法第 18 节价格指标 | `1 - after_price / before_price`；价格缺失或分母为 0 写 NULL |
| 促销识别方式 | `promotion_identify_method` | varchar(64) | 必须 | 本算法第 15 节折扣代理规则 | V1 固定为 `DISCOUNT_PROXY_V1` |

得分和锚点字段：

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 画像贡献维度分 | `contribution_dimension_score` | decimal(18,8) | 条件必须 | 本算法第 19.1 节一级评分维度 | 目标画像贡献维度得分 |
| 画像偏好维度分 | `preference_dimension_score` | decimal(18,8) | 条件必须 | 本算法第 19.2 节一级评分维度 | 目标画像偏好维度得分 |
| 自然动销维度分 | `natural_sales_dimension_score` | decimal(18,8) | 条件必须 | 本算法第 19.3 节一级评分维度 | 19:30 前自然动销维度得分 |
| 毛利维度分 | `margin_dimension_score` | decimal(18,8) | 条件必须 | 本算法第 19.4 节一级评分维度 | 商品毛利维度得分 |
| 维度权重 JSON | `dimension_weights_json` | json | 必须 | CRITIC | JSON 对象；键为维度/指标编码，值为 decimal 权重；不适用维度不写键 |
| 点估计观察分 | `point_evidence_score` | decimal(18,8) | 条件必须 | 本算法第 20-21 节标准化与 CRITIC | 使用后验均值计算的观察分，用于低证据对比 |
| SKU 表现综合分 | `sku_performance_score` | decimal(18,8) | 条件必须 | 本算法第 21 节两级 CRITIC | 正式保守综合表现分，使用 95% 下界 |
| 选中分组数量 | `selected_cluster_count` | int | 条件必须 | Jenks/BIC | 可计算时为 1、2 或 3；`DATA_INCOMPLETE` / `NOT_CALCULABLE` 且无法分组时写 NULL |
| Jenks 分割点 JSON | `jenks_breaks_json` | json | 必须 | Jenks/BIC | JSON 数组；按升序保存各分割点 decimal；K=1 写 `[]` |
| SSE 结果 JSON | `sse_by_k_json` | json | 必须 | Jenks/BIC | JSON 对象：`status` 见第 29.6 节，`values` 的键为字符串 K、值为 SSE decimal 或 JSON null |
| BIC 结果 JSON | `bic_by_k_json` | json | 必须 | Jenks/BIC | JSON 对象：`status` 见第 29.6 节，`values` 的键为字符串 K、值为 BIC decimal 或 JSON null |
| 表现分组 | `performance_group` | varchar(64) | 必须 | 本算法第 22 章 Jenks+BIC 分组 | 见第 29.6 节状态约束 |
| 是否正式锚点 | `is_formal_anchor` | tinyint | 必须 | 本算法第 23 章正式锚点准入 | `1` 是正式锚点，`0` 不是 |
| 锚点生命周期状态 | `anchor_lifecycle_status` | varchar(64) | 必须 | 本算法第 24 章当前/历史锚点 | 见第 29.6 节状态约束 |
| 锚点证据类型 | `anchor_evidence_type` | varchar(64) | 必须 | 本算法第 23-27 章锚点证据判定 | 见第 29.6 节状态约束 |

稳定性、属性和状态字段：

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| Top1 门店销售额 | `top1_store_sales_amt` | decimal(18,6) | 条件必须 | 本算法第 25.1 节门店级销售聚合 | 当前业务范围内该 SKU 销售额最高门店的销售额；Top1 占比分子 |
| Top1 门店销售占比 | `top1_store_sales_share` | decimal(18,8) | 条件必须 | `top1_store_sales_amt / sku_total_sales_amt` | 最大单店销售额 / 该 SKU 总销售额 |
| 门店销售 HHI | `store_sales_hhi` | decimal(18,8) | 条件必须 | 本算法第 25.1 节门店集中度 | 门店销售集中度 |
| 有效留一门店验证次数 | `valid_leave_one_store_test_cnt` | bigint | 必须 | 本算法第 25.2 节留一门店验证 | 能完整重算评分和分组的留一门店场景数；稳定率分母 |
| 留一门店仍为锚点次数 | `leave_one_store_anchor_retained_cnt` | bigint | 必须 | 本算法第 25.2 节留一门店验证 | 有效场景中仍满足正式锚点的次数；稳定率分子 |
| 留一门店锚点稳定率 | `leave_one_store_anchor_rate` | decimal(18,8) | 条件必须 | 本算法第 25.2 节留一门店验证 | 删除单店后仍为锚点的比例 |
| 门店稳定性状态 | `store_stability_status` | varchar(64) | 必须 | 本算法第 25.2 节留一门店验证 | 见第 29.6 节状态约束 |
| 有效留一月验证次数 | `valid_leave_one_month_test_cnt` | bigint | 必须 | 本算法第 26 章时间稳定性验证 | 能完整重算评分和分组的留一月场景数；稳定率分母 |
| 留一月仍为锚点次数 | `leave_one_month_anchor_retained_cnt` | bigint | 必须 | 本算法第 26 章时间稳定性验证 | 有效场景中仍满足正式锚点的次数；稳定率分子 |
| 留一月锚点稳定率 | `leave_one_month_anchor_rate` | decimal(18,8) | 条件必须 | 本算法第 26 章时间稳定性验证 | 删除单月后仍为锚点的比例 |
| 时间稳定性状态 | `time_stability_status` | varchar(64) | 必须 | 本算法第 26 章时间稳定性验证 | 见第 29.6 节状态约束 |
| 拉动月份 JSON | `pull_months_json` | json | 条件必须 | 本算法第 26 章有效留一月验证 | `YYYY-MM` 字符串数组；无拉动月写 `[]`，有效验证不足写 SQL `NULL` |
| 温层 | `temperature_layer` | varchar(64) | 建议 | `dim_sku.temperature_layer` | 冷藏、冷冻、常温等 |
| 品牌 | `brand_name` | varchar(128) | 建议 | `dim_sku.brand_name` | 商品品牌 |
| 属性来源 JSON | `attribute_source_json` | json | 必须 | 本算法第 17.2 节读取 `dim_sku` 快照 | JSON 对象；固定五个 V1 属性键，值为 `MASTER_DATA` / `UNKNOWN` |
| 属性置信度 JSON | `attribute_confidence_json` | json | 必须 | 本算法第 17.2 节属性置信度缺失处理 | JSON 对象；固定五个 V1 属性键，值均为 JSON `null`；没有已验收的置信度模型时不编造数值 |
| 商品状态编码 | `product_status_code` | varchar(8) | 建议 | `dim_product_status` | `A` / `O` / `S` / `D` / `B`；V1 不参与评分，缺失写 NULL |
| 商品状态可用性 | `product_status_availability` | varchar(32) | 必须 | `dim_product_status` + 本算法第 18 节商品状态可用性判定 | `AVAILABLE` 或 `NOT_AVAILABLE`；缺失不得编造停售/季节原因 |
| 结果状态 | `result_status` | varchar(64) | 必须 | 本算法第 28 章结果状态设计 | 见第 29.6 节状态约束 |
| 盈利状态 | `profitability_status` | varchar(64) | 必须 | 本算法第 16.4 节毛利底线 | 见第 29.6 节状态约束 |
| 证据状态 | `evidence_status` | varchar(64) | 必须 | 本算法第 13 章统计证据 | 见第 29.6 节状态约束 |
| 自然动销状态 | `natural_sales_status` | varchar(64) | 必须 | 本算法第 14 章自然动销 | 见第 29.6 节状态约束 |
| 订购覆盖状态 | `order_coverage_status` | varchar(64) | 必须 | 本算法第 10.3-10.4 节订购覆盖 | 见第 29.6 节状态约束 |
| 属性状态 | `attribute_status` | varchar(64) | 必须 | 本算法第 17 章商品属性 | 见第 29.6 节状态约束 |
| 数据质量标记 JSON | `data_quality_flags` | json | 必须 | 本算法第 32 章数据质量验收 | JSON 数组；每项为稳定英文标记；无标记写 `[]`；字段缺失、单位换算失败和价格/成本冲突等降级必须显式记录 |
| 计算时间 | `calculated_at` | datetime | 必须 | 系统生成 | 结果写入时间 |

### 29.3 标准商品表现：`mart_target_profile_product_performance`

一行代表：一个周期、一个范围、一个门店群、一个消费者画像和一个标准商品的表现结果。

主键：

```text
algorithm_batch_version
+ performance_start_date
+ performance_end_date
+ scope_type
+ scope_id
+ category_granularity
+ category_code
+ store_group_type
+ final_level
+ final_profile
+ standard_product_key
```

本表以与 SKU 层相同的交易级和门店日级过程数据独立重算。V1 优先按商品基础表 `spu_id` 归并；`spu_id` 缺失时 `standard_product_key = sku_id`，`standard_product_mode = SKU_ONLY`。成员 SKU 表仅提供成员关系和追溯证据，销售额、去重小票、去重会员、复购、成本、评分和状态不得由 SKU 正式结果简单求和或继承。

标准商品层的在售状态必须在成员 SKU 状态稳定后重新聚合，不能从代表 SKU 直接继承：

```text
1. 成员 SKU 必须使用同一 `listing_snapshot_date` 和 `listing_scope_aggregation_method`，并先验证有效门店覆盖完整、成员集合无冲突、成员状态均来自同一快照。
2. 任一成员 SKU 状态为 NULL、成员覆盖不足或快照不一致时，标准商品两个字段都写 NULL，并在 `data_quality_flags` 写 `DATA_INSUFFICIENT`；此时不得继续按 ACTIVE/INACTIVE 推断。标准商品成员映射或主键冲突属于输入质量失败，直接阻断整批发布，不写正式诊断行。
3. V1 固定 `standard_product_listing_method = ANY_ACTIVE_MEMBER`。在第 1-2 步通过后，任一成员 SKU 为 ACTIVE 即标准商品为 ACTIVE；全部成员 SKU 均为 INACTIVE 才判 INACTIVE。
4. 成员状态未知或覆盖不足时，标准商品 `orderable_sellable_flag`、`listing_status` 写 NULL，不能进入正式锚点。
5. `listing_status = NULL` 只能表示当前在售不可判断，不得转写为 `HISTORICAL_ANCHOR`；历史锚点必须有明确 `listing_status = INACTIVE`。
```

标准商品层的销售额、去重小票/会员、成本、CRITIC、Jenks/BIC 和锚点准入仍按第 17.4 节重新计算；不得把成员 SKU 分数或代表 SKU 状态冒充标准商品结论。

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 统一算法批次版本 | `algorithm_batch_version` | varchar(32) | 必须 | `mart_target_profile_sku_performance.algorithm_batch_version` | 固定为 `BATCH_YYYYMM`；与算法 01～03 同批，并进入本表唯一键 |
| 运行ID | `run_id` | varchar(64) | 必须 | 调度系统 | 本次结果所属算法 04 实际运行；同批原子发布的三张结果表和一张参数表使用同一 `run_id` |
| 重跑原因 | `rerun_reason` | varchar(512) | 条件必须 | 调度运行清单 | 同批次修正重跑时必填；首次运行可为 NULL |
| 更新时间 | `updated_at` | datetime | 必须 | 系统生成 | 本批本处理单元最近一次成功写入时间 |
| 数据周期开始日期 | `performance_start_date` | date | 必须 | `mart_target_profile_sku_performance.performance_start_date` + 本算法第 29.3 节标准商品层聚合 | 统计周期开始日期 |
| 数据周期结束日期 | `performance_end_date` | date | 必须 | `mart_target_profile_sku_performance.performance_end_date` + 本算法第 29.3 节标准商品层聚合 | 统计周期结束日期 |
| 范围类型 | `scope_type` | varchar(32) | 必须 | `mart_target_profile_sku_performance.scope_type` + 本算法第 29.3 节标准商品层聚合 | `CITY` / `CITY_CLUSTER` |
| 范围编码 | `scope_id` | varchar(64) | 必须 | `mart_target_profile_sku_performance.scope_id` + 本算法第 29.3 节标准商品层聚合 | 城市或城市群编码 |
| 范围名称 | `scope_name` | varchar(128) | 必须 | `mart_target_profile_sku_performance.scope_name` + 本算法第 29.3 节标准商品层聚合 | 城市或城市群名称 |
| 品类颗粒度 | `category_granularity` | varchar(32) | 必须 | `mart_target_profile_sku_performance.category_granularity` + 本算法第 29.3 节标准商品层聚合 | 大类 / 中类 / 小类 |
| 品类编码 | `category_code` | varchar(64) | 必须 | `mart_target_profile_sku_performance.category_code` + 本算法第 29.3 节标准商品层聚合 | 当前计算品类编码 |
| 品类名称 | `category_name` | varchar(128) | 必须 | `mart_target_profile_sku_performance.category_name` + 本算法第 29.3 节标准商品层聚合 | 当前计算品类名称 |
| 门店群类型 | `store_group_type` | varchar(32) | 必须 | `mart_target_profile_sku_performance.store_group_type` + 本算法第 29.3 节标准商品层聚合 | `FINAL_LEVEL` / `ALL_RATED` |
| 门店品类等级 | `final_level` | varchar(32) | 必须 | `mart_target_profile_sku_performance.final_level` + 本算法第 29.3 节标准商品层聚合 | 当前门店群等级 |
| 消费者画像 | `final_profile` | varchar(128) | 必须 | `mart_target_profile_sku_performance.final_profile` + 本算法第 29.3 节标准商品层聚合 | 目标消费者画像 |
| 门店品类等级开始日期 | `category_level_start_date` | date | 必须 | `mart_target_profile_sku_performance.category_level_start_date` + 本算法第 29.3 节标准商品层聚合 | 算法 02 结果周期开始日期 |
| 门店品类等级结束日期 | `category_level_end_date` | date | 必须 | `mart_target_profile_sku_performance.category_level_end_date` + 本算法第 29.3 节标准商品层聚合 | 算法 02 结果周期结束日期 |
| 消费者贡献开始日期 | `consumer_contribution_start_date` | date | 必须 | `mart_target_profile_sku_performance.consumer_contribution_start_date` + 本算法第 29.3 节标准商品层聚合 | 算法 03 结果周期开始日期 |
| 消费者贡献结束日期 | `consumer_contribution_end_date` | date | 必须 | `mart_target_profile_sku_performance.consumer_contribution_end_date` + 本算法第 29.3 节标准商品层聚合 | 算法 03 结果周期结束日期 |
| 在售快照日期 | `listing_snapshot_date` | date | 必须 | SKU 表现表 `listing_snapshot_date` + 标准商品层成员 SKU 聚合 | 标准商品层当前可订可售状态使用的锁定快照日期 |
| 在售范围聚合方法 | `listing_scope_aggregation_method` | varchar(64) | 必须 | `mart_target_profile_sku_performance.listing_scope_aggregation_method` / 调度参数 + 本算法第 10.1.1 节有效门店集合 | V1 固定 `ANY_ACTIVE_STORE`；标准商品层沿用同批范围规则 |
| 标准商品成员在售方法 | `standard_product_listing_method` | varchar(64) | 必须 | 本算法第 17.4、29.3 节成员状态聚合 | V1 固定 `ANY_ACTIVE_MEMBER`；任一成员 ACTIVE 则标准商品 ACTIVE，全部成员 INACTIVE 才判 INACTIVE |
| 是否可订可售 | `orderable_sellable_flag` | tinyint | 必须 | SKU 表现表 `orderable_sellable_flag` + 本算法第 29.3 节标准商品层聚合 | V1 按 `ANY_ACTIVE_MEMBER` 计算；成员状态未知或覆盖不足时为 `NULL` |
| 在售状态 | `listing_status` | varchar(64) | 必须 | SKU 表现表 `listing_status` + 本算法第 29.3 节标准商品层聚合 | `ACTIVE` / `INACTIVE` / `NULL`；`NULL` 不得降级为历史锚点 |
| 标准商品主键 | `standard_product_key` | varchar(128) | 必须 | `mart_target_profile_sku_performance.standard_product_key` + 本算法第 17.4、29.3 节归并 | SPU 有效时取 `spu_id`，否则取 `sku_id` |
| 标准商品名称 | `standard_product_name` | varchar(256) | 必须 | `dim_sku.spu_name` / `dim_sku.sku_name` + 本算法第 17.4、29.3 节代表 SKU 归并 | SPU 名称或代表 SKU 名称 |
| 标准商品模式 | `standard_product_mode` | varchar(64) | 必须 | `mart_target_profile_sku_performance.standard_product_mode` + 本算法第 17.4 节标准商品归并 | `SPU_MAPPED` / `SKU_ONLY` |
| SPU 编码 | `spu_id` | varchar(64) | 建议 | `dim_sku.spu_id` | 商品基础表 SPU 编码 |
| SPU 名称 | `spu_name` | varchar(256) | 建议 | `dim_sku.spu_name` | 商品基础表 SPU 名称 |
| 代表 SKU 编码 | `representative_sku_id` | varchar(64) | 必须 | `mart_target_profile_sku_performance.sku_id` + 本算法第 17.4 节标准商品归并 | 展示和追溯使用的代表 SKU |
| 成员 SKU 列表 JSON | `member_sku_list_json` | json | 必须 | `mart_target_profile_sku_performance.sku_id` + 本算法第 17.4 节标准商品归并 | JSON 数组；每项为 `sku_id` 字符串；无成员不写虚假 SKU，写 `[]` |
| 成员 SKU 数 | `member_sku_cnt` | bigint | 必须 | `mart_target_profile_sku_performance.sku_id` + 本算法第 17.4 节标准商品归并 | 标准商品下 SKU 数 |
| 标准商品计量类型 | `measurement_type` | varchar(32) | 必须 | `dim_sku.sale_unit/unit_weight_kg` + 本算法第 11、17.4 节成员换算 | `WEIGHT` / `QUANTITY` / `PIECE_COUNT` / `VOLUME` / `UNKNOWN`；成员无法统一时为 `UNKNOWN` |
| 标准商品标准单位 | `standard_unit` | varchar(32) | 条件必须 | 本算法第 11、17.4 节成员换算 | 成员可统一换算时写 kg、piece、count 或 L；不可统一时 NULL |
| 计量映射状态 | `measurement_mapping_status` | varchar(64) | 必须 | 本算法第 11、17.4 节成员换算 | 见第 29.6 节状态约束 |
| 标准商品销售额 | `product_sales_amt` | decimal(18,6) | 必须 | `valid_profiled_member_txn` + 本算法第 17.4 节标准商品层聚合 | 标准商品层目标画像销售额 |
| 标准商品销售标准量 | `product_sales_qty` | decimal(18,6) | 条件必须 | `valid_profiled_member_txn.sales_standard_qty` + 本算法第 17.4 节成员换算 | 成员计量类型可统一时汇总；不可统一时 NULL |
| 标准商品小票数 | `product_ticket_cnt` | bigint | 必须 | `valid_profiled_member_txn.ticket_key` + 本算法第 17.4 节去重 | 标准商品层直接按交易级小票去重，不汇总 SKU 小票数 |
| 标准商品购买会员数 | `product_buyer_cnt` | bigint | 必须 | `valid_profiled_member_txn.customer_id` + 本算法第 17.4 节去重 | 标准商品层直接按交易级会员去重，不汇总 SKU 会员数 |
| 标准商品销售占比 | `product_sales_share` | decimal(18,8) | 必须 | `product_sales_amt / target_profile_category_sales_amt` | 标准商品销售额占目标画像品类销售额比例 |
| 目标画像品类总销售额 | `target_profile_category_sales_amt` | decimal(18,6) | 必须 | `valid_profiled_member_txn` 品类聚合 | `product_sales_share` 分母 |
| 标准商品小票渗透率 | `product_ticket_penetration` | decimal(18,8) | 必须 | `product_ticket_cnt / target_profile_category_ticket_cnt` | 标准商品小票覆盖率 |
| 目标画像品类总小票数 | `target_profile_category_ticket_cnt` | bigint | 必须 | `valid_profiled_member_txn.ticket_key` 品类去重 | 小票渗透率分母 |
| 标准商品会员渗透率原始值 | `product_buyer_penetration_raw` | decimal(18,8) | 必须 | `product_buyer_cnt / target_profile_category_buyer_cnt` | 标准商品会员渗透原始比例 |
| 标准商品会员渗透率 95% 下界 | `product_buyer_penetration_lower_95` | decimal(18,8) | 必须 | 本算法第 13、17.4 节 Jeffreys 区间 | 正式评分使用下界 |
| 标准商品会员渗透率 95% 上界 | `product_buyer_penetration_upper_95` | decimal(18,8) | 必须 | 本算法第 13、17.4 节 Jeffreys 区间 | 解释字段 |
| 目标画像品类去重会员数 | `target_profile_category_buyer_cnt` | bigint | 必须 | `valid_profiled_member_txn.customer_id` 品类去重 | 目标画像渗透率分母 |
| 参考画像标准商品购买会员数 | `reference_product_buyer_cnt` | bigint | 条件必须 | `valid_profiled_member_txn.customer_id` + 本算法第 12、17.4 节参考画像聚合 | 无参考画像时为 NULL |
| 参考画像品类去重会员数 | `reference_profile_category_buyer_cnt` | bigint | 条件必须 | `valid_profiled_member_txn.customer_id` + 本算法第 12 节 | 无参考画像时为 NULL |
| 标准商品目标画像渗透率 | `product_target_penetration` | decimal(18,8) | 必须 | `product_buyer_cnt / target_profile_category_buyer_cnt` | 目标画像标准商品渗透率 |
| 标准商品参考画像渗透率 | `product_reference_penetration` | decimal(18,8) | 条件必须 | `reference_product_buyer_cnt / reference_profile_category_buyer_cnt` | 无参考画像时为 NULL |
| 标准商品偏好参考组状态 | `preference_reference_status` | varchar(64) | 必须 | `mart_store_group_consumer_contribution` + 本算法第 12.4、17.4 节标准商品层对照组判断 | 见第 29.6 节状态约束；无参考画像时偏好指标写 NULL 并从标准商品层 CRITIC 移除 |
| 标准商品偏好指数原始值 | `product_preference_index_raw` | decimal(18,8) | 条件必须 | 本算法第 12、17.4 节 | 目标渗透率 / 参考渗透率；参考为 0 时按原始规则处理 |
| 标准商品偏好指数平滑值 | `product_preference_index_smoothed` | decimal(18,8) | 条件必须 | 本算法第 12、17.4 节 Jeffreys 平滑 | 无参考画像时为 NULL |
| 标准商品偏好指数 95% 下界 | `product_preference_lower_95` | decimal(18,8) | 条件必须 | 本算法第 13、17.4 节区间估计 | 标准商品层正式评分使用的偏好下界；无参考画像写 NULL |
| 标准商品偏好指数 95% 上界 | `product_preference_upper_95` | decimal(18,8) | 条件必须 | 本算法第 13、17.4 节区间估计 | 解释字段；无参考画像写 NULL |
| 7 天复购会员数 | `repeat_buyer_cnt_7d_pre19` | bigint | 必须 | 标准商品层交易级复购过程计算 | 同一标准商品成员 SKU 之间的跨码复购按标准商品去重后计算 |
| 7 天可观察首购会员数 | `eligible_first_buyer_cnt_7d` | bigint | 必须 | 标准商品层交易级复购过程计算 | 具备完整 7 天窗口的首购会员数 |
| 观察不足首购会员数 | `insufficient_observation_first_buyer_cnt` | bigint | 必须 | 标准商品层交易级复购过程计算 | 不进入正式分子分母 |
| 观察不足但已观察到复购会员数 | `insufficient_observation_observed_repeat_buyer_cnt_pre19` | bigint | 必须 | 标准商品层交易级复购过程计算 | 仅作诊断 |
| 7 天复购率原始值 | `repurchase_rate_7d_pre19_raw` | decimal(18,8) | 条件必须 | `repeat_buyer_cnt_7d_pre19 / eligible_first_buyer_cnt_7d` | 分母为 0 时 NULL |
| 7 天复购率 95% 下界 | `repurchase_rate_7d_pre19_lower_95` | decimal(18,8) | 条件必须 | 本算法第 13、17.4 节 Jeffreys 区间 | 正式评分使用下界 |
| 7 天复购率 95% 上界 | `repurchase_rate_7d_pre19_upper_95` | decimal(18,8) | 条件必须 | 本算法第 13、17.4 节 Jeffreys 区间 | 解释字段 |
| 复购计算状态 | `repurchase_calc_status` | varchar(64) | 必须 | 本算法第 9、17.4 节 | 见第 29.6 节状态约束 |
| 有效门店商品日数 | `available_store_day_cnt` | bigint | 条件必须 | `mart_sku_margin_loss` 运行级成员聚合 | 成员 SKU 实际收货后按标准商品 + 门店 + 日期去重 |
| 每有效门店商品日销售额 | `sales_per_available_store_day` | decimal(18,8) | 条件必须 | `product_sales_amt / available_store_day_cnt` | 贡献维度复算字段 |
| 非促销有效门店商品日数 | `non_promo_available_store_day_cnt` | bigint | 条件必须 | `valid_all_txn.discount_amt` + 实际收货过程数据 | 自然动销分母诊断 |
| 19:30 前销售标准量 | `pre1930_sales_standard_qty` | decimal(18,6) | 条件必须 | `valid_all_txn.sales_standard_qty` + 本算法第 14、17.4 节成员换算 | 全部有效标准商品门店日的 19:30 前销售标准量；销售深度分子 |
| 19:30 前非促销销售标准量 | `non_promo_pre1930_sales_standard_qty` | decimal(18,6) | 条件必须 | `valid_all_txn` + 本算法第 14、17.4 节成员换算 | 成员计量可统一时输出 |
| 实际收货标准量 | `actual_arrival_standard_qty` | decimal(18,6) | 条件必须 | `mart_sku_margin_loss.receipt_qty/receipt_weight_kg` + 成员换算 | 自然动销和吸收率分母 |
| 非促销实际收货标准量 | `non_promo_actual_arrival_standard_qty` | decimal(18,6) | 条件必须 | `mart_sku_margin_loss.receipt_qty/receipt_weight_kg` + 非促销有效门店商品日集合 + 成员换算 | 非促销售罄率分母；只汇总非促销有效日，不能使用全部有效日到货量替代 |
| 非促销 19:30 前售罄率 | `non_promo_pre1930_sell_through_rate` | decimal(18,8) | 条件必须 | `non_promo_pre1930_sales_standard_qty / non_promo_actual_arrival_standard_qty` | 自然动销维度复算字段 |
| 每有效门店商品日 19:30 前销售量 | `pre1930_sales_volume_per_available_store_day` | decimal(18,8) | 条件必须 | `pre1930_sales_standard_qty / available_store_day_cnt` | 自然动销维度复算字段 |
| 目标画像 19:30 前销售标准量 | `target_profile_pre1930_sales_standard_qty` | decimal(18,6) | 条件必须 | `valid_profiled_member_txn` + 本算法第 14、17.4 节 | 目标画像吸收率分子 |
| 目标画像 19:30 前吸收率 | `target_profile_pre1930_absorption_rate` | decimal(18,8) | 条件必须 | `target_profile_pre1930_sales_standard_qty / actual_arrival_standard_qty` | 自然动销解释与评分字段 |
| 促销识别方式 | `promotion_identify_method` | varchar(64) | 必须 | 本算法第 14、17.4 节标准商品层自然动销重算 | V1 固定为 `DISCOUNT_PROXY_V1` |
| 订购门店数 | `ordered_store_cnt` | bigint | 条件必须 | 本算法第 10.3、17.4 节标准商品成员门店日聚合 | 成员 SKU 订购后按标准商品和门店去重 |
| 允许订购门店数 | `eligible_orderable_store_cnt` | bigint | 条件必须 | 本算法第 10.3、17.4 节周期可订范围 | 与订购门店数使用同一周期 |
| 标准商品门店订购率 | `store_order_rate` | decimal(18,8) | 条件必须 | `ordered_store_cnt / eligible_orderable_store_cnt` | 仅作覆盖解释 |
| 订购门店日数 | `ordered_store_day_cnt` | bigint | 条件必须 | 本算法第 10.3、17.4 节 | 真实订购量大于 0 的去重门店日数 |
| 允许订购门店日数 | `eligible_orderable_store_day_cnt` | bigint | 条件必须 | 本算法第 10.3、17.4 节 | 同周期可订去重门店日数 |
| 标准商品门店订购日率 | `ordered_store_day_rate` | decimal(18,8) | 条件必须 | `ordered_store_day_cnt / eligible_orderable_store_day_cnt` | 仅作覆盖解释 |
| 订购覆盖状态 | `order_coverage_status` | varchar(64) | 必须 | 本算法第 10.4、17.4 节 | 见第 29.6 节状态约束 |
| 标准商品成本额 | `product_cost_amt` | decimal(18,6) | 条件必须 | 运行级日门店成员成本 + 本算法第 16.3、17.4 节 | 标准商品层目标画像成本金额 |
| 标准商品毛利额 | `product_margin_amt` | decimal(18,6) | 条件必须 | `product_sales_amt - product_cost_amt` | 标准商品层目标画像毛利额 |
| 标准商品毛利率 | `product_margin_rate` | decimal(18,8) | 条件必须 | `mart_target_profile_product_performance.product_margin_amt/product_sales_amt` | 标准商品层目标画像毛利率 |
| 标准商品总销售额 | `product_total_sales_amt` | decimal(18,6) | 必须 | `valid_all_txn` + 本算法第 29.3 节标准商品层聚合 | 标准商品层全量销售额 |
| 标准商品总成本额 | `product_total_cost_amt` | decimal(18,6) | 条件必须 | `product_total_sales_amt - product_total_margin_amt` | 标准商品层全量成本额 |
| 标准商品总毛利额 | `product_total_margin_amt` | decimal(18,6) | 必须 | `mart_sku_margin_loss.full_link_margin_amt` + 本算法第 29.3 节标准商品层聚合 | 标准商品层全量毛利额 |
| 标准商品总毛利率 | `product_total_margin_rate` | decimal(18,8) | 条件必须 | `product_total_margin_amt / product_total_sales_amt` | 毛利维度复算字段 |
| 成本来源 | `cost_source` | varchar(64) | 必须 | 本算法第 16.3、17.4 节 | 见第 29.6 节状态约束 |
| 成本分摊方法 | `cost_allocation_method` | varchar(64) | 必须 | 本算法第 16.3、17.4 节 | 见第 29.6 节状态约束 |
| 成本分摊状态 | `cost_allocation_status` | varchar(64) | 必须 | 本算法第 16.3、17.4 节 | 见第 29.6 节状态约束 |
| 标准商品画像贡献维度分 | `product_contribution_dimension_score` | decimal(18,8) | 条件必须 | 本算法第 29.3 节标准商品层 CRITIC 重算 | 标准商品层 CRITIC 贡献维度分 |
| 标准商品画像偏好维度分 | `product_preference_dimension_score` | decimal(18,8) | 条件必须 | 本算法第 29.3 节标准商品层 CRITIC 重算 | 标准商品层 CRITIC 偏好维度分；无参考画像写 NULL |
| 标准商品自然动销维度分 | `product_natural_sales_dimension_score` | decimal(18,8) | 条件必须 | 本算法第 29.3 节标准商品层 CRITIC 重算 | 标准商品层 CRITIC 自然动销维度分 |
| 标准商品毛利维度分 | `product_margin_dimension_score` | decimal(18,8) | 条件必须 | 本算法第 29.3 节标准商品层 CRITIC 重算 | 标准商品层 CRITIC 毛利维度分 |
| 标准商品维度权重 JSON | `product_dimension_weights_json` | json | 必须 | 本算法第 29.3 节标准商品层 CRITIC 参数 | JSON 对象；键为维度编码，值为权重 |
| 标准商品综合表现分 | `product_performance_score` | decimal(18,8) | 条件必须 | 本算法第 29.3 节标准商品层 CRITIC 重算 | 标准商品层综合表现分 |
| 标准商品点估计证据分 | `product_point_evidence_score` | decimal(18,8) | 条件必须 | 本算法第 13、17.4、29.3 节标准商品层统计重算 | 使用点估计计算的诊断分；不替代下界口径正式表现分 |
| 标准商品头部门店销售额 | `product_top1_store_sales_amt` | decimal(18,6) | 条件必须 | 交易级过程数据按标准商品 + 门店聚合 | 标准商品销售额最高门店的销售额；Top1 占比分子 |
| 标准商品头部门店销售占比 | `product_top1_store_sales_share` | decimal(18,8) | 条件必须 | `product_top1_store_sales_amt / product_total_sales_amt` | 销售额最高门店销售额 / 标准商品全量销售额；门店稳定性复算字段 |
| 标准商品门店销售 HHI | `product_store_sales_hhi` | decimal(18,8) | 条件必须 | 交易级过程数据按标准商品 + 门店聚合 | 各门店销售额占比平方和；门店稳定性复算字段 |
| 标准商品有效留一门店验证次数 | `product_valid_leave_one_store_test_cnt` | bigint | 必须 | 本算法第 25、17.4 节标准商品层留一门店重算 | 能完整重算标准商品层评分和分组的留一门店场景数；保持率分母 |
| 标准商品留一门店仍为锚点次数 | `product_leave_one_store_anchor_retained_cnt` | bigint | 必须 | 本算法第 25、17.4 节标准商品层留一门店重算 | 有效场景中仍满足正式锚点的次数；保持率分子 |
| 标准商品留一门店锚点保持率 | `product_leave_one_store_anchor_rate` | decimal(18,8) | 条件必须 | 本算法第 25、17.4 节留一门店重算 | 有效留一门店场景中仍满足正式锚点的场景占比 |
| 标准商品有效留一月验证次数 | `product_valid_leave_one_month_test_cnt` | bigint | 必须 | 本算法第 26、17.4 节标准商品层留一月重算 | 能完整重算标准商品层评分和分组的留一月场景数；保持率分母 |
| 标准商品留一月仍为锚点次数 | `product_leave_one_month_anchor_retained_cnt` | bigint | 必须 | 本算法第 26、17.4 节标准商品层留一月重算 | 有效场景中仍满足正式锚点的次数；保持率分子 |
| 标准商品留一月锚点保持率 | `product_leave_one_month_anchor_rate` | decimal(18,8) | 条件必须 | 本算法第 26、17.4 节留一月重算 | 有效留一月场景中仍满足正式锚点的场景占比 |
| 标准商品选中分组数量 | `product_selected_cluster_count` | int | 条件必须 | 本算法第 29.3 节标准商品层 Jenks/BIC 重算 | 可计算时为 1、2 或 3；K=1 时不产生正式高表现组；无法分组时写 NULL |
| 标准商品 Jenks 分割点 JSON | `product_jenks_breaks_json` | json | 必须 | 本算法第 29.3 节标准商品层 Jenks/BIC 重算 | JSON 数组；无分割点写 `[]` |
| 标准商品 SSE JSON | `product_sse_by_k_json` | json | 必须 | 本算法第 29.3 节标准商品层 Jenks/BIC 重算 | JSON 对象：`status` 见第 29.6 节，`values` 的键为字符串 K、值为 SSE decimal 或 JSON null |
| 标准商品 BIC JSON | `product_bic_by_k_json` | json | 必须 | 本算法第 29.3 节标准商品层 Jenks/BIC 重算 | JSON 对象：`status` 见第 29.6 节，`values` 的键为字符串 K、值为 BIC decimal 或 JSON null |
| 表现分组 | `performance_group` | varchar(64) | 必须 | 本算法第 29.3 节标准商品层 Jenks/BIC 重算 | 见第 29.6 节状态约束 |
| 是否正式锚点 | `is_formal_anchor` | tinyint | 必须 | 本算法第 23 章标准商品层锚点准入 | `1` 是正式锚点，`0` 不是 |
| 锚点生命周期状态 | `anchor_lifecycle_status` | varchar(64) | 必须 | 本算法第 24 章标准商品层当前/历史锚点 | 见第 29.6 节状态约束 |
| 锚点证据类型 | `anchor_evidence_type` | varchar(64) | 必须 | 本算法第 23-27 章标准商品层证据判定 | 见第 29.6 节状态约束 |
| 标准商品盈利状态 | `profitability_status` | varchar(64) | 必须 | 本算法第 29.3 节标准商品层毛利重算 | 目标画像和整体标准商品毛利底线状态 |
| 标准商品证据状态 | `evidence_status` | varchar(64) | 必须 | 本算法第 29.3 节标准商品层统计重算 | 标准商品层统计证据状态 |
| 标准商品自然动销状态 | `natural_sales_status` | varchar(64) | 必须 | 本算法第 29.3 节标准商品层自然动销重算 | 标准商品层自然动销窗口状态 |
| 标准商品门店稳定性状态 | `store_stability_status` | varchar(64) | 必须 | 本算法第 29.3 节标准商品层留一门店重算 | 标准商品层留一门店状态 |
| 标准商品时间稳定性状态 | `time_stability_status` | varchar(64) | 必须 | 本算法第 29.3 节标准商品层留一月重算 | 标准商品层留一月状态 |
| 标准商品拉动月份 JSON | `pull_months_json` | json | 条件必须 | 本算法第 29.3 节标准商品层留一月重算 | 标准商品层独立计算的 `YYYY-MM` 字符串数组；有效验证不足写 SQL `NULL` |
| 结果状态 | `result_status` | varchar(64) | 必须 | 本算法第 28 章结果状态设计 / 第 29.3 节标准商品层 | 见第 29.6 节状态约束 |
| 数据质量标记 JSON | `data_quality_flags` | json | 必须 | `mart_target_profile_sku_performance.data_quality_flags` + 本算法第 32 章标准商品层质量聚合 | JSON 数组；成员 SKU 质量标记去重汇总；无质量问题写 `[]` |
| 计算时间 | `calculated_at` | datetime | 必须 | 系统生成 | 结果写入时间 |

### 29.4 锚点汇总：`mart_target_profile_anchor_summary`

一行代表：一个周期、一个范围、一个门店群和一个消费者画像下的锚点汇总结果。

主键：

```text
algorithm_batch_version
+ performance_start_date
+ performance_end_date
+ scope_type
+ scope_id
+ category_granularity
+ category_code
+ store_group_type
+ final_level
+ final_profile
```

#### 29.4.1 锚点汇总 canonical 层与去重规则

锚点汇总不得把 SKU 表和标准商品表的锚点行直接相加。先生成唯一的 `canonical_anchor_set`，再填充本表的 JSON 和计数：

| 条件 | canonical 来源层 | canonical 实体键 | 代表字段 |
|---|---|---|---|
| `standard_product_mode = SPU_MAPPED` | `mart_target_profile_product_performance` | 本表业务主键 + `standard_product_key` | `representative_sku_id`；成员 SKU 仅用于追溯 |
| `standard_product_mode = SKU_ONLY` | `mart_target_profile_sku_performance` | 本表业务主键 + `standard_product_key`（等于 `sku_id`） | `sku_id` 作为 `representative_sku_id` |

执行规则：

```text
1. SPU_MAPPED 只从标准商品表现表取一行进入当前/历史/相对锚点 JSON；同一标准商品的 SKU 成员不再作为第二个锚点实体计数。
2. SKU_ONLY 只从 SKU 表取一行；同一 SKU 的标准商品回退行不再重复计数。
3. 每个 JSON 数组按 canonical 实体键去重；每项至少包含 standard_product_key、representative_sku_id、source_layer（只允许 `PRODUCT` 或 `SKU`），并在可用时包含 member_sku_list。
4. `formal_anchor_cnt` 和 `historical_anchor_cnt` 按 canonical 实体计数，不能把 SKU 表和标准商品表两个 `is_formal_anchor`/生命周期字段相加。
5. 低订购、时间敏感、门店集中和相对候选 JSON 也按 canonical 实体输出；SKU 级证据放在对象的 `evidence_sku_ids` 中，不改变 canonical 计数。
6. 标准商品成员状态未知、覆盖不足或快照不一致时，canonical 实体可保留 `DATA_INSUFFICIENT` 诊断行但不进入正式锚点 JSON/计数；成员映射或主键冲突直接阻断整批发布。
```

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 统一算法批次版本 | `algorithm_batch_version` | varchar(32) | 必须 | `mart_target_profile_sku_performance.algorithm_batch_version` | 固定为 `BATCH_YYYYMM`；与算法 01～03 同批，并进入本表唯一键 |
| 运行ID | `run_id` | varchar(64) | 必须 | 调度系统 | 本次结果所属算法 04 实际运行；同批原子发布的三张结果表和一张参数表使用同一 `run_id` |
| 重跑原因 | `rerun_reason` | varchar(512) | 条件必须 | 调度运行清单 | 同批次修正重跑时必填；首次运行可为 NULL |
| 更新时间 | `updated_at` | datetime | 必须 | 系统生成 | 本批本处理单元最近一次成功写入时间 |
| 数据周期开始日期 | `performance_start_date` | date | 必须 | 调度参数 | 统计周期开始日期 |
| 数据周期结束日期 | `performance_end_date` | date | 必须 | 调度参数 | 统计周期结束日期 |
| 范围类型 | `scope_type` | varchar(32) | 必须 | `dim_algorithm_batch_city_region_snapshot` | `CITY` / `CITY_CLUSTER` |
| 范围编码 | `scope_id` | varchar(64) | 必须 | `dim_algorithm_batch_city_region_snapshot.algorithm_region_code` | 城市或城市群编码 |
| 范围名称 | `scope_name` | varchar(128) | 必须 | `dim_algorithm_batch_city_region_snapshot.algorithm_region_name` | 城市或城市群名称 |
| 品类颗粒度 | `category_granularity` | varchar(32) | 必须 | `dim_sku` + 本算法品类颗粒度映射 | 大类 / 中类 / 小类 |
| 品类编码 | `category_code` | varchar(64) | 必须 | `dim_sku.category_level1_code/category_level2_code/category_level3_code` + 本算法品类颗粒度映射 | 当前计算品类编码 |
| 品类名称 | `category_name` | varchar(128) | 必须 | `dim_sku.category_level1_name/category_level2_name/category_level3_name` + 本算法品类颗粒度映射 | 当前计算品类名称 |
| 门店群类型 | `store_group_type` | varchar(32) | 必须 | `mart_store_category_level.final_level` + 本算法第 3.1 节范围分组 | `FINAL_LEVEL` / `ALL_RATED` |
| 门店品类等级 | `final_level` | varchar(32) | 必须 | `mart_store_category_level.final_level` | 当前门店群等级 |
| 消费者画像 | `final_profile` | varchar(128) | 必须 | `dim_customer_profile.final_profile` / `mart_store_group_consumer_contribution.final_profile` | 当前消费者画像 |
| 门店品类等级开始日期 | `category_level_start_date` | date | 必须 | `mart_store_category_level.calculation_start_date` | 算法 02 结果周期开始日期 |
| 门店品类等级结束日期 | `category_level_end_date` | date | 必须 | `mart_store_category_level.calculation_end_date` | 算法 02 结果周期结束日期 |
| 消费者贡献开始日期 | `consumer_contribution_start_date` | date | 必须 | `mart_store_group_consumer_contribution.contribution_start_date`（本卡别名） | 算法 03 结果周期开始日期 |
| 消费者贡献结束日期 | `consumer_contribution_end_date` | date | 必须 | `mart_store_group_consumer_contribution.contribution_end_date`（本卡别名） | 算法 03 结果周期结束日期 |
| 在售快照日期 | `listing_snapshot_date` | date | 必须 | SKU 表现表 / 标准商品表现表 | 锚点汇总所引用的当前可订可售快照日期 |
| 在售范围聚合方法 | `listing_scope_aggregation_method` | varchar(64) | 必须 | 调度参数 + 本算法第 10.1.1 节有效门店集合 | V1 固定 `ANY_ACTIVE_STORE`；用于解释当前/历史锚点判定 |
| 当前锚点 SKU JSON | `active_anchor_skus_json` | json | 必须 | `canonical_anchor_set`（由本算法第 29.4.1 节按 SKU/标准商品表现表生成） | JSON 数组；每项为 canonical 实体，至少含 `standard_product_key`、`representative_sku_id`、`source_layer`、`anchor_lifecycle_status`、`performance_score`；无结果写 `[]` |
| 历史锚点 SKU JSON | `historical_anchor_skus_json` | json | 必须 | `canonical_anchor_set` + 本算法第 29.4.1 节筛选 | JSON 数组；每项为 canonical 实体，至少含 `standard_product_key`、`representative_sku_id`、`source_layer`、`anchor_lifecycle_status`、`listing_status`；无结果写 `[]` |
| 低订购高表现 SKU JSON | `low_order_high_performance_skus_json` | json | 必须 | `canonical_anchor_set` + 本算法第 29.4.1 节筛选 | JSON 数组；每项至少含 canonical 实体键、`representative_sku_id`、`source_layer`、`store_order_rate`、`performance_score`；SKU 证据放 `evidence_sku_ids`；无结果写 `[]` |
| 时间敏感锚点 SKU JSON | `time_sensitive_anchor_skus_json` | json | 必须 | `canonical_anchor_set` + 本算法第 29.4.1 节筛选 | JSON 数组；每项至少含 canonical 实体键、`representative_sku_id`、`source_layer`、`time_stability_status`、`pull_months_json`；无结果写 `[]` |
| 门店集中锚点 SKU JSON | `store_concentrated_anchor_skus_json` | json | 必须 | `canonical_anchor_set` + 本算法第 29.4.1 节筛选 | JSON 数组；每项至少含 canonical 实体键、`representative_sku_id`、`source_layer`、`store_stability_status`；无结果写 `[]` |
| 相对锚点候选 JSON | `relative_anchor_candidates_json` | json | 必须 | `canonical_anchor_set` + 本算法第 29.4.1 节筛选 | JSON 数组；每项至少含 canonical 实体键、`representative_sku_id`、`source_layer`、`anchor_evidence_type`、`result_status`；无结果写 `[]` |
| 正式锚点数量 | `formal_anchor_cnt` | bigint | 必须 | `canonical_anchor_set` + 本算法第 29.4.1 节汇总 | canonical 实体中 `is_formal_anchor = 1` 的数量；同一 `standard_product_key` 只计 1 次 |
| 历史锚点数量 | `historical_anchor_cnt` | bigint | 必须 | `canonical_anchor_set` + 本算法第 29.4.1 节汇总 | canonical 实体中生命周期为 `HISTORICAL_ANCHOR` 的数量；同一 `standard_product_key` 只计 1 次 |
| 结果状态 | `result_status` | varchar(64) | 必须 | 本算法第 28 章结果状态设计 / 第 29.4 节锚点汇总 | 见第 29.6 节状态约束 |
| 质量指标 JSON | `quality_metrics_json` | json | 必须 | 本算法第 29.6.1 节 JSON 结构约束 + 第 32 章质量验收 | JSON 对象；固定键见第 29.6.1 节，覆盖 SKU、标准商品、canonical 实体、锚点计数和对账状态；无法计算的值写 JSON `null` |
| 数据质量标记 JSON | `data_quality_flags` | json | 必须 | `mart_target_profile_sku_performance.data_quality_flags` / `mart_target_profile_product_performance.data_quality_flags` + `canonical_anchor_set` + 本算法第 32 章汇总 | JSON 数组；汇总范围内质量标记去重后写入；无质量问题写 `[]` |
| 计算时间 | `calculated_at` | datetime | 必须 | 系统生成 | 结果写入时间 |

### 29.5 参数表：`mart_target_profile_sku_performance_params`

一行代表：一个统一算法批次、一个参数作用范围、一个评分层、一个计量作用域和一个动态参数。固定业务规则直接写在本算法卡正文，不重复落入参数表。

主键：

```text
algorithm_batch_version
+ parameter_scope_key
+ scoring_layer
+ param_group
+ metric_code
+ param_code
```

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 统一算法批次版本 | `algorithm_batch_version` | varchar(32) | 必须 | `调度运行清单` | 固定为 `BATCH_YYYYMM`；进入唯一键 |
| 运行ID | `run_id` | varchar(64) | 必须 | 调度系统 | 与同批三张正式结果表使用同一实际运行 ID |
| 重跑原因 | `rerun_reason` | varchar(512) | 条件必须 | 调度运行清单 | 同批修正重跑时必填；首次运行可为 NULL |
| 更新时间 | `updated_at` | datetime | 必须 | 系统生成 | 本批动态参数最近一次成功写入时间 |
| 参数作用范围键 | `parameter_scope_key` | varchar(512) | 必须 | 范围、品类、门店群、画像和周期键拼接 | 必须能唯一定位参数适用的计算单元 |
| 数据周期开始日期 | `performance_start_date` | date | 必须 | 调度参数 | 最近 3 个完整自然月开始日期 |
| 数据周期结束日期 | `performance_end_date` | date | 必须 | 调度参数 | 最近 3 个完整自然月结束日期 |
| 范围类型 | `scope_type` | varchar(32) | 必须 | `dim_algorithm_batch_city_region_snapshot.scope_type` | `CITY` / `CITY_CLUSTER` |
| 范围编码 | `scope_id` | varchar(64) | 必须 | `dim_algorithm_batch_city_region_snapshot.algorithm_region_code` | 城市或城市群编码 |
| 品类颗粒度 | `category_granularity` | varchar(32) | 必须 | 本算法第 3.3 节 | `LARGE` / `MIDDLE` / `SMALL` |
| 品类编码 | `category_code` | varchar(64) | 必须 | `dim_sku` 对应层级品类编码 | 当前参数适用的品类 |
| 门店群类型 | `store_group_type` | varchar(32) | 必须 | 本算法第 3.1 节 | `FINAL_LEVEL` / `ALL_RATED` |
| 门店品类等级 | `final_level` | varchar(32) | 必须 | `mart_store_category_level.final_level` + 本算法第 3.1 节 | A/B/C/D 或 ALL_RATED |
| 消费者画像 | `final_profile` | varchar(128) | 必须 | `mart_store_group_consumer_contribution.final_profile` | 当前参数适用的消费者画像 |
| 评分层 | `scoring_layer` | varchar(32) | 必须 | 本算法第 17.4、20-22 章 | `SKU` / `STANDARD_PRODUCT`；两层参数独立计算 |
| 参数计量作用域 | `parameter_measurement_scope` | varchar(32) | 必须 | 本算法第 11.2、19-22 章 | 金额、比例和毛利等跨计量指标写 `ALL`；销售量深度、到货量和售罄率等数量指标按 `WEIGHT` / `QUANTITY` / `PIECE_COUNT` / `VOLUME` 分开保存参数；无法换算的 `UNKNOWN` 不生成数量指标参数 |
| 门店品类等级开始日期 | `category_level_start_date` | date | 必须 | `mart_store_category_level.calculation_start_date` | 对应算法 02 周期开始 |
| 门店品类等级结束日期 | `category_level_end_date` | date | 必须 | `mart_store_category_level.calculation_end_date` | 对应算法 02 周期结束 |
| 消费者贡献开始日期 | `consumer_contribution_start_date` | date | 必须 | `mart_store_group_consumer_summary.contribution_start_date` | 对应算法 03 周期开始 |
| 消费者贡献结束日期 | `consumer_contribution_end_date` | date | 必须 | `mart_store_group_consumer_summary.contribution_end_date` | 对应算法 03 周期结束 |
| 参数分组 | `param_group` | varchar(64) | 必须 | 本算法第 20-22 章动态计算 | `ROBUST_STANDARDIZATION` / `CRITIC` / `JENKS_BIC` |
| 参数编码 | `param_code` | varchar(128) | 必须 | 本算法第 29.5 节参数编码规则 | 参数唯一编码；允许值见下表 |
| 参数名称 | `param_name` | varchar(256) | 必须 | 本算法第 29.5 节参数字典 | 参数中文名称 |
| 指标编码 | `metric_code` | varchar(128) | 必须 | 本算法第 19-22 章指标定义 | 指标级参数写指标或维度编码；矩阵和分组整体参数固定写 `__GROUP__`；进入唯一键 |
| 参数数值 | `param_value_decimal` | decimal(18,8) | 条件必须 | 本算法第 20-22 章参数计算 | 数值型动态参数；非数值参数写 NULL |
| 参数文本值 | `param_value_text` | varchar(512) | 条件必须 | 本算法第 20-22 章参数计算 | 方法名等文本参数；不适用写 NULL |
| 参数 JSON 值 | `param_value_json` | json | 条件必须 | 本算法第 20-22 章参数计算 | 矩阵、断点或按 K 指标；不适用写 SQL NULL |
| 样本数 | `sample_cnt` | bigint | 必须 | 本算法第 20-22 章实际样本集合 | 该参数计算使用的实体数 |
| 是否回退 | `fallback_flag` | tinyint | 必须 | 本算法第 20.3、21.4 节 | `1` 使用已定义回退，`0` 未回退 |
| 回退原因 | `fallback_reason` | varchar(512) | 条件必须 | 本算法第 20.3、21.4 节 | `fallback_flag = 1` 时必填；否则 NULL |
| 关联算法步骤 | `algorithm_step` | varchar(128) | 必须 | 本算法第 20-22 章 | `ROBUST_STANDARDIZATION` / `CRITIC_WEIGHTING` / `JENKS_BIC_GROUPING` |
| 计算时间 | `calculated_at` | datetime | 必须 | 系统生成 | 参数写入时间 |

`parameter_scope_key` 固定按以下字段顺序用 `|` 拼接，字段值本身不得包含 `|`：

```text
performance_start_date|performance_end_date|scope_type|scope_id|category_granularity|category_code|store_group_type|final_level|final_profile|parameter_measurement_scope
```

每行 `param_value_decimal`、`param_value_text`、`param_value_json` 必须且只能有一个非 NULL；同一主键不得重复。

动态参数编码闭集如下。`JENKS_BIC` 同时保存综合表现分组和订购覆盖分组使用的动态参数，通过 `metric_code` 区分 `PERFORMANCE_SCORE` 与 `STORE_ORDER_RATE`；不得只保存最终状态而丢失订购覆盖断点。

| 参数分组 | 参数编码 | 值字段 | 内容 |
|---|---|---|---|
| `ROBUST_STANDARDIZATION` | `MEDIAN` | `param_value_decimal` | 当前评分层、当前作用范围、当前指标的中位数 |
| `ROBUST_STANDARDIZATION` | `SCALE_METHOD` | `param_value_text` | `MAD` 或卡内已定义的回退方法 |
| `ROBUST_STANDARDIZATION` | `SCALE_VALUE` | `param_value_decimal` | 当前指标的 MAD 或回退尺度值 |
| `CRITIC` | `METRIC_WEIGHT` | `param_value_decimal` | 维度内指标权重 |
| `CRITIC` | `DIMENSION_WEIGHT` | `param_value_decimal` | 四个一级维度的层间权重 |
| `CRITIC` | `CORRELATION_MATRIX` | `param_value_json` | `metric_code = __GROUP__`；指标编码为行列键、相关系数为值的方阵 |
| `JENKS_BIC` | `SELECTED_K` | `param_value_decimal` | 综合表现分组时 `metric_code = PERFORMANCE_SCORE`、K 为 1/2/3；订购覆盖分组时 `metric_code = STORE_ORDER_RATE`、K 为 1/2 |
| `JENKS_BIC` | `BREAKS` | `param_value_json` | `metric_code = PERFORMANCE_SCORE / STORE_ORDER_RATE`；升序分割点数组，K=1 时写 `[]` |
| `JENKS_BIC` | `SSE_BY_K` | `param_value_json` | `metric_code = PERFORMANCE_SCORE / STORE_ORDER_RATE`；对象键覆盖对应候选 K，值为 SSE 或 JSON null |
| `JENKS_BIC` | `BIC_BY_K` | `param_value_json` | `metric_code = PERFORMANCE_SCORE / STORE_ORDER_RATE`；对象键覆盖对应候选 K，值为 BIC 或 JSON null |

同一批次重跑必须读取该批已发布动态参数并复用；若原批从未成功发布，首次成功运行计算并随结果原子写入。不得借重跑改变中位数、尺度、权重、K 或断点。

### 29.5.1 自行验收和原子发布

算法 04 先在运行级暂存对象完成计算，再按批次自行验收：

```text
1. 上游四张正式表、共享城市区域快照和基础输入均按同一 algorithm_batch_version / 周期完整交付。
2. 输入主键、商品映射、城市区域映射和标准商品成员映射唯一。
3. 算法 03 汇总表与贡献明细双向一致；汇总为 NOT_CALCULABLE 的门店群视为正常排除项，贡献明细必须为 0 行。
4. 三张正式结果表和动态参数表的主键唯一、状态取值合法、JSON 结构合法。
5. 所有比率可由分子分母复算；SKU 层、标准商品层的 CRITIC、Jenks/BIC 和稳定性参数能与参数表双向复算。
6. 应处理对象与实际结果双向核对：有合法画像但无合法 SKU 的组只允许一条 NO_VALID_SKU 锚点汇总；不得伪造 SKU 或标准商品行。
7. 销售额、会员数、门店数、标准商品成员和 canonical 锚点计数通过第 6、17、29.4、32 章对账。
```

全部通过后，以同一 `run_id` 原子发布三张正式结果表和一张动态参数表；任一项失败均不写入或覆盖该批正式结果，由平台现有任务状态、数据质量记录和输入血缘保存失败原因。下游只在平台标记算法 04 该批成功后启动。

同一批次失败重跑沿用原 `algorithm_batch_version`、城市区域快照、`listing_snapshot_date` 和已发布动态参数，只更新实际运行 `run_id`、时间及重跑原因。已有可靠正式结果在失败重跑期间保持不变。

### 29.6 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `listing_scope_aggregation_method` | 在售范围聚合方法 | `ANY_ACTIVE_STORE` | 任一有效门店可订可售 | V1 固定规则，且有效门店与状态覆盖完整 |
| `scope_type` | 范围类型 | `CITY` | 单城市 | 当前结果按单个城市计算 |
| `scope_type` | 范围类型 | `CITY_CLUSTER` | 城市群 | 当前结果按城市算法区域或城市群计算 |
| `category_granularity` | 品类颗粒度 | `LARGE` | 大类 | 当前结果按商品一级分类聚合 |
| `category_granularity` | 品类颗粒度 | `MIDDLE` | 中类 | 当前结果按商品二级分类聚合 |
| `category_granularity` | 品类颗粒度 | `SMALL` | 小类 | 当前结果按商品三级分类聚合 |
| `store_group_type` | 门店群类型 | `FINAL_LEVEL` | 分等级门店群 | 按算法 02 输出的门店品类等级分组 |
| `store_group_type` | 门店群类型 | `ALL_RATED` | 全部有等级门店 | 当前品类下所有已评级门店合并计算 |
| `final_level` | 门店等级 | `A` | A 级门店 | 算法 02 输出的 A 级门店群 |
| `final_level` | 门店等级 | `B` | B 级门店 | 算法 02 输出的 B 级门店群 |
| `final_level` | 门店等级 | `C` | C 级门店 | 算法 02 输出的 C 级门店群 |
| `final_level` | 门店等级 | `D` | D 级门店 | 算法 02 输出的 D 级门店群 |
| `final_level` | 门店等级 | `ALL_RATED` | 全部已评级门店 | `store_group_type = ALL_RATED` 时使用 |
| `is_main_profile` | 是否主力画像 | `1` | 主力画像 | 算法 03 判断该画像为当前门店群主力消费者画像 |
| `is_main_profile` | 是否主力画像 | `0` | 非主力画像 | 算法 03 判断该画像不是当前门店群主力消费者画像 |
| `is_relative_main_candidate` | 是否相对主力候选 | `1` | 相对主力候选 | 算法 03 在 `NO_OBVIOUS_MAIN` 场景下标记最高贡献候选 |
| `is_relative_main_candidate` | 是否相对主力候选 | `0` | 非相对主力候选 | 不属于相对主力候选 |
| `measurement_type` | 计量类型 | `WEIGHT` | 重量计价 | 商品销售单位可稳定换算为重量口径 |
| `measurement_type` | 计量类型 | `QUANTITY` | 非重量数量计价 | 商品按件、份、盒、包、袋、瓶、个、只等数量单位计价 |
| `measurement_type` | 计量类型 | `PIECE_COUNT` | 枚数计价 | 商品按枚数计价，例如蛋品 |
| `measurement_type` | 计量类型 | `VOLUME` | 容量计价 | 商品按 L、ml 等容量单位计价 |
| `measurement_type` | 计量类型 | `UNKNOWN` | 未知计量类型 | 商品销售单位无法被 V1 单位规则识别 |
| `is_formal_anchor` | 是否正式锚点 | `1` | 正式锚点 | SKU 或标准商品满足正式锚点准入 |
| `is_formal_anchor` | 是否正式锚点 | `0` | 非正式锚点 | SKU 或标准商品未满足正式锚点准入 |
| `repurchase_calc_status` | 复购计算状态 | `OK` | 复购计算成功 | 可观察首购会员数大于 0；观察不足会员另作诊断，不影响可观察会员计算 |
| `repurchase_calc_status` | 复购计算状态 | `DENOMINATOR_ZERO` | 复购分母为 0 | 可观察首购会员数为 0 且观察不足首购会员数也为 0 |
| `repurchase_calc_status` | 复购计算状态 | `INSUFFICIENT_WINDOW` | 观察窗口不足 | 可观察首购会员数为 0 且观察不足首购会员数大于 0 |
| `valid_transaction_filter_method` | 有效交易过滤方式 | `SOURCE_TABLE_CLEANED` | 源表已清洗 | 数据开发确认 Doris 主表已保留有效正向销售 |
| `valid_transaction_filter_method` | 有效交易过滤方式 | `RULE_FILTERED` | 算法任务内过滤 | 算法 04 按 `order_status`、`is_return`、`usual_amt`、`weight` 等字段过滤 |
| `standard_product_mode` | 标准商品模式 | `SPU_MAPPED` | 已按 SPU 归并 | 商品基础表有有效 `spu_id` |
| `standard_product_mode` | 标准商品模式 | `SKU_ONLY` | 只按销售 SKU 计算 | `spu_id` 为空或无法稳定映射 |
| `orderable_sellable_flag` | 是否可订可售 | `1` | 当前范围快照可订且可售 | SKU 层按第 10.1 节、标准商品层按第 29.3 节完成有效门店/成员覆盖校验后判定为可订可售 |
| `orderable_sellable_flag` | 是否可订可售 | `0` | 当前范围快照已确认不可订或不可售 | 状态覆盖完整，按已确认的门店群及标准商品成员合成方法判定条件不成立 |
| `orderable_sellable_flag` | 是否可订可售 | `NULL` | 在售状态不可判断 | 候选/有效门店覆盖不足、无有效状态行、快照不一致或成员状态未知；同时写 `DATA_INSUFFICIENT`，不进入正式锚点 |
| `listing_status` | 在售状态 | `ACTIVE` | 当前范围内可订可售 | SKU 层按第 10.1 节、标准商品层按第 29.3 节判定为 `orderable_sellable_flag = 1` |
| `listing_status` | 在售状态 | `INACTIVE` | 当前范围内不可订或不可售 | 状态覆盖完整，按已确认的门店群及标准商品成员合成方法判定 `orderable_sellable_flag = 0` |
| `listing_status` | 在售状态 | `NULL` | 在售状态不可判断 | 候选/有效门店覆盖不足、无有效状态行、快照不一致或成员状态未知；同时写 `DATA_INSUFFICIENT`，不进入正式锚点，也不得转成 `HISTORICAL_ANCHOR` |
| `orderable_scope` | 订购范围口径 | `STORE_SKU_ORDERABLE` | 门店 SKU 可订范围 | 仅在可订可售表按合同稳定交付并通过覆盖验收后使用 |
| `orderable_scope` | 订购范围口径 | `NULL` | 订购范围不可判断 | 门店级可订范围缺失或字段不完整；同时将订购覆盖字段写 `NULL + DATA_INSUFFICIENT` |
| `measurement_mapping_status` | 计量映射状态 | `MAPPED` | 计量单位可识别 | 商品基础表单位可映射到重量或数量 |
| `measurement_mapping_status` | 计量映射状态 | `UNKNOWN` | 计量单位未知 | 商品基础表单位缺失或无法识别 |
| `measurement_mapping_status` | 计量映射状态 | `UNIT_CONVERSION_ERROR` | 单位换算异常 | 单位重量或换算系数缺失且指标必须换算 |
| `cost_source` | 成本来源 | `FULL_CHAIN_MARGIN_DERIVED_COST` | 全链路毛利反推成本 | 使用毛利损耗表销售额和全链路毛利额反推成本 |
| `cost_source` | 成本来源 | `ARRIVAL_COST_TAX_INCLUDED` | 出库到店含税成本 | 全链路毛利口径无法稳定取数时，使用门店商品日价格表出库到店成本含税作为备选 |
| `cost_source` | 成本来源 | `SOURCE_MISSING` | 成本来源缺失 | 全链路毛利反推和完整价格键备选成本均不可用 |
| `cost_source` | 成本来源 | `SOURCE_CONFLICT` | 成本来源冲突 | 完整物理主键唯一，但同一日期、门店、销售 SKU 对应多个不同有效单位成本，不能折叠到销售 SKU 口径 |
| `cost_allocation_method` | 成本分摊方法 | `UNIT_COST_BY_STANDARD_QTY` | 按销售标准量单位成本分摊 | V1 默认口径，`weight` 作为销售标准量 |
| `cost_allocation_method` | 成本分摊方法 | `NOT_ALLOCATED` | 未分摊 | 成本缺失或标准销售量不可用，正式毛利字段写 NULL |
| `cost_allocation_status` | 成本分摊状态 | `COST_ALLOCATED_V1` | 成本分摊成功 | 销售标准量和成本分母均有效，使用默认单位成本口径 |
| `cost_allocation_status` | 成本分摊状态 | `COST_NOT_ALLOCATED` | 成本未分摊 | 成本来源有效且分母非 0，但计量映射或目标画像标准销售量无法可靠换算；V1 禁止销售额占比分摊进入正式结果 |
| `cost_allocation_status` | 成本分摊状态 | `SOURCE_MISSING` | 成本分摊来源缺失 | 两个成本来源都没有有效值 |
| `cost_allocation_status` | 成本分摊状态 | `SOURCE_CONFLICT` | 成本分摊来源冲突 | 备选成本在完整主键唯一后仍有多个不同单位成本，不能选取或平均 |
| `cost_allocation_status` | 成本分摊状态 | `ZERO_DENOMINATOR` | 成本分摊分母为 0 | 该日门店 SKU 总销售标准量为 0 |
| `promotion_identify_method` | 促销识别方式 | `DISCOUNT_PROXY_V1` | 折扣代理口径 | V1 无促销活动表，使用 `discount_amt > 0` 识别促销代理 |
| `preference_reference_status` | 偏好参考组状态 | `HAS_REFERENCE_PROFILE` | 有参考画像 | 同一比较组内存在非目标画像有效消费 |
| `preference_reference_status` | 偏好参考组状态 | `NO_REFERENCE_PROFILE` | 没有参考画像 | 同一比较组只有目标画像；对应原始业务规则的 `NO_REFERENCE_PROFILE`，偏好指数不适用 |
| `result_status` | 结果状态 | `SUCCESS` | 计算成功 | 当前比较组正常产出结果 |
| `result_status` | 结果状态 | `SINGLE_SKU` | 只有一个可计算实体 | 当前结果层只有 1 个可计算实体：SKU 表按 SKU、标准商品表按 standard_product_key、汇总表按 canonical 实体判断；沿用业务原文枚举名 |
| `result_status` | 结果状态 | `NO_OBVIOUS_HIGH_SKU` | 无明显高表现 SKU | Jenks/BIC 未形成高表现组 |
| `result_status` | 结果状态 | `NO_VALID_SKU` | 无有效 SKU | 商品主数据和交易有效性过滤后无合法 SKU；当前不在售商品仍可保留为历史证据 |
| `result_status` | 结果状态 | `DATA_INCOMPLETE` | 数据不完整 | 核心输入缺失但可保留诊断 |
| `result_status` | 结果状态 | `NOT_CALCULABLE` | 合法业务单元不可计算 | 已有合法画像与业务键，但所有核心业务分母均不可用；上游交付失败不写正式结果行 |
| `profitability_status` | 盈利状态 | `POSITIVE_MARGIN` | 毛利为正 | 当前 SKU 或标准商品的目标画像毛利额与整体毛利额均大于 0 |
| `profitability_status` | 盈利状态 | `NON_POSITIVE_MARGIN` | 毛利非正 | 当前 SKU 或标准商品的目标画像毛利额、整体毛利额任一小于等于 0 |
| `profitability_status` | 盈利状态 | `COST_SOURCE_MISSING` | 成本来源缺失 | 当前 SKU 或标准商品的目标画像成本无法可靠计算 |
| `profitability_status` | 盈利状态 | `COST_SOURCE_CONFLICT` | 成本来源冲突 | 当前 SKU 或标准商品命中多个不同有效单位成本，不能可靠计算目标画像成本 |
| `profitability_status` | 盈利状态 | `COST_NOT_CALCULABLE` | 成本无法计算 | 成本来源有效，但成本分摊分母、计量映射或目标画像标准销售量不能可靠用于分摊 |
| `evidence_status` | 证据状态 | `SUFFICIENT` | 证据充分 | 渗透、复购、偏好等样本达到正式评分要求 |
| `evidence_status` | 证据状态 | `LOW_EVIDENCE` | 低证据 | 小样本或区间下界不足，不能作为正式锚点 |
| `evidence_status` | 证据状态 | `DATA_INSUFFICIENT` | 证据数据不完整 | 渗透、复购或偏好所需源字段缺失，结果保留诊断但不能成为正式锚点 |
| `time_stability_status` | 时间稳定性状态 | `STABLE` | 时间稳定 | 留一月验证仍保持锚点或高表现 |
| `time_stability_status` | 时间稳定性状态 | `TIME_SENSITIVE` | 时间敏感 | 只在特定月份或时段表现突出 |
| `time_stability_status` | 时间稳定性状态 | `INSUFFICIENT_TIME_SAMPLE` | 时间样本不足 | 有效月份不足以做稳定性验证 |
| `store_stability_status` | 门店稳定性状态 | `STABLE` | 门店稳定 | 留一门店验证仍保持锚点或高表现 |
| `store_stability_status` | 门店稳定性状态 | `STORE_CONCENTRATED` | 门店集中 | 表现集中在少数门店 |
| `store_stability_status` | 门店稳定性状态 | `INSUFFICIENT_STORE_SAMPLE` | 门店样本不足 | 有效门店不足以做稳定性验证 |
| `natural_sales_status` | 自然动销状态 | `VALID` | 自然动销有效 | 存在可计算的 19:30 前非促销自然动销窗口 |
| `natural_sales_status` | 自然动销状态 | `NO_NATURAL_SALES_WINDOW` | 无自然销售窗口 | 全部销售依赖促销代理或时段折扣 |
| `natural_sales_status` | 自然动销状态 | `DATA_INSUFFICIENT` | 自然动销数据不完整 | 收货量、单位换算或有效门店商品日不足，无法复算自然动销 |
| `order_coverage_status` | 订购覆盖状态 | `HIGH` | 订购覆盖高 | 订购覆盖位于高覆盖组 |
| `order_coverage_status` | 订购覆盖状态 | `LOW` | 订购覆盖低 | 订购覆盖低但表现可单独解释 |
| `order_coverage_status` | 订购覆盖状态 | `NO_OBVIOUS_SPLIT` | 无明显分组 | 订购覆盖未形成明显高低分组 |
| `order_coverage_status` | 订购覆盖状态 | `DATA_INSUFFICIENT` | 订购覆盖不可计算 | 没有商品计量类型对应的真实 `order_qty` 或 `order_weight_kg`，或没有可订范围字段 |
| `attribute_status` | 属性状态 | `COMPLETE` | V1 属性字段齐备 | `specification`、`unit_weight_kg`、`temperature_layer`、`brand_name` 均有值；不代表主材料、口味和形态齐备 |
| `attribute_status` | 属性状态 | `ATTRIBUTE_INCOMPLETE` | V1 属性字段不全 | 上述任一字段缺失，不阻断经营表现计算 |
| `attribute_source_json` | 属性来源 JSON | 对象值 `MASTER_DATA` / `UNKNOWN` | V1 属性来源闭集 | 固定键为 `specification`、`sale_unit`、`unit_weight_kg`、`temperature_layer`、`brand_name`；字段有值写 `MASTER_DATA`，否则写 `UNKNOWN` |
| `attribute_confidence_json` | 属性置信度 JSON | 对象值 JSON `null` | V1 属性识别置信度未提供 | 键与 `attribute_source_json` 一致；当前均写 JSON `null`，不把主数据有值推断为识别准确率 |
| `data_quality_flags` | 数据质量标记 JSON | 数组值 `PRICE_SOURCE_MISSING` / `PRICE_SOURCE_CONFLICT` / `UNIT_CONVERSION_ERROR` / `DATA_INSUFFICIENT` | 数据质量问题集合 | 无问题写 `[]`；原价存在多个有效值，或完整物理主键唯一但同一销售 SKU 折叠前存在多个不同单位成本时写 `PRICE_SOURCE_CONFLICT`；不得用自由中文替代稳定英文标记 |
| `sse_by_k_json.status` / `bic_by_k_json.status` / `product_sse_by_k_json.status` / `product_bic_by_k_json.status` | 分组参数 JSON 状态 | `CALCULATED` | 已计算 | 至少有一个有效消费者类型且对应 K 值按第 22 章完成计算 |
| `sse_by_k_json.status` / `bic_by_k_json.status` / `product_sse_by_k_json.status` / `product_bic_by_k_json.status` | 分组参数 JSON 状态 | `NOT_APPLICABLE` | 不适用 | 单一有效类型或本结果不需要运行 Jenks/BIC；K 值写 `null` |
| `sse_by_k_json.status` / `bic_by_k_json.status` / `product_sse_by_k_json.status` / `product_bic_by_k_json.status` | 分组参数 JSON 状态 | `NOT_CALCULABLE` | 无法计算 | 合法业务实体的核心分母均不可用；`values` 对应 K 写 JSON null，不伪造参数；上游失败不发布正式 JSON |
| `performance_group` | 表现分组 | `HIGH_PERFORMANCE` | 高表现组 | Jenks/BIC 判定为高表现 |
| `performance_group` | 表现分组 | `MIDDLE_PERFORMANCE` | 中表现组 | Jenks/BIC 判定为中表现 |
| `performance_group` | 表现分组 | `LOW_PERFORMANCE` | 低表现组 | Jenks/BIC 判定为低表现 |
| `performance_group` | 表现分组 | `NO_OBVIOUS_HIGH_SKU` | 无明显高表现 | 未形成可发布高表现组 |
| `anchor_lifecycle_status` | 锚点生命周期状态 | `ACTIVE_ANCHOR` | 当前锚点 | 当前可订可售且通过正式锚点准入 |
| `anchor_lifecycle_status` | 锚点生命周期状态 | `HISTORICAL_ANCHOR` | 历史锚点 | 贡献周期内表现较好且 `listing_status = INACTIVE`（已确认当前不可订或不可售）；`NULL` 不得转成历史锚点 |
| `anchor_lifecycle_status` | 锚点生命周期状态 | `NOT_ANCHOR` | 非锚点 | 未通过正式锚点准入且不属于历史锚点 |
| `anchor_evidence_type` | 锚点证据类型 | `ACTIVE_STABLE_ANCHOR` | 当前稳定锚点 | 当前可订可售、证据充分且稳定 |
| `anchor_evidence_type` | 锚点证据类型 | `LOW_ORDER_HIGH_PERFORMANCE` | 低订购高表现 | 订购覆盖低但实际表现高 |
| `anchor_evidence_type` | 锚点证据类型 | `TIME_SENSITIVE_ANCHOR` | 时间敏感锚点 | 只在特定月份或时段表现突出 |
| `anchor_evidence_type` | 锚点证据类型 | `STORE_CONCENTRATED_ANCHOR` | 门店集中锚点 | 表现集中在少数门店 |
| `anchor_evidence_type` | 锚点证据类型 | `RELATIVE_ANCHOR_CANDIDATE` | 相对锚点候选 | 小样本或双 SKU 场景下的相对候选 |
| `anchor_evidence_type` | 锚点证据类型 | `NOT_ANCHOR` | 非锚点 | 未通过锚点准入 |
| `standard_product_listing_method` | 标准商品成员在售方法 | `ANY_ACTIVE_MEMBER` | 任一成员在售 | 成员覆盖和快照完整时，任一成员 ACTIVE 则标准商品 ACTIVE |
| `scoring_layer` | 评分层 | `SKU` | SKU 评分层 | 参数用于销售 SKU 层复算 |
| `scoring_layer` | 评分层 | `STANDARD_PRODUCT` | 标准商品评分层 | 参数用于标准商品层独立复算 |
| `parameter_measurement_scope` | 参数计量作用域 | `ALL` | 不区分计量类型 | 金额、比例、毛利及分组整体参数使用 |
| `parameter_measurement_scope` | 参数计量作用域 | `WEIGHT` / `QUANTITY` / `PIECE_COUNT` / `VOLUME` | 按可换算计量类型分组 | 数量、到货和售罄相关指标只在相同计量类型内标准化或赋权；`UNKNOWN` 不生成数量指标参数 |
| `fallback_flag` | 是否回退 | `0` / `1` | 参数是否使用回退 | 参数表中 `1` 表示该参数因样本不足、MAD 为 0 等已定义原因使用回退口径 |
| `param_group` | 参数分组 | `ROBUST_STANDARDIZATION` | 稳健标准化参数 | 中位数、尺度方法和尺度值 |
| `param_group` | 参数分组 | `CRITIC` | CRITIC 参数 | 维度内或维度间动态权重、相关矩阵 |
| `param_group` | 参数分组 | `JENKS_BIC` | Jenks/BIC 参数 | 动态分组、断点、SSE 和 BIC |
| `algorithm_step` | 关联算法步骤 | `ROBUST_STANDARDIZATION` | 稳健标准化 | 中位数、尺度方法和尺度值参数 |
| `algorithm_step` | 关联算法步骤 | `CRITIC_WEIGHTING` | CRITIC 赋权 | 指标/维度权重和相关矩阵参数 |
| `algorithm_step` | 关联算法步骤 | `JENKS_BIC_GROUPING` | Jenks/BIC 分组 | K、断点、SSE 和 BIC 参数 |
| `product_status_availability` | 商品状态可用性 | `AVAILABLE` | 商品状态可用 | `dim_product_status` 在当前区域和快照提供有效记录 |
| `product_status_availability` | 商品状态可用性 | `NOT_AVAILABLE` | 商品状态不可用 | V1 缺失、冲突或未接入状态资产 |
| `product_status_code` | 商品状态编码 | `A` | 全年品 | `dim_product_status` 标记为全年品 |
| `product_status_code` | 商品状态编码 | `O` | 试卖品 | `dim_product_status` 标记为试卖品 |
| `product_status_code` | 商品状态编码 | `S` | 季节品 | `dim_product_status` 标记为季节品 |
| `product_status_code` | 商品状态编码 | `D` | 淘汰品 | `dim_product_status` 标记为淘汰品 |
| `product_status_code` | 商品状态编码 | `B` | 备选品 | `dim_product_status` 标记为备选品 |

### 29.6.1 `quality_metrics_json` 结构约束

`mart_target_profile_anchor_summary.quality_metrics_json` 必须是 JSON 对象，固定包含：

```text
sku_cnt
valid_sku_cnt
standard_product_cnt
valid_standard_product_cnt
canonical_entity_cnt
formal_anchor_cnt
historical_anchor_cnt
reconciliation_status
missing_field_cnt
```

| JSON 键 | 类型 | 计算规则 |
|---|---|---|
| `sku_cnt` | integer | 当前汇总键实际输出的 SKU 明细行数 |
| `valid_sku_cnt` | integer | SKU 层通过核心字段完整性门、可进入本层比较的实体数；小样本回退实体仍计入 |
| `standard_product_cnt` | integer | 当前汇总键实际输出的标准商品明细行数 |
| `valid_standard_product_cnt` | integer | 标准商品层通过核心字段完整性门、可进入本层比较的实体数；小样本回退实体仍计入 |
| `canonical_entity_cnt` | integer | 第 29.4.1 节去重后的 canonical 实体数 |
| `formal_anchor_cnt` | integer | canonical 实体中 `is_formal_anchor = 1` 的数量；必须与汇总字段一致 |
| `historical_anchor_cnt` | integer | canonical 实体中生命周期为 `HISTORICAL_ANCHOR` 的数量；必须与汇总字段一致 |
| `missing_field_cnt` | integer | 当前汇总键内所有正式实体的 `实体主键 + 字段名` 缺失实例去重计数；只统计字段合同中“必须/条件必须”且当前条件已触发的字段 |
| `reconciliation_status` | string | 允许值见下表 |

已发布正式汇总中的 `reconciliation_status` 只允许以下取值；对账失败会阻断整批，因此不会生成 `FAILED` 正式值：

| JSON 键 | 允许取值 | 含义 | 触发条件 |
|---|---|---|---|
| `reconciliation_status` | `PASS` | 对账通过 | 画像层金额按 2 位小数比较且绝对差不超过 0.01 元；其他层按各自已登记容差通过 |
| `reconciliation_status` | `NOT_CALCULABLE` | 无法对账 | 合法业务单元的必要分母不可得；上游交付失败直接阻断整批，不写正式汇总 |

单个指标无法计算时，该键的值写 JSON `null`；整个汇总没有可计算指标时仍保留上述固定键、数值写 JSON `null`、`reconciliation_status` 写 `NOT_CALCULABLE`，不能改成 `{}`、`0`、空字符串或自由中文。

### 29.6.2 嵌套 JSON 枚举约束

正式输出表中的嵌套 JSON 枚举必须按以下闭集写入，不能让开发自行扩展英文取值：

| JSON 路径 | 类型 | 允许取值 | 中文含义与来源 | 缺失写法 |
|---|---|---|---|---|
| `active_anchor_skus_json[*].source_layer`、`historical_anchor_skus_json[*].source_layer`、`low_order_high_performance_skus_json[*].source_layer`、`time_sensitive_anchor_skus_json[*].source_layer`、`store_concentrated_anchor_skus_json[*].source_layer`、`relative_anchor_candidates_json[*].source_layer` | string | `PRODUCT` | canonical 实体来自 `mart_target_profile_product_performance`；仅当 `standard_product_mode = SPU_MAPPED` 使用 | 无结果时数组写 `[]`；诊断实体不进入正式 JSON |
| 同上 | string | `SKU` | canonical 实体来自 `mart_target_profile_sku_performance`；仅当 `standard_product_mode = SKU_ONLY` 使用 | 同上 |
| 各锚点 JSON 的 `performance_score` | number 或 `null` | `product_performance_score` / `sku_performance_score` | 按 `source_layer` 取对应层的正式表现分 | 来源层对应表现分不可计算时写 JSON `null`，不写 0 |
| 各锚点 JSON 的 `member_sku_list` / `evidence_sku_ids` | string 数组 | 销售 SKU 编码 | 分别表示标准商品成员和 SKU 级证据 | 无成员或无 SKU 级证据时写 `[]`；不得填入标准商品名称或重复编码 |
| `time_sensitive_anchor_skus_json[*].pull_months_json` | string 数组 | `YYYY-MM` | 第 26 章有效留一月验证确定的拉动月份，按月升序去重 | 有效验证不足的实体不得进入时间敏感锚点 JSON；无拉动月写 `[]` |
| `before_after_promotion_price.price_source` | string | `PRICE_TABLE_ORIGINAL_DORIS_USUAL_AMT_PER_WEIGHT` | `before_price` 来自 `mart_store_sku_daily_price.original_sale_price`；`after_price` 来自有效 Doris 交易 `usual_amt / weight` 的成交单价 | 任一来源缺失、价格分母无效或无法关联时，整个 `before_after_promotion_price` 写 JSON `null`，并在 `data_quality_flags` 写 `PRICE_SOURCE_MISSING` |

---

## 30. 产品端应用边界

产品默认按同一比较组的 canonical 实体展示排名：

```text
source_layer = PRODUCT -> product_performance_score
source_layer = SKU     -> sku_performance_score
```

展示排名，同时展示：

```text
为什么表现高
目标画像买了多少
相对其他画像是否更偏好
复购证据是否充分
19:30 前自然动销是否成立
商品毛利是否为正
门店订购是否充分
是否依赖某个月或某家门店
```

算法 04 结果只用于：

```text
1. 识别现有高表现锚点商品
2. 决定购物篮分析默认锚点顺序
3. 为后续组合保留锚点的已定义商品属性；主材料、口味和形态须待规则资产与字段合同落地后补齐
```

不得将综合得分直接表述为新品成功概率。

---

## 31. 完整演示案例复算

本章用于开发复算和业务抽样验收，不作为线上展示文案。

### 31.1 案例 A：稳定成熟锚点

范围：

```text
周期：2026 年 4-6 月
范围：上海
品类：即烹类 / 牛肉制品
门店群：A 级门店群
目标画像：上班族晚高峰型-小家庭-中频-价格非敏感
```

输入样例：

```text
目标画像品类购买会员数 = 1200
其他画像品类购买会员数 = 3000
```

| SKU | 销售占比 | 目标购买人数 | 其他购买人数 | 7天复购 | 非促销19:30前售罄 | 目标毛利额 | 整体毛利额 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 黑椒牛柳丝200g | 30% | 360 | 400 | 96/300 | 82% | 120000 | 300000 |
| 蚝油牛肉片200g | 25% | 300 | 600 | 63/280 | 84% | 85000 | 240000 |
| 香辣牛肉丝200g | 20% | 240 | 650 | 36/220 | 55% | 50000 | 150000 |
| 黑椒牛排200g | 15% | 180 | 450 | 18/160 | 65% | 35000 | 100000 |
| 孜然牛肉粒180g | 10% | 1 | 0 | 1/1 | 30% | 10000 | 15000 |

关键复算：

```text
黑椒牛柳丝原始会员渗透率 = 360 / 1200 = 30%
黑椒牛柳丝会员渗透率 Jeffreys 95% 下界约 = 27.46%

目标画像渗透率 = 360 / 1200 = 30%
其他画像渗透率 = 400 / 3000 = 13.33%
原始偏好指数 = 30% / 13.33% = 2.25
偏好指数 95% 下界约 = 1.98

原始 7 天 19 点前复购率 = 96 / 300 = 32%
复购率 Jeffreys 95% 下界约 = 26.91%
```

四维得分样例：

| SKU | 画像贡献 | 画像偏好 | 自然动销 | 商品毛利 |
|---|---:|---:|---:|---:|
| 黑椒牛柳丝200g | 88 | 90 | 82 | 78 |
| 蚝油牛肉片200g | 76 | 62 | 84 | 72 |
| 香辣牛肉丝200g | 60 | 70 | 55 | 50 |
| 黑椒牛排200g | 45 | 40 | 65 | 58 |
| 孜然牛肉粒180g | 30 | 25 | 30 | 35 |

一级 CRITIC 权重样例：

```text
目标画像贡献权重 = 17.24%
目标画像偏好权重 = 41.05%
自然动销权重     = 25.57%
商品毛利权重     = 16.14%
```

黑椒牛柳丝综合得分：

```text
88 * 17.24% + 90 * 41.05% + 82 * 25.57% + 78 * 16.14% = 85.67
```

Jenks/BIC 样例：

```text
K=1：SSE=1868.15，BIC=31.23
K=2：SSE=530.40，BIC=26.54
K=3：SSE=159.33，BIC=22.14
```

期望结果：

```text
高表现组：黑椒牛柳丝200g、蚝油牛肉片200g
黑椒牛柳丝200g：
is_formal_anchor = 1
anchor_evidence_type = ACTIVE_STABLE_ANCHOR
```

算法 04 到此为止，只输出现有锚点，不输出圆葱、青椒或新品配料结论。

### 31.2 案例 B：低订购率高表现

输入样例：

```text
SKU：青椒牛肉丝180g
可订可售：是
允许订购门店：20 家
实际订购门店：4 家
门店订购率：20%
```

实际订购门店表现：

```text
目标画像偏好指数下界 = 1.72
7 天 19 点前复购率下界 = 24%
非促销 19:30 前售罄率 = 88%
目标画像和 SKU 整体商品毛利均为正
综合得分 = 82
Jenks = 高表现组
```

期望结果：

```text
is_formal_anchor = 1
order_coverage_status = LOW
anchor_evidence_type = LOW_ORDER_HIGH_PERFORMANCE
```

订购率低不能直接扣进综合分，应作为覆盖解释字段保留。

### 31.3 案例 C：1 人中 1 人复购

输入样例：

```text
SKU：孜然牛肉粒180g
目标画像品类购买会员数 = 1200
购买该 SKU 会员数 = 1
具备完整 7 天观察窗口会员数 = 1
发生复购会员数 = 1
其他画像购买该 SKU 会员数 = 0
```

原始值：

```text
原始复购率 = 1 / 1 = 100%
原始偏好指数 = 无穷大
```

统计校正后：

```text
复购率 Jeffreys 平滑值 = 75%
复购率 95% 下界约 = 14.67%
平滑偏好指数 = 7.50
偏好指数 95% 下界约 = 0.31
会员渗透率 = 1 / 1200 = 0.083%
会员渗透率 95% 下界约 = 0.009%
```

期望结果：

```text
evidence_status = LOW_EVIDENCE
is_formal_anchor = 0
不作为默认购物篮锚点
```

## 32. 开发验收

### 32.1 上游接口与对象对账

必须同时验证：

```text
1. dim_customer_profile 的 final_profile 在同批会员范围内唯一。
2. mart_store_category_level 的 SUCCESS 行在范围 + 品类 + 门店粒度唯一，promotion_discount_scope 一致。
3. mart_store_group_consumer_summary 与 mart_store_group_consumer_contribution 同批、同周期并双向一致。
4. 算法 03 汇总为 NOT_CALCULABLE 时贡献明细为 0 行；其他可消费状态必须有合法画像明细。
5. 算法 04 历史门店集合的 store_cnt 与算法 03 汇总一致。
6. 算法 04 SKU 销售额按画像汇总后，与算法 03 对应画像销售额在保留 2 位小数后绝对差不超过 0.01 元。
```

### 32.2 主键与发布完整性

检查三张正式结果表和动态参数表的主键唯一，且同一 `algorithm_batch_version` 使用同一成功 `run_id`。平台成功前四张正式表均不可对下游可见；失败重跑不得覆盖同批已有可靠结果。

### 32.3 公式复算

抽样复算：

```text
sku_sales_share 及品类销售额分母
sku_ticket_penetration 及品类小票分母
sku_buyer_penetration 原始值、Jeffreys 上下界及品类会员分母
repurchase_rate_7d_pre19 及可观察/观察不足人数
preference_index 原始值、平滑值和 95% 下界
non_promo_pre1930_sell_through_rate 及销售量/收货量
store_order_rate、ordered_store_day_rate 及同周期分子分母
target_profile_sku_margin_amt、总毛利及完整价格键匹配
sku_performance_score、CRITIC 权重、Jenks/BIC 分组和 is_formal_anchor
original_price、目标/参考画像成交均价、标准化成交价、促销前后价格和实际折扣率
标准商品层交易级去重销售、小票、会员、复购、成本、稳定性、CRITIC、Jenks/BIC 和锚点准入
canonical 锚点 JSON 与正式锚点数量
```

SKU 层和标准商品层必须分别与 `scoring_layer = SKU / STANDARD_PRODUCT` 的动态参数双向复算。

### 32.4 分层追溯

平台血缘和正式字段共同支持追溯到：

```text
小票商品明细及实际读取分区
算法 01 会员画像
算法 02 门店品类等级
算法 03 门店群汇总与画像贡献明细
商品基础表及 SPU 成员关系
到货、订购、毛利和门店 SKU 日价格数据
可订可售快照与商品状态快照
本批动态参数
```

### 32.5 稳定性与后验

SKU 层和标准商品层分别复算留一门店、留一月和下一周期后验表现。标准商品稳定性必须用交易级标准商品集合重算，不能聚合 SKU 稳定性结论。

### 32.6 边界场景

必须覆盖：

```text
算法 03 汇总 NOT_CALCULABLE，算法 04 零正式行
有合法画像但无合法 SKU，仅输出 NO_VALID_SKU 汇总
只有 1 个或 2 个有效 canonical 实体
没有参考画像
可观察首购人数为 0，但存在观察不足首购会员
无自然销售窗口或售罄率异常
当前不可订或不可售但历史表现好
目标画像毛利不为正或成本无法可靠匹配
价格缺失与同键价格冲突
SPU 多成员、SPU 缺失回退 SKU_ONLY、成员计量无法统一
商品映射冲突和主键重复导致整批不发布
```

### 32.7 字段级交付闸门

逐张检查三张正式结果表、一张动态参数表和运行级复购过程数据集：

```text
1. 字段合同表头严格为：中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释。
2. 每张正式表均写清一行粒度、主键、缺失/降级写法；algorithm_batch_version 进入主键。
3. 所有状态、枚举、二值判断和口径方法字段均在第 29.6 节闭环。
4. JSON 字段明确结构、键名、值类型和空值写法。
5. 每个比率、得分和判断字段能由正式分子、分母或动态参数复算。
6. 固定业务规则不重复落参数表；参数表只保存稳健标准化、CRITIC 和 Jenks/BIC 动态结果。
7. 上游失败、正常排除、无 SKU、指标缺失和不可计算场景严格按写入边界处理。
8. 四张正式表通过整批自行验收后原子可见；平台任务成功是下游启动条件。
```

---

## 33. V1 固定业务规则

| 事项 | V1 规则 |
|---|---|
| 门店群在售聚合 | `ANY_ACTIVE_STORE`；仅使用当前有效门店集合，覆盖不足写 NULL |
| 标准商品在售聚合 | `ANY_ACTIVE_MEMBER`；成员状态完整时任一成员 ACTIVE 即 ACTIVE |
| 首购范围 | `WITHIN_PERFORMANCE_WINDOW`；首购限制在 3 个月表现周期内，首购当天时刻不限 |
| 观察不足会员 | 不进入正式复购分子和分母，单独输出两个诊断人数 |
| 促销代理 | 无促销活动表，使用 `discount_amt > 0`；总折扣口径为 `TOTAL_DISCOUNT_INCL_TIME` |
| 成本降级 | 禁止销售额占比分摊；成本无法可靠匹配时毛利字段 NULL |
| 画像销售额对账 | 保留 2 位小数，绝对差不超过 0.01 元；失败阻断整批发布 |
| 标准商品关系 | 使用商品基础表 SPU；SPU 缺失时 `SKU_ONLY`，不接入独立换码或替代关系 |
| 商品状态缺失 | 状态码 NULL、可用性 `NOT_AVAILABLE`，不推断停售或季节性原因 |
| 商品属性范围 | 只输出规格、单位、单位重量、温层和品牌；缺失标记 `ATTRIBUTE_INCOMPLETE` |
| 时间敏感锚点 | 算法 04 输出稳定性和拉动月份；三组购物篮关联由算法 06 计算 |
| 正式生效 | 三张结果表和动态参数表按统一批次自行验收并原子发布；平台成功后下游读取 |

---

## 34. 开发交付验收项

数据合同已明确的粒度和字段事实不再作为产品待确认项；开发交付按以下项目做真实数据验收。

| 编号 | 验收项 | 影响 |
|---|---|---|
| D1 | 抽样验证 Doris `weight` 与商品基础表销售单位的物理含义，确保标准销售量、重量和件数没有混用 | 数量、复购、售罄率、成本 |
| D2 | `mart_sku_margin_loss` 按合同主键唯一提供销售额、全链路毛利、收货和订购字段，订购与收货分别使用 | 毛利、有效门店商品日、售罄率、订购覆盖 |
| D3 | `mart_store_sku_daily_sale_order_status` 在日期 + 门店 + 销售 SKU 粒度唯一，完整覆盖锁定的当前快照和表现周期 | 当前在售、订购分母、正式锚点 |
| D4 | `mart_store_sku_daily_price` 按日期 + 门店 + 销售 SKU + 收货 SKU 完整键唯一；简化到销售 SKU 前满足唯一收货 SKU 或成本值一致 | 原价、备选成本、价格冲突降级 |
| D5 | 有效交易过滤复用算法 01～04 的共享实现；只使用已确认枚举，未确认的退款或业务来源枚举不得自行扩展为删除条件 | 全部交易指标 |
| D6 | 算法 02 结果与算法 03 汇总/贡献明细同批、同周期、主键唯一，并通过状态与门店数双向对账 | 处理对象、目标画像、历史门店群 |
| D7 | SKU 与 SPU 映射满足销售 SKU 至多一个 SPU；多个 SKU 共享一个 SPU 被视为正常成员关系 | 标准商品独立重算 |
| D8 | 平台保存实际输入分区、任务状态和失败质量记录；四张正式表按批次原子可见 | 重跑、追溯、下游读取 |
| D9 | 用真实数据样例逐字段复算 SKU 层、标准商品层和 canonical 汇总，并验证状态优先级 | 字段级交付闸门 |

### 34.1 当前产品确认状态

V1 产品口径已全部冻结。算法 04 当前没有待产品确认的业务口径；剩余工作均为 D1-D9 的开发数据验收。真实数据验收通过前，不得宣称算法 04 已可正式跑数或发布锚点。

---

## 35. 不能做的事

```text
不能把候选新品当成算法 04 已验证的现有锚点
不能用固定销售、复购和毛利权重
不能把订购率直接加入综合得分
不能用 Min-Max 替代稳健标准化
不能用固定人数门槛替代 Jeffreys 证据判断
不能跳过 Jenks+BIC 动态锚点分组
不能把当前不可订或不可售商品标成 ACTIVE_ANCHOR
不能将不同比较组的综合得分直接横向比较
不能将综合得分说成新品成功概率
```

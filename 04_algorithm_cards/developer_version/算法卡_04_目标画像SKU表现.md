# 算法卡_04_目标画像 SKU 表现算法

更新时间：2026-09-20

业务原始依据：`算法卡_04_目标画像SKU表现_业务提供最新原始版_20260731.md`

开发交付定位：将业务已确认的“目标画像现有高表现锚点商品识别算法”转成数据开发可建表、可计算、可验收的版本。

重要原则：

```text
业务原文中的算法逻辑不得压缩删除。
数据暂不满足的地方，只能标记 V1 落地口径或待确认，不能改写成另一套简单算法。
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

### 2.2 算法编号与上游依赖闸门

算法 04 只消费已经发布的上游正式结果，不在本算法内重算算法 01、02 或 03。

| 上游结果 | 可消费状态 | 不可消费状态/处理 | 版本和周期闸门 |
|---|---|---|---|
| `dim_customer_profile` | 锁定版本内 `customer_id + final_profile` 唯一且非空 | 缺失、重复或画像周期与本算法周期不一致：阻断本次运行 | 校验 `profile_model_version`、`member_filter_rule_version`、`calculation_start_date/end_date` |
| `mart_store_category_level` | 只使用 `result_status = SUCCESS` 的门店品类行 | `NOT_CALCULABLE` 门店不得进入门店群；没有任何 `SUCCESS` 门店时阻断该组 | 校验 `category_level_model_version`、`level_start_date/end_date`、`scope_version` |
| `mart_store_group_consumer_contribution` | 使用 `SUCCESS`、`SINGLE_PROFILE`、`NO_OBVIOUS_MAIN` 的有效画像明细 | `NO_RATED_STORE`、`NO_MEMBER_CONSUMPTION`、版本/关联阻断状态不得当作目标画像输入 | 校验 `consumer_contribution_model_version`、贡献周期、范围和 `final_profile` 唯一 |

当前数据库核查未找到算法 02、算法 03 的正式物理表。未找到时：

```text
upstream_gate_status = UPSTREAM_RESULT_MISSING
不重算上游、不跨范围回退、不写四张正式结果表；只写 process_algo04_run_audit。
```

### 2.3 正式结果与过程表的边界

| 类型 | 表 | 是否下游正式读取 | 写入边界 |
|---|---|---:|---|
| 过程/前置表 | `mart_sku_repurchase_7d_pre19` | 否，先由算法04任务读取 | 仅在上游闸门通过后生成；不替代四张正式结果表 |
| 正式结果表 | `mart_target_profile_sku_performance` | 是 | 只写有合法 SKU 主键的明细；无 SKU 的组状态写摘要和运行审计 |
| 正式结果表 | `mart_target_profile_product_performance` | 是 | 由 SKU 证据聚合到标准商品层后写入 |
| 正式结果表 | `mart_target_profile_anchor_summary` | 是 | 每个合法范围/品类/门店群/画像一行；无消费或无 SKU 时可写状态摘要 |
| 正式参数表 | `mart_target_profile_sku_performance_params` | 是（复算/审计） | 只写实际使用的参数、版本、回退原因和 JSON 结构 |
| 运行审计表 | `process_algo04_run_audit` | 否 | 记录依赖缺失、重复键、对账失败、重跑和阻断原因；不冒充正式结果 |

### 2.4 运行流程和表关系

算法 04 是离线批量识别现有 SKU 锚点，不是前端查询时实时生成新品。

第一段：前置复购结果。

```text
触发：每月正式调度，或上游算法 01-03 正式版本变化后重跑。
输入：有效会员小票、商品、门店群、目标画像。
输出：mart_sku_repurchase_7d_pre19。
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
1. 上游闸门未通过：只写 process_algo04_run_audit；不写复购过程表和四张正式结果表。
2. 上游闸门通过但某范围无目标画像消费：允许写 anchor_summary 状态摘要和 run_audit；不伪造 SKU 明细。
3. 有目标画像消费但无合法 SKU：允许写 anchor_summary 状态摘要和 run_audit；不伪造 SKU 明细、标准商品行或锚点 SKU JSON。
4. 有合法 SKU 但某 SKU 核心字段不可计算：写 SKU 明细的诊断字段和 DATA_INCOMPLETE；不把 NULL 改成 0，不进入正式锚点。
5. 只有通过字段级质量闸门的组，才写正式参数、标准商品表现和锚点汇总的可发布结论。
```

`process_algo04_run_audit` 是过程审计表，不属于下游业务结果；即使正式结果阻断，也必须记录运行批次、阻断原因和输入版本。

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
sku_performance_model_version
+ performance_start_date
+ performance_end_date
+ scope_version
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

### 4.2 上游版本锁定

每次运行必须锁定：

```text
profile_model_version
member_filter_rule_version
category_level_model_version
category_level_start_date
category_level_end_date
consumer_contribution_model_version
consumer_contribution_start_date
consumer_contribution_end_date
category_mapping_version
sku_attribute_version
listing_scope_rule_version
source_data_version
sku_performance_model_version
upstream_version_fingerprint
```

`sku_performance_model_version` 必须由上述版本、周期、范围级在售聚合规则版本和输入快照指纹生成，不能在更换上游版本或在售聚合规则后复用同一个模型版本覆盖旧结果。`upstream_version_fingerprint` 保存完整组合，便于在主键不变时仍能审计实际输入。当前 V1 提案的规则版本可记为 `ANY_ACTIVE_STORE_V1`；业务确认“全部门店”后必须改版本并全量重算。

算法 01、02、03 任一正式版本、过滤规则版本、范围版本或周期变化时，算法 04 必须全量重算。

禁止同一批结果混用不同周期、不同画像版本或不同门店群结果。

画像周期闸门：

```text
dim_customer_profile.calculation_start_date <= performance_start_date
dim_customer_profile.calculation_end_date   >= performance_end_date
算法02 level_start_date/end_date             = performance_start_date/end_date
算法03 contribution_start_date/end_date      = performance_start_date/end_date
```

任一周期无法证明一致时，写 `UPSTREAM_VERSION_ERROR`，不发布正式锚点。

### 4.3 当前在售快照

历史表现使用正式 3 个月周期。

当前在售状态读取计算时最新正式可订可售表快照；商品基础表和门店基础表也必须先锁定同一 `source_data_version`，并锁定由 `dim_sku.data_update_time`、`dim_store.data_update_time`（源系统仅有分区 `dt` 时取该日期）确定的同一主数据快照日期，再与可订可售表 `business_date` 对齐：

```text
listing_snapshot_date
orderable_sellable_flag
source_data_version
```

下一次正式运行时重新读取当前状态，不修改已发布历史版本。

---

## 5. 输入数据与字段合同

### 5.1 必需数据集

| 逻辑数据集 | 是否必需 | 用途 | V1 来源说明 |
|---|---|---|---|
| 算法 01 正式会员画像 | 必须 | 取得每名会员唯一 `final_profile` 和过滤规则版本 | 逻辑表 `dim_customer_profile`；当前物理唯一性已核查 |
| 算法 02 正式门店品类等级 | 必须 | 取得正式门店群和 `final_level` | 逻辑表 `mart_store_category_level`；当前库未找到，缺失即阻断 |
| 算法 03 消费者贡献结果 | 必须 | 取得主力、相对主力和消费者类型范围 | 逻辑表 `mart_store_group_consumer_contribution`；当前库未找到，缺失即阻断 |
| 小票商品明细 | 必须 | 销售、数量、小票、会员及购买时间 | `data_agent.dws_member_order_item_detail_df_all_new` |
| 商品基础表 | 必须 | 商品编码、名称、品类、单位、单位重量和 SPU；独立换码/替代关系不作为 V1 输入 | 逻辑表 `dim_sku`；物理快照需按锁定的 `data_update_time`/分区 `dt` 日期去重 |
| 门店基础表/区域映射 | 必须 | 门店、城市、营业状态和算法范围 | `dim_store` + `dim_city_algorithm_region`；物理快照需锁定 |
| 实际到货/订购明细 | 必须 | 有效在售 SKU 日、实际收货量、订购覆盖 | 逻辑表 `mart_sku_margin_loss`（物理 `data_analysis.dwd_mart_sku_margin_loss`）+ 可订可售表 |
| 商品毛利明细 | 必须 | SKU 总销售额、全链路毛利额；目标画像成本按 V1 单位成本口径分摊 | `mart_sku_margin_loss`；缺字段不得补零 |
| 折扣代理字段 | 必须 | 非促销 SKU 日、实付价格和折扣阶梯 | V1 不接促销活动表，用有效交易行 `discount_amt > 0` 代理，并写方法状态 |
| 门店商品日价格表 | 条件必须 | 原价、成交价和成本备选 | `mart_store_sku_daily_price`；含税出库到店成本字段缺失时不得启用成本备选 |
| 商品状态表 | 解释性 | 历史锚点季节/停售原因 | `dim_product_status`；V1 不作为评分必需输入，缺失时写不可用状态 |
| 7 天复购结果 | 必须 | 复购分子、分母、原始复购率 | V1 先产出过程表 `mart_sku_repurchase_7d_pre19` |

### 5.1.1 逻辑表与物理表映射硬规则

```text
逻辑 `mart_sku_margin_loss`
-> 当前物理映射：`data_analysis.dwd_mart_sku_margin_loss`

逻辑 Doris 小票
-> 当前物理表：`data_agent.dws_member_order_item_detail_df_all_new`
```

以下逻辑表在当前账号核查不到正式物理结果时，不得自行创建临时替代结果冒充上游正式表：

```text
mart_store_category_level
mart_store_group_consumer_contribution
```

`dim_sku`、`dim_store` 物理源若带 `inc_day`、`dt` 或其他快照字段，必须先按调度锁定的 `source_data_version` 和对应快照日期选一版，再按 `sku_id` / `store_id` 去重；不能把所有快照直接连接到交易明细。

### 5.1.2 算法 03 字段映射（物理字段名与本卡别名）

算法 03 正式表的周期字段名必须按其字段合同读取。本卡为了区分算法 04 自身的表现周期，使用 `consumer_contribution_start_date` / `consumer_contribution_end_date` 作为内部别名；开发实现必须显式做以下映射，不得直接读取不存在的同名物理列：

```text
mart_store_group_consumer_contribution.contribution_start_date
    AS consumer_contribution_start_date
mart_store_group_consumer_contribution.contribution_end_date
    AS consumer_contribution_end_date
```

算法 04 内部别名只用于本卡五张正式结果表和参数表；上游接口验收仍以算法 03 的 `contribution_start_date` / `contribution_end_date` 为准，且两列必须分别等于本批 `performance_start_date` / `performance_end_date`。

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
| 小时优惠金额 | `hour_discount_amt` | decimal(18,6) | 可选 | Doris `hour_discount_amt` | 不是商品行时段折扣金额，不直接按行求和 |
| 订单状态 | `order_status` | varchar(64) | 必须 | Doris `order_status` | 有效交易过滤，V1 保留 `os.completed` |
| 是否退货 | `is_return` | int | 必须 | Doris `is_return` | 有效交易过滤，V1 保留 `0` |
| 退款类型 | `refund_type` | varchar(64) | 条件必须 | Doris `refund_type` | 退款/冲销过滤辅助字段；枚举未冻结前仅做质量检查 |
| 业务来源 | `business_source` | varchar(64) | 可选 | Doris `business_source` | 测试交易或特殊来源过滤辅助字段 |
| 订单更新时间 | `update_time` | datetime | 必须 | Doris `update_time` | `order_item_id` 去重时按最新记录保留，并用于源数据追溯 |

### 5.3 商品基础表字段

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 交易商品编码 | `sku_id` | varchar(64) | 必须 | `dim_sku.sku_id` | 与 Doris `article_id` 对齐 |
| 商品编码 | `product_id` | varchar(64) | 可选 | `dim_sku.product_id` | 商品主数据编码；缺失时标准商品主键回退 `sku_id` |
| 商品名称 | `sku_name` | varchar(256) | 必须 | `dim_sku.sku_name` | SKU 展示名称 |
| SPU编码 | `spu_id` | varchar(64) | 可选 | `dim_sku.spu_id` | 标准商品层聚合；无有效值时使用 `SKU_ONLY` |
| 大类编码 | `category_level1_code` | varchar(64) | 必须 | `dim_sku.category_level1_code` | 大类计算；按数据合同不能为空 |
| 大类名称 | `category_level1_name` | varchar(128) | 必须 | `dim_sku.category_level1_name` | 大类计算；按数据合同不能为空 |
| 中类编码 | `category_level2_code` | varchar(64) | 必须 | `dim_sku.category_level2_code` | 中类计算；按数据合同不能为空 |
| 中类名称 | `category_level2_name` | varchar(128) | 必须 | `dim_sku.category_level2_name` | 中类计算；按数据合同不能为空 |
| 小类编码 | `category_level3_code` | varchar(64) | 必须 | `dim_sku.category_level3_code` | 小类计算；按数据合同不能为空 |
| 小类名称 | `category_level3_name` | varchar(128) | 必须 | `dim_sku.category_level3_name` | 小类计算；按数据合同不能为空 |
| 销售单位 | `sale_unit` | varchar(32) | 必须 | `dim_sku.sale_unit` | 计量标准化 |
| 单位重量 | `unit_weight_kg` | decimal(18,6) | 条件必须 | `dim_sku.unit_weight_kg` | 定量包装、件转重量时使用 |
| 净含量 | `net_content` | decimal(18,6) | 条件必须 | `dim_sku.net_content` 或规格解析 | 定量包装解释；无法解析时写缺失状态 |
| 主材料 | `main_ingredient` | varchar(128) | 可选 | `dim_sku.main_ingredient` | 商品属性输出，缺失不阻断经营表现 |
| 商品形态 | `product_form` | varchar(128) | 可选 | `dim_sku.product_form` | 商品属性输出，缺失不阻断经营表现 |
| 配料 | `ingredient` | varchar(512) | 可选 | `dim_sku.ingredient` | 商品属性输出，缺失不阻断经营表现 |
| 口味 | `flavor` | varchar(128) | 可选 | `dim_sku.flavor` | 商品属性输出，缺失不阻断经营表现 |
| 加工方式 | `processing_method` | varchar(128) | 可选 | `dim_sku.processing_method` | 商品属性输出，缺失不阻断经营表现 |
| 烹饪方式 | `cooking_method` | varchar(128) | 可选 | `dim_sku.cooking_method` | 商品属性输出，缺失不阻断经营表现 |
| 包装类型 | `package_type` | varchar(128) | 可选 | `dim_sku.package_type` | 商品属性输出，缺失不阻断经营表现 |
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
| 总折扣额 | `discount_amt` | decimal(18,6) | 条件必须 | `mart_sku_margin_loss.discount_amt` | V1 折扣代理汇总 |
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
任一字段缺失或无法映射 -> orderable_sellable_flag = NULL，并写运行审计
```

当前物理源若无法提供合同要求的 `order_sku_id`、`is_saleable` 或 `is_orderable`，必须在 `process_algo04_run_audit` 记录 `DATA_INSUFFICIENT` 或 `UPSTREAM_RESULT_MISSING`，不得用收货、销量或其他代理字段补写订购状态。

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
customer_id 能关联本次锁定的 profile_model_version，且 final_profile 非空
```

`refund_type`、`business_source` 等字段只在已确认枚举后增加精确过滤；未确认的枚举不能被开发自行扩大为删除条件，必须写入运行审计和规则版本。

过滤方式字段：

```text
valid_transaction_filter_method = SOURCE_TABLE_CLEANED
或 RULE_FILTERED
```

`member_filter_rule_version` 必须与算法 01/03 使用的规则版本一致，并写入所有正式结果和运行审计。会员画像、偏好、复购和目标画像毛利只能使用 `valid_profiled_member_txn`；全量 SKU 销售、19:30 前自然动销和折扣阶梯不得误用该集合。

### 6.2 商品映射

```text
商品编码必须关联唯一正式商品记录
SKU 必须成功映射到目标品类
交易发生时只能命中一条有效品类映射
```

V1 商品分类使用当前商品基础表分类；商品分类历史变化概率极低，暂不做历史分类回溯。

如果一对多或品类冲突：

```text
result_status = PRODUCT_MASTER_CONFLICT
禁止发布正式得分
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

无法对平：

```text
result_status = UPSTREAM_RECONCILIATION_ERROR
不发布正式得分
```

同时必须做两层对账：

```text
valid_all_txn SKU 销售额合计
= 毛利损耗表同日门店 SKU 销售额（允许合同约定的金额误差）

valid_profiled_member_txn 目标画像销售额合计
= 算法03对应门店群、品类、消费者画像的 profile_sales_amt
```

全量对账失败时，自然动销和 SKU 总经营字段标记 `UPSTREAM_RECONCILIATION_ERROR`；画像对账失败时，目标画像得分和锚点准入均阻断。两者都不得通过缩小到会员集或用平均值“对平”。

---

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
首次购买：购买该 SKU 的时间不限
第二次购买：首次购买后的第 1 到第 7 个自然日内，且发生在 19:00 前
同一天多张小票不算复购
周期结束前不足 7 天才首次购买的会员不进入分母
```

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
repurchase_rate_7d_pre19
repurchase_model_version
```

公式：

```text
repurchase_rate_7d_pre19
= repeat_buyer_cnt_7d_pre19 / eligible_first_buyer_cnt_7d
```

只有复购率、没有分子分母的结果不能进入正式评分。

---

## 10. 有效在售、订购与铺货

### 10.1 当前在售

```text
is_saleable = 1 AND is_orderable = 1
    -> orderable_sellable_flag = 1 -> listing_status = ACTIVE
is_saleable / is_orderable 均有明确 0/1，且不同时为 1
    -> orderable_sellable_flag = 0 -> listing_status = INACTIVE
字段缺失、快照不一致或主键冲突
    -> orderable_sellable_flag = NULL -> listing_status = NULL
```

当前在售不以近期是否实际到货判断。

#### 10.1.1 有效门店集合和覆盖完整性

可订可售合同的物理粒度是“日期 + 门店 + SKU”，而算法 04 正式结果粒度是“范围 + 门店群 + 画像 + SKU”。跨门店汇总前，必须先冻结本批 `effective_store_set`，再按门店 SKU 日粒度生成 `store_orderable_sellable_flag`。有效门店集合定义为：

```text
1. 先形成 `candidate_store_set`：从算法 02 `mart_store_category_level` 取同一 `scope_version`、同一算法 02 周期、同一品类的 `result_status = SUCCESS` 门店。`store_group_type = FINAL_LEVEL` 时按算法 02 的 `final_level = A/B/C/D` 取对应门店；`store_group_type = ALL_RATED` 时取该品类下所有 A/B/C/D 的 `SUCCESS` 门店并集。`store_group_type` 是算法 04/03 在本地按门店群规则派生的字段，不是算法 02 输入列；`NOT_CALCULABLE` 门店不进入候选集合。
2. 候选集合中的 `store_id`、版本、周期、品类和门店等级必须唯一；同一门店多条记录、等级冲突、版本/周期不一致或品类不一致时，集合直接判为无效，不能静默删掉异常门店。
3. 将候选集合与锁定 `source_data_version` 和 `dim_store.data_update_time`（V1 源系统只有 `dt` 时使用该快照日期）的 `dim_store` 关联。每个候选门店必须恰好命中一条基础记录；`is_open = 1` 的门店进入 `effective_store_set`，已明确 `is_open = 0` 的门店作为已知闭店排除，但仍保留候选/排除计数。
4. `dim_store` 缺失、同一门店多条当前记录、`is_open` 无法解析或候选与快照键不一致时，集合直接判为无效，必须写 `process_algo04_run_audit`，不能把异常门店当成“已排除”。没有任何 `is_open = 1` 的有效门店时同样写 NULL 和审计。
5. `effective_store_set` 的集合版本由 `scope_version + category_level_model_version + listing_snapshot_date + listing_scope_rule_version` 唯一确定。
```

因此，`NOT_CALCULABLE` 门店不能进入有效门店分母，也不能被默认为不可售门店。状态表必须在同一 `listing_snapshot_date` 对每个有效门店和 SKU 提供唯一状态行；状态行未覆盖全部有效门店时，不能把“已覆盖门店全为 0”直接判为 `INACTIVE`。

业务原文没有明确“任一门店”还是“全部门店”的范围级聚合规则，V1 暂拟采用以下可审计口径：

```text
范围内至少一个有效门店的 store_orderable_sellable_flag = 1
    -> orderable_sellable_flag = 1
    -> listing_status = ACTIVE
所有有效门店均已覆盖，且 store_orderable_sellable_flag = 0
    -> orderable_sellable_flag = 0
    -> listing_status = INACTIVE
状态表未覆盖全部有效门店、没有有效状态行、快照日期不一致、`dim_store.is_open` 未知或存在主键冲突
    -> orderable_sellable_flag = NULL
    -> listing_status = NULL
    -> 写 process_algo04_run_audit，不进入正式锚点
```

“任一有效门店即可标记 ACTIVE”是 V1 落地提案，不是业务原文已确认规则；正式发布前必须由业务确认。若业务要求“全部有效门店均可订可售”才算 ACTIVE，应将上述聚合规则和模型版本一起替换，不能在开发实现中自行选择。

物理表中的 `is_saleable` / `is_orderable` 必须先转为明确的 0/1 并通过非空校验。若物理 `is_saleable` 实际含义是“可订可售合并标记”而非纯可售字段，必须先完成字段映射确认；不得直接把该字段当作纯 `is_saleable` 使用。

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

```text
ordered_standard_qty
= CASE
    WHEN measurement_type = WEIGHT THEN order_weight_kg
    ELSE order_qty
  END

ordered_store_cnt
= COUNT(DISTINCT store_id)
  WHERE ordered_standard_qty > 0
  （按商品计量类型选择 mart_sku_margin_loss 的真实订购字段；不把件数和重量相加或混用）

store_order_rate
= ordered_store_cnt / 允许订购该 SKU 的有效门店数

ordered_store_day_rate
= 存在真实订购数量的门店日数 / 允许订购该 SKU 的有效门店营业日数
```

`receipt_qty`、`receipt_weight_kg` 只用于实际收货、有效在售日和售罄率，不能把收货门店数冒充 `ordered_store_cnt`。如果当前物理源缺少该商品计量类型对应的真实 `order_qty` 或 `order_weight_kg`，则：

```text
ordered_store_cnt = NULL
store_order_rate = NULL
ordered_store_day_rate = NULL
order_coverage_status = DATA_INSUFFICIENT
```

该 SKU 仍可保留销售、偏好和自然动销诊断，但不能把订购覆盖解释为已计算。

只有在输入合同明确提供“全局可订范围”事实，且该事实带有来源、`source_data_version`、快照日期和范围版本时，才允许在没有门店级可订清单的兼容场景使用：

```text
分母 = 门店群全部有效门店
orderable_scope = GROUP_ALL_STORES
data_quality_flags 包含 ORDERABLE_SCOPE_DEGRADED
```

`GROUP_ALL_STORES` 只表示订购率分母的范围回退，不补造真实订购分子。即使可以使用该分母，若没有商品计量类型对应的真实订购字段，仍必须按下列规则输出：

```text
ordered_store_cnt = NULL
store_order_rate = NULL
ordered_store_day_rate = NULL
order_coverage_status = DATA_INSUFFICIENT
```

门店 SKU 每日可订可售表是 V1 的合同必需输入，但当前物理核查尚未证明其来源和字段完整；只有开发按合同交付并通过主键、非空和快照验收后，正式计算才可优先使用门店级可订范围：

```text
orderable_scope = STORE_SKU_ORDERABLE
```

如果该门店级表缺失或字段不完整，不能因为缺少商品计量类型对应的订购字段或门店级可订清单而自动切换到 `GROUP_ALL_STORES`；应写入 `process_algo04_run_audit`，并将受影响订购覆盖字段置为 `NULL + DATA_INSUFFICIENT`。只有开发交付了经批准的全局可订范围来源后，才可按上面的兼容口径回退。

订购率不进入综合得分，单独反映门店采用程度。

### 10.4 订购覆盖分组

订购率高低使用自身 Jenks+BIC 动态划分，不使用固定 50%。

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
-> result_status = SELL_THROUGH_DATA_ERROR
-> 不进入自然动销得分
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

只有在个别 SKU 或个别日期出现 `weight` 缺失、`weight <= 0`、计量类型无法识别等异常，导致目标画像标准销售量无法取得时，才允许进入异常兜底：

```text
target_profile_daily_store_sku_cost_amt
= daily_store_sku_cost_amt
 * target_profile_daily_store_sku_sales_amt
 / daily_store_sku_sales_amt

cost_allocation_method = SALES_AMOUNT_SHARE_DEGRADED
cost_allocation_status = COST_ALLOCATED_DEGRADED
```

销售额占比分摊不是默认口径，只能作为异常兜底。若异常兜底仍无法保证可解释，则相关 SKU 输出：

```text
result_status = DATA_INCOMPLETE
cost_allocation_status = COST_NOT_ALLOCATED
```

若启用降级，必须写入 `data_quality_flags`，不能静默按销售额占比分摊。

备选：

```text
cost_source = ARRIVAL_COST_TAX_INCLUDED
```

使用门店商品日价格表 `出库到店成本含税` 时，先按 `warehouse_id + store_id + sku_id + business_date` 校验仓商品日成本口径，再聚合到日期 + 门店 + 销售 SKU。

### 16.4 正式锚点毛利底线

```text
target_profile_sku_margin_amt > 0
并且
sku_total_margin_amt > 0
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

锚点 SKU 输出：

```text
main_ingredient：主材料
product_form：肉类部位或商品形态
ingredient：已有配料
flavor：口味
processing_method：加工方式
cooking_method：烹饪方式
net_content：净含量
package_type：包装方式
temperature_layer：温层
brand_name：品牌
```

### 17.2 来源优先级

```text
1. 商品基础表
2. 已审核 SKU 属性字典
3. SKU 名称、商品描述和包装规格规则解析
```

冲突优先级：

```text
商品基础表 > 属性字典 > 名称规则
```

每个属性保存：

```text
attribute_value
attribute_source
attribute_confidence
attribute_version
```

V1 正式落地只强依赖商品基础表已有字段和名称/规格规则解析。其他非数据合同来源不作为一期输入；缺失属性输出 `ATTRIBUTE_INCOMPLETE`。

无法确认时输出：

```text
UNKNOWN
```

### 17.3 商品编码核对

```text
同一商品编码在同一有效日期只能命中一条正式商品记录
商品编码命中后仍需校验商品名称和品类一致性
一对多或品类冲突禁止重复关联小票金额
```

### 17.4 SKU 与标准商品双层

输出两层：

```text
SKU 层：保留原始商品编码表现
标准商品层：按商品基础表现有 spu_id 汇总同一标准商品
```

V1 只使用商品基础表现有 `spu_id` 做标准商品归并，不新增独立换码或替代关系。

`spu_id` 缺失或无法稳定映射时：

```text
standard_product_mode = SKU_ONLY
```

名称相似不能自动合并。

标准商品层的计算顺序必须冻结：

```text
1. SKU 层保留每个销售 SKU 的原始交易、门店、会员和状态证据，供追溯。
2. `spu_id` 有效且在当前商品快照内唯一时，按 `standard_product_key = spu_id` 聚合；缺失或冲突时按 `SKU_ONLY`。
3. 先按标准商品层重新聚合去重小票、去重会员、销售额、标准量、实际收货量和成本，再在标准商品层重算 CRITIC、综合分、Jenks/BIC 和正式锚点准入。
4. SKU 行不把 SKU 自身分数冒充标准商品分数；通过 `standard_product_key` 关联标准商品层的分组和锚点结论，并保留 `sku_id` 追溯。
5. 标准商品层无法稳定聚合时，写 `standard_product_mode = SKU_ONLY`、`result_status = PRODUCT_MASTER_CONFLICT` 或 `DATA_INCOMPLETE`，不得按名称相似合并。
```

标准商品层的去重必须在“标准商品 + 会员 + 小票”键上执行，不能先把各 SKU 的去重会员数简单相加，否则会重复计算跨 SKU 购买者。

标准商品层关键指标口径：

```text
product_sales_amt = SUM(标准商品层去重后的目标画像有效销售额)
product_sales_qty = SUM(标准商品层可解释计量类型内的标准销售量)
product_ticket_cnt = COUNT(DISTINCT standard_product_key + ticket_key)
product_buyer_cnt = COUNT(DISTINCT customer_id)
product_margin_amt = product_sales_amt - product_cost_amt
product_preference = 目标画像标准商品渗透率 / 参考画像标准商品渗透率，再做 Jeffreys 区间
```

标准商品层自然动销使用全量有效交易和标准商品实际收货量；标准商品层 CRITIC 使用重新计算的指标矩阵，不能对 SKU 分数做平均或按 SKU 数量加权。标准商品层通过正式锚点准入后，SKU 行只继承/关联标准商品的 `performance_group`、`is_formal_anchor` 和锚点状态，不得把单个 SKU 的分数伪装成标准商品分数。

---

## 18. 价格指标与算法 05 边界

算法 04 只输出现有 SKU 价格描述：

```text
original_price
target_profile_avg_paid_price
reference_profile_avg_paid_price
standardized_paid_price
before_after_promotion_price
actual_discount_rate
```

价格不进入算法 04 综合得分。

目标画像可接受价格和候选新品价格带由算法 05 单独计算。

正式输出字段及计算边界：

```text
original_price = 当前价格快照的销售原价；不能用 avg_sale_price 代替
target_profile_avg_paid_price = 目标画像实付金额 / 目标画像销售标准量
reference_profile_avg_paid_price = 参考画像实付金额 / 参考画像销售标准量
standardized_paid_price = 按 sale_unit、unit_weight_kg 和 standard_unit 换算后的标准化实付价
before_after_promotion_price = {"before_price": 原价, "after_price": 促销后实际成交价, "price_source": "PRICE_TABLE_ORIGINAL_DORIS_USUAL_AMT_PER_WEIGHT"} 对象
actual_discount_rate = 1 - after_price / before_price；分母为 0 或价格缺失时写 NULL
```

价格来源缺失时保留 `NULL`，并在 `data_quality_flags` 写 `PRICE_SOURCE_MISSING`；不得把价格缺失静默当作 0，也不得因此进入算法 04 综合分。

`dim_product_status` 在 V1 只作为解释性状态输入：不参与评分、不阻断有完整经营数据的 SKU。季节/停售原因只有在该表提供可靠版本和枚举时才展示；否则写 `product_status_code = NULL`、`product_status_availability = NOT_AVAILABLE`，不得根据销量季节性或名称编造原因。

---

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

---

## 22. Jenks+BIC 动态锚点组

### 22.1 候选组数

对同一比较组的 `sku_performance_score` 从低到高排序：

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

`listing_status = NULL` 只表示当前状态未知，不能降级成 `HISTORICAL_ANCHOR`；该 SKU 写 `NOT_ANCHOR`/`DATA_INCOMPLETE` 并保留运行审计。
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

完整 3 个月仍为正式结果。

时间敏感不直接删除锚点。

---

## 27. 时间敏感锚点的购物篮路径

稳定锚点：

```text
使用完整 3 个月小票进行购物篮分析
关联结果可作为常规商品开发证据
```

时间敏感锚点同时计算：

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

门店集中锚点同理增加分店验证。

---

## 28. 结果状态设计

算法 04 不使用一个大而全的组合标签。计算结果、锚点资格、在售状态、盈利状态、证据状态、门店稳定性、时间稳定性、自然动销状态、订购覆盖状态和属性完整度必须拆成独立字段保存。

正式输出字段和状态取值约束见第 29 章。缺失、不适用和异常不能写成 0。

---

## 29. 输出表

算法 04 开发交付 6 张可持久化表：1 张前置复购过程表 + 4 类正式结果表 + 1 张运行审计表。

开发可以有临时表或过程表，但下游正式读取以下表：

| 表名 | 表类型 | 一行代表什么 | 下游用途 |
|---|---|---|---|
| `mart_sku_repurchase_7d_pre19` | 前置中间结果表 | 一个周期 + 一个范围 + 一个消费者画像 + 一个 SKU 的 7 天 19 点前复购结果 | 先由算法 04 计算，再被 SKU 表现主表读取 |
| `mart_target_profile_sku_performance` | 正式结果表 | 一个周期 + 一个范围 + 一个门店群 + 一个消费者画像 + 一个销售 SKU | 算法 04 主表，给算法 05/06/09/10 读取 |
| `mart_target_profile_product_performance` | 正式结果表 | 一个周期 + 一个范围 + 一个门店群 + 一个消费者画像 + 一个标准商品 | 标准商品层表现，V1 用 SPU，SPU 缺失时按 SKU_ONLY |
| `mart_target_profile_anchor_summary` | 正式结果表 | 一个周期 + 一个范围 + 一个门店群 + 一个消费者画像的锚点汇总 | 给业务验收和下游选择默认锚点 |
| `mart_target_profile_sku_performance_params` | 正式参数表 | 一个参数版本 + 一个参数作用范围 + 一个参数 | 复现 CRITIC、Jenks/BIC、Jeffreys、单位映射和口径参数 |
| `process_algo04_run_audit` | 运行审计表 | 一个运行批次 + 一个范围处理单元 + 一个审计事件 | 记录阻断、告警、对账和正式写入闸门，不供业务查询 |

### 29.1 前置表：`mart_sku_repurchase_7d_pre19`

一行代表：一个周期、一个范围、一个门店群、一个消费者画像和一个 SKU 的 7 天 19 点前复购结果。

主键：

```text
repurchase_model_version
+ performance_start_date
+ performance_end_date
+ scope_version
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
| 复购口径版本 | `repurchase_model_version` | varchar(64) | 必须 | 算法 04 参数 | 7 天 19 点前复购计算版本 |
| 数据周期开始日期 | `performance_start_date` | date | 必须 | 调度参数 | 统计周期开始日期 |
| 数据周期结束日期 | `performance_end_date` | date | 必须 | 调度参数 | 统计周期结束日期 |
| 范围版本 | `scope_version` | varchar(64) | 必须 | `dim_city_algorithm_region` 数据快照 / 调度参数 | 城市算法区域版本 |
| 范围类型 | `scope_type` | varchar(32) | 必须 | `dim_city_algorithm_region` + 本算法范围映射 | `CITY` / `CITY_CLUSTER` |
| 范围编码 | `scope_id` | varchar(64) | 必须 | `dim_city_algorithm_region.algorithm_region_code` / 本算法范围映射 | 城市或城市群编码 |
| 范围名称 | `scope_name` | varchar(128) | 必须 | `dim_city_algorithm_region.algorithm_region_name` / 本算法范围映射 | 城市或城市群名称 |
| 品类颗粒度 | `category_granularity` | varchar(32) | 必须 | `dim_sku` + 本算法品类颗粒度映射 | 大类 / 中类 / 小类 |
| 品类编码 | `category_code` | varchar(64) | 必须 | `dim_sku.category_level1_code/category_level2_code/category_level3_code` + 本算法品类颗粒度映射 | 当前计算品类编码 |
| 品类名称 | `category_name` | varchar(128) | 必须 | `dim_sku.category_level1_name/category_level2_name/category_level3_name` + 本算法品类颗粒度映射 | 当前计算品类名称 |
| 门店群类型 | `store_group_type` | varchar(32) | 必须 | `mart_store_category_level.final_level` + 本算法第 3.1 节范围分组 | `FINAL_LEVEL` / `ALL_RATED` |
| 门店品类等级 | `final_level` | varchar(32) | 必须 | 算法 02 `mart_store_category_level` | A/B/C/D 或 ALL_RATED |
| 消费者画像 | `final_profile` | varchar(128) | 必须 | 算法 01 `dim_customer_profile` | 算法 01 最终画像 |
| 会员画像版本 | `profile_model_version` | varchar(64) | 必须 | 算法 01 `dim_customer_profile` | 本次锁定会员画像版本 |
| 会员过滤规则版本 | `member_filter_rule_version` | varchar(64) | 必须 | 算法 01/03 正式结果 | 本次运行继承的有效会员过滤规则版本 |
| 门店品类等级版本 | `category_level_model_version` | varchar(64) | 必须 | 算法 02 `mart_store_category_level` | 本次锁定门店品类等级版本 |
| 门店品类等级开始日期 | `category_level_start_date` | date | 必须 | 算法 02 `mart_store_category_level` | 算法 02 结果周期开始日期 |
| 门店品类等级结束日期 | `category_level_end_date` | date | 必须 | 算法 02 `mart_store_category_level` | 算法 02 结果周期结束日期 |
| 消费者贡献版本 | `consumer_contribution_model_version` | varchar(64) | 必须 | 算法 03 `mart_store_group_consumer_contribution` | 本次锁定消费者贡献版本 |
| 消费者贡献开始日期 | `consumer_contribution_start_date` | date | 必须 | `mart_store_group_consumer_contribution.contribution_start_date`（本卡别名） | 算法 03 结果周期开始日期 |
| 消费者贡献结束日期 | `consumer_contribution_end_date` | date | 必须 | `mart_store_group_consumer_contribution.contribution_end_date`（本卡别名） | 算法 03 结果周期结束日期 |
| 商品分类版本 | `category_mapping_version` | varchar(64) | 必须 | `dim_sku` 数据快照 / 调度参数 | 商品分类口径版本 |
| 源数据版本 | `source_data_version` | varchar(128) | 必须 | 调度参数 + 输入快照 | 小票、商品、门店和经营表的统一输入快照版本 |
| 上游版本指纹 | `upstream_version_fingerprint` | varchar(512) | 必须 | 本算法第 4.2 节版本指纹生成 | 由画像、门店等级、贡献、过滤规则、周期、在售聚合规则和源数据版本组成的完整指纹 |
| 在售范围聚合规则版本 | `listing_scope_rule_version` | varchar(64) | 必须 | 调度参数 + 本算法第 10.1.1 节有效门店集合 | 例如 `ANY_ACTIVE_STORE_V1`；规则变更必须全量重算，不得复用旧结果 |
| SKU 编码 | `sku_id` | varchar(64) | 必须 | `data_agent.dws_member_order_item_detail_df_all_new.article_id` / `dim_sku.sku_id` | 销售 SKU |
| 7 天复购会员数 | `repeat_buyer_cnt_7d_pre19` | bigint | 必须 | Doris 小票计算 | 首次购买后第 1-7 个自然日且 19:00 前再次购买该 SKU 的会员数 |
| 7 天可观察首购会员数 | `eligible_first_buyer_cnt_7d` | bigint | 必须 | Doris 小票计算 | 首次购买后具备完整 7 天观察窗口的会员数 |
| 7 天 19 点前复购率 | `repurchase_rate_7d_pre19` | decimal(18,8) | 必须 | 本表计算 | `repeat_buyer_cnt_7d_pre19 / eligible_first_buyer_cnt_7d` |
| 计算状态 | `repurchase_calc_status` | varchar(64) | 必须 | 本表计算 | 见第 29.6 节状态约束 |
| 上游闸门状态 | `upstream_gate_status` | varchar(64) | 必须 | 本算法上游依赖闸门 | 上游结果、版本和周期是否允许本表计算 |
| 计算时间 | `calculated_at` | datetime | 必须 | 系统生成 | 结果写入时间 |

### 29.2 SKU 表现明细：`mart_target_profile_sku_performance`

一行代表：一个周期、一个范围、一个门店群、一个消费者画像和一个销售 SKU 的表现结果。

主键：

```text
sku_performance_model_version
+ performance_start_date
+ performance_end_date
+ scope_version
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
| SKU 表现模型版本 | `sku_performance_model_version` | varchar(64) | 必须 | 算法 04 参数 | 算法 04 本次计算版本 |
| 数据周期开始日期 | `performance_start_date` | date | 必须 | 调度参数 | 最近 3 个完整自然月开始日期 |
| 数据周期结束日期 | `performance_end_date` | date | 必须 | 调度参数 | 最近 3 个完整自然月结束日期 |
| 范围版本 | `scope_version` | varchar(64) | 必须 | `dim_city_algorithm_region` 数据快照 / 调度参数 | 城市算法区域版本 |
| 范围类型 | `scope_type` | varchar(32) | 必须 | `dim_city_algorithm_region` + 本算法范围映射 | `CITY` / `CITY_CLUSTER` |
| 范围编码 | `scope_id` | varchar(64) | 必须 | `dim_city_algorithm_region.algorithm_region_code` / 本算法范围映射 | 城市或城市群编码 |
| 范围名称 | `scope_name` | varchar(128) | 必须 | `dim_city_algorithm_region.algorithm_region_name` / 本算法范围映射 | 城市或城市群名称 |
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
| 门店品类等级 | `final_level` | varchar(32) | 必须 | 算法 02 `mart_store_category_level` | 当前门店群等级 |
| 门店数 | `store_cnt` | bigint | 必须 | 本算法第 10.1.1 节 `effective_store_set`（来源为 `mart_store_category_level.store_id` + `dim_store.is_open`） | 当前范围内进入计算的有效营业门店数 |
| 消费者画像 | `final_profile` | varchar(128) | 必须 | 算法 01 `dim_customer_profile` | 目标消费者画像 |
| 是否主力画像 | `is_main_profile` | tinyint | 必须 | 算法 03 `mart_store_group_consumer_contribution` | `1` 是正式主力画像，`0` 不是 |
| 是否相对主力候选 | `is_relative_main_candidate` | tinyint | 必须 | 算法 03 `mart_store_group_consumer_contribution` | `1` 是相对主力候选，`0` 不是 |
| 会员画像版本 | `profile_model_version` | varchar(64) | 必须 | 算法 01 `dim_customer_profile` | 本次锁定会员画像版本 |
| 门店品类等级版本 | `category_level_model_version` | varchar(64) | 必须 | 算法 02 `mart_store_category_level` | 本次锁定门店品类等级版本 |
| 消费者贡献版本 | `consumer_contribution_model_version` | varchar(64) | 必须 | 算法 03 `mart_store_group_consumer_contribution` | 本次锁定消费者贡献版本 |
| 商品分类版本 | `category_mapping_version` | varchar(64) | 必须 | `dim_sku` 数据快照 / 调度参数 | 商品基础表分类口径版本 |
| 商品属性版本 | `sku_attribute_version` | varchar(64) | 必须 | `dim_sku` 数据快照 / 本算法第 17 章属性加工规则 | V1 为商品基础表和名称解析口径版本 |
| 在售快照日期 | `listing_snapshot_date` | date | 必须 | `mart_store_sku_daily_sale_order_status.business_date` | 当前可订可售快照日期 |
| 在售范围聚合规则版本 | `listing_scope_rule_version` | varchar(64) | 必须 | 调度参数 + 本算法第 10.1.1 节有效门店集合 | 例如 `ANY_ACTIVE_STORE_V1`；用于追溯任一/全部有效门店规则 |
| 会员过滤规则版本 | `member_filter_rule_version` | varchar(64) | 必须 | 算法 01/03 正式结果 | 本次运行继承的有效会员过滤规则版本 |
| 门店品类等级开始日期 | `category_level_start_date` | date | 必须 | 算法 02 `mart_store_category_level` | 算法 02 结果周期开始日期 |
| 门店品类等级结束日期 | `category_level_end_date` | date | 必须 | 算法 02 `mart_store_category_level` | 算法 02 结果周期结束日期 |
| 消费者贡献开始日期 | `consumer_contribution_start_date` | date | 必须 | `mart_store_group_consumer_contribution.contribution_start_date`（本卡别名） | 算法 03 结果周期开始日期 |
| 消费者贡献结束日期 | `consumer_contribution_end_date` | date | 必须 | `mart_store_group_consumer_contribution.contribution_end_date`（本卡别名） | 算法 03 结果周期结束日期 |
| 源数据版本 | `source_data_version` | varchar(128) | 必须 | 调度参数 + 输入快照 | 小票、商品、门店和经营表统一输入快照版本 |
| 上游版本指纹 | `upstream_version_fingerprint` | varchar(512) | 必须 | 本算法第 4.2 节版本指纹生成 | 完整上游版本、周期、过滤规则、在售聚合规则和源数据指纹 |
| 有效交易过滤方式 | `valid_transaction_filter_method` | varchar(64) | 必须 | 本算法第 6.1 节交易过滤 | 见第 29.6 节状态约束 |
| 上游闸门状态 | `upstream_gate_status` | varchar(64) | 必须 | 本算法第 2.2 节 | 上游结果、版本和周期是否允许正式计算 |

商品、在售和计量字段：

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| SKU 编码 | `sku_id` | varchar(64) | 必须 | `data_agent.dws_member_order_item_detail_df_all_new.article_id` / `dim_sku.sku_id` | 销售 SKU |
| 商品编码 | `product_id` | varchar(64) | 建议 | `dim_sku.product_id` | 商品主数据编码；可为空，缺失时标准商品主键回退 `sku_id` |
| SKU 名称 | `sku_name` | varchar(256) | 必须 | `dim_sku.sku_name` | 商品展示名称 |
| SPU 编码 | `spu_id` | varchar(64) | 建议 | `dim_sku.spu_id` | 商品基础表现有 SPU 编码 |
| SPU 名称 | `spu_name` | varchar(256) | 建议 | `dim_sku.spu_name` | 商品基础表现有 SPU 名称 |
| 标准商品主键 | `standard_product_key` | varchar(128) | 必须 | `dim_sku.spu_id` / `dim_sku.sku_id` + 本算法第 17.4 节标准商品归并 | SPU 有效时取 `spu_id`，否则取 `sku_id` |
| 标准商品模式 | `standard_product_mode` | varchar(64) | 必须 | 本算法第 17.4 节标准商品归并 | 见第 29.6 节状态约束 |
| 是否可订可售 | `orderable_sellable_flag` | tinyint | 必须 | `mart_store_sku_daily_sale_order_status.is_orderable` + `mart_store_sku_daily_sale_order_status.is_saleable` + 本算法第 10.1 节范围聚合 | 按同一快照日期聚合到范围 + 门店群 + SKU；门店覆盖不足、无有效状态行或冲突写 NULL |
| 在售状态 | `listing_status` | varchar(64) | 必须 | 本算法第 10.1 节范围聚合 | 见第 29.6 节状态约束；范围聚合规则确认前不得发布正式锚点 |
| 计量类型 | `measurement_type` | varchar(32) | 必须 | `dim_sku.sale_unit` / `dim_sku.specification` / 本算法第 11.1 节 | `WEIGHT` / `QUANTITY` / `PIECE_COUNT` / `VOLUME` / `UNKNOWN` |
| 销售单位 | `sale_unit` | varchar(32) | 必须 | `dim_sku.sale_unit` | 商品基础表单位 |
| 标准单位 | `standard_unit` | varchar(32) | 必须 | `dim_sku.sale_unit` / 本算法第 11.1 节标准单位映射 | 算法计算使用的标准单位 |
| 单位换算系数 | `conversion_factor` | decimal(18,8) | 条件必须 | `dim_sku.unit_weight_kg` / 本算法第 11.1 节单位换算 | 从销售单位换算到标准单位的系数 |
| 计量映射状态 | `measurement_mapping_status` | varchar(64) | 必须 | 本算法第 11.1 节单位映射 | 见第 29.6 节状态约束 |
| 订购范围口径 | `orderable_scope` | varchar(64) | 必须 | `mart_store_sku_daily_sale_order_status` / 本算法第 10 章 | 见第 29.6 节状态约束 |
| 订购门店数 | `ordered_store_cnt` | bigint | 必须 | `mart_sku_margin_loss.order_qty/order_weight_kg`（按 `measurement_type` 选择）+ `mart_store_sku_daily_sale_order_status.is_orderable` | 周期内适用计量类型的真实订购数量大于 0 的门店数；适用字段缺失写 NULL |
| 允许订购门店数 | `eligible_orderable_store_cnt` | bigint | 必须 | `mart_store_sku_daily_sale_order_status.is_orderable` | 当前门店群内允许订购该 SKU 的有效门店数 |
| 门店订购率 | `store_order_rate` | decimal(18,8) | 必须 | 本算法第 10.3 节订购率 | 订购门店数 / 允许订购该 SKU 的有效门店数 |
| 允许订购有效门店日数 | `eligible_orderable_store_day_cnt` | bigint | 必须 | `mart_store_sku_daily_sale_order_status.is_orderable` + `business_date` | 当前门店群内允许订购该 SKU 的有效门店营业日数 |
| 门店订购日率 | `ordered_store_day_rate` | decimal(18,8) | 必须 | `mart_sku_margin_loss.order_qty/order_weight_kg`（按 `measurement_type` 选择）+ 本算法第 10.3 节 | 有真实订购数量的门店日数 / 允许订购的有效门店营业日数 |

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
| 参考画像渗透率 | `reference_penetration` | decimal(18,8) | 必须 | 本算法第 12.2 节原始渗透率 | 非目标画像购买该 SKU 的会员渗透率 |
| 参考画像渗透率分子 | `reference_penetration_numerator` | bigint | 必须 | 本算法第 12.2 节原始渗透率 | 参考画像购买该 SKU 的去重会员数 |
| 参考画像渗透率分母 | `reference_penetration_denominator` | bigint | 必须 | 本算法第 12.2 节原始渗透率 | 参考画像在相同可购买门店日内购买该品类的去重会员数 |
| 偏好参考组状态 | `preference_reference_status` | varchar(64) | 必须 | `mart_store_group_consumer_contribution` + 本算法第 12.4 节对照组判断 | 见第 29.6 节状态约束 |
| 原始偏好指数 | `preference_index_raw` | decimal(18,8) | 必须 | 本算法第 12.3 节偏好指数 | 目标画像渗透率 / 参考画像渗透率 |
| 平滑偏好指数 | `smoothed_preference_index` | decimal(18,8) | 必须 | Jeffreys 平滑 | 小样本校正后的偏好指数 |
| 偏好指数 95% 下界 | `preference_lower_95` | decimal(18,8) | 必须 | Jeffreys 区间 | 正式评分使用下界 |
| 偏好指数 95% 上界 | `preference_upper_95` | decimal(18,8) | 必须 | Jeffreys 区间 | 偏好指数区间上界 |
| 7 天复购会员数 | `repeat_buyer_cnt_7d_pre19` | bigint | 必须 | `mart_sku_repurchase_7d_pre19` | 7 天内且 19:00 前复购该 SKU 的会员数 |
| 7 天可观察首购会员数 | `eligible_first_buyer_cnt_7d` | bigint | 必须 | `mart_sku_repurchase_7d_pre19` | 有完整 7 天观察窗口的首购会员数 |
| 7 天 19 点前复购率原始值 | `repurchase_rate_7d_pre19_raw` | decimal(18,8) | 必须 | `mart_sku_repurchase_7d_pre19` | 原始复购率 |
| 7 天 19 点前复购率 95% 下界 | `repurchase_rate_7d_pre19_lower_95` | decimal(18,8) | 必须 | Jeffreys 区间 | 正式评分使用下界 |
| 7 天 19 点前复购率 95% 上界 | `repurchase_rate_7d_pre19_upper_95` | decimal(18,8) | 必须 | Jeffreys 区间 | 复购率区间上界 |

经营、毛利和价格字段：

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 有效门店 SKU 日数 | `available_store_day_cnt` | bigint | 必须 | `mart_sku_margin_loss` / `mart_store_sku_daily_sale_order_status` | 周期内有实际收货条件的门店 SKU 日数 |
| 每有效门店 SKU 日销售额 | `sales_per_available_store_day` | decimal(18,8) | 必须 | 本算法第 10.2 节有效在售 SKU 日 | 目标画像销售额 / 有效门店 SKU 日数 |
| 每有效门店 SKU 日购买会员数 | `buyers_per_available_store_day` | decimal(18,8) | 必须 | 本算法第 10.2 节有效在售 SKU 日 | 目标画像购买会员数 / 有效门店 SKU 日数 |
| 实际到货标准量 | `actual_arrival_standard_qty` | decimal(18,6) | 必须 | `mart_sku_margin_loss.receipt_qty` / `mart_sku_margin_loss.receipt_weight_kg` / `dim_sku.sale_unit` | 称重商品取门店进货重量；普通计件和枚数型商品取门店进货数量；体积商品可稳定换算时按标准体积口径换算 |
| 19:30 前销售标准量 | `pre1930_sales_standard_qty` | decimal(18,6) | 必须 | `data_agent.dws_member_order_item_detail_df_all_new.weight` | 有效 SKU 日 19:30 前销售标准量 |
| 非促销有效门店 SKU 日数 | `non_promo_available_store_day_cnt` | bigint | 必须 | `data_agent.dws_member_order_item_detail_df_all_new.discount_amt` + `mart_sku_margin_loss` | 19:30 前 `discount_amt = 0` 的有效门店 SKU 日数 |
| 非促销实际到货标准量 | `non_promo_actual_arrival_standard_qty` | decimal(18,6) | 必须 | `mart_sku_margin_loss.receipt_qty/receipt_weight_kg` + `dim_sku.sale_unit` + 本算法第 14.2 节非促销窗口过滤 | 非促销有效 SKU 日实际到货标准量 |
| 非促销 19:30 前销售标准量 | `non_promo_pre1930_sales_standard_qty` | decimal(18,6) | 必须 | `data_agent.dws_member_order_item_detail_df_all_new.weight` | 非促销有效 SKU 日 19:30 前销售标准量 |
| SKU 总 19:30 前销售标准量 | `sku_total_pre1930_sales_standard_qty` | decimal(18,6) | 必须 | `data_agent.dws_member_order_item_detail_df_all_new.weight` | 全量有效交易该 SKU 19:30 前销售标准量；用于经营解释，不作为目标画像吸收率分母 |
| 19:30 前售罄率 | `pre1930_sell_through_rate` | decimal(18,8) | 必须 | `data_agent.dws_member_order_item_detail_df_all_new.weight` + `mart_sku_margin_loss.receipt_qty/receipt_weight_kg` | 19:30 前销售标准量 / 实际收货标准量 |
| 非促销 19:30 前售罄率 | `non_promo_pre1930_sell_through_rate` | decimal(18,8) | 必须 | `data_agent.dws_member_order_item_detail_df_all_new.weight` + `mart_sku_margin_loss.receipt_qty/receipt_weight_kg` | 剔除 `discount_amt > 0` 代理促销后的 19:30 前售罄率 |
| 每有效门店 SKU 日 19:30 前销售量 | `pre1930_sales_volume_per_available_store_day` | decimal(18,8) | 必须 | `data_agent.dws_member_order_item_detail_df_all_new.weight` | 19:30 前销售标准量 / 有效门店 SKU 日数 |
| 目标画像 19:30 前吸收率 | `target_profile_pre1930_absorption_rate` | decimal(18,8) | 必须 | 本算法第 14.5 节吸收贡献 | 目标画像 19:30 前销售标准量 / 该 SKU 实际收货标准量；门店群总销售量另存解释字段 |
| 折扣阶梯 JSON | `discount_ladder_json` | json | 必须 | Doris 小票 + 本算法第 15 章 | JSON 数组；每项含 `band_start`、`band_end`、`sales_standard_qty`、`incremental_sell_through_rate`、`cumulative_sell_through_rate_at_band_end`、`actual_discount_rate`；无数据写 `[]` |
| 目标画像 SKU 销售额 | `target_profile_sku_sales_amt` | decimal(18,6) | 必须 | Doris 小票 | 目标画像该 SKU 销售额 |
| 目标画像 SKU 成本额 | `target_profile_sku_cost_amt` | decimal(18,6) | 必须 | `mart_sku_margin_loss.sales_amt/full_link_margin_amt` + 本算法第 16.3 节目标画像成本分摊 | 按标准量单位成本分摊到目标画像的 SKU 成本金额 |
| 目标画像 SKU 毛利额 | `target_profile_sku_margin_amt` | decimal(18,6) | 必须 | 本算法第 16.1 节毛利公式 | `target_profile_sku_sales_amt - target_profile_sku_cost_amt` |
| 目标画像 SKU 毛利率 | `target_profile_sku_margin_rate` | decimal(18,8) | 必须 | 本算法第 16.1 节毛利公式 | `target_profile_sku_margin_amt / target_profile_sku_sales_amt` |
| SKU 总销售额 | `sku_total_sales_amt` | decimal(18,6) | 必须 | `mart_sku_margin_loss.sales_amt` | 该 SKU 在比较组内全量销售额 |
| SKU 总成本额 | `sku_total_cost_amt` | decimal(18,6) | 必须 | `mart_sku_margin_loss.sales_amt` + `mart_sku_margin_loss.full_link_margin_amt` + 本算法第 16 章 | `sku_total_sales_amt - sku_total_margin_amt` |
| SKU 总毛利额 | `sku_total_margin_amt` | decimal(18,6) | 必须 | `mart_sku_margin_loss.full_link_margin_amt` | 该 SKU 在比较组内全链路毛利额 |
| SKU 总毛利率 | `sku_total_margin_rate` | decimal(18,8) | 必须 | 本算法第 16.1 节毛利公式 | `sku_total_margin_amt / sku_total_sales_amt` |
| 成本来源 | `cost_source` | varchar(64) | 必须 | 本算法第 16.3 节成本落地口径 | 见第 29.6 节状态约束 |
| 成本分摊方法 | `cost_allocation_method` | varchar(64) | 必须 | 本算法第 16.3 节成本落地口径 | V1 默认 `UNIT_COST_BY_STANDARD_QTY` |
| 成本分摊状态 | `cost_allocation_status` | varchar(64) | 必须 | 本算法第 16.3 节成本落地口径 | 见第 29.6 节状态约束 |
| SKU 实付均价 | `sku_avg_paid_price` | decimal(18,6) | 建议 | Doris 小票 | 目标画像该 SKU 实付销售额 / 销售标准量 |
| 销售原价 | `original_price` | decimal(18,6) | 必须 | `mart_store_sku_daily_price.original_sale_price` | 当前价格快照销售原价；缺失写 NULL + `PRICE_SOURCE_MISSING` |
| 目标画像平均实付价 | `target_profile_avg_paid_price` | decimal(18,6) | 必须 | `data_agent.dws_member_order_item_detail_df_all_new.usual_amt/weight` + 本算法第 18 节画像分组聚合 | 目标画像实付金额 / 目标画像销售标准量；分母无效写 NULL |
| 参考画像平均实付价 | `reference_profile_avg_paid_price` | decimal(18,6) | 必须 | `data_agent.dws_member_order_item_detail_df_all_new.usual_amt/weight` + 本算法第 18 节参考画像分组聚合 | 参考画像实付金额 / 参考画像销售标准量；无参考画像写 NULL |
| 标准化成交价格 | `standardized_paid_price` | decimal(18,6) | 必须 | 本算法第 18 节价格指标 | 按标准单位换算后的成交价格；单位不可解释写 NULL |
| 促销前后价格 JSON | `before_after_promotion_price` | json | 必须 | 价格表 + Doris 小票 | JSON 对象，键为 `before_price`、`after_price`、`price_source`；`price_source` 只允许 `PRICE_TABLE_ORIGINAL_DORIS_USUAL_AMT_PER_WEIGHT`；任一来源缺失时整个对象写 `NULL` 并标记 `PRICE_SOURCE_MISSING` |
| 实际折扣率 | `actual_discount_rate` | decimal(18,8) | 必须 | 本算法第 18 节价格指标 | `1 - after_price / before_price`；价格缺失或分母为 0 写 NULL |
| 促销识别方式 | `promotion_identify_method` | varchar(64) | 必须 | 本算法第 15 节折扣代理规则 | V1 固定为 `DISCOUNT_PROXY_V1` |

得分和锚点字段：

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 画像贡献维度分 | `contribution_dimension_score` | decimal(18,8) | 必须 | 本算法第 19.1 节一级评分维度 | 目标画像贡献维度得分 |
| 画像偏好维度分 | `preference_dimension_score` | decimal(18,8) | 必须 | 本算法第 19.2 节一级评分维度 | 目标画像偏好维度得分 |
| 自然动销维度分 | `natural_sales_dimension_score` | decimal(18,8) | 必须 | 本算法第 19.3 节一级评分维度 | 19:30 前自然动销维度得分 |
| 毛利维度分 | `margin_dimension_score` | decimal(18,8) | 必须 | 本算法第 19.4 节一级评分维度 | 商品毛利维度得分 |
| 维度权重 JSON | `dimension_weights_json` | json | 必须 | CRITIC | JSON 对象；键为维度/指标编码，值为 decimal 权重；不适用维度不写键 |
| 点估计观察分 | `point_evidence_score` | decimal(18,8) | 必须 | 本算法第 20-21 节标准化与 CRITIC | 使用后验均值计算的观察分，用于低证据对比 |
| SKU 表现综合分 | `sku_performance_score` | decimal(18,8) | 必须 | 本算法第 21 节两级 CRITIC | 正式保守综合表现分，使用 95% 下界 |
| 选中分组数量 | `selected_cluster_count` | int | 必须 | Jenks/BIC | Jenks+BIC 选择的分组数量 |
| Jenks 分割点 JSON | `jenks_breaks_json` | json | 必须 | Jenks/BIC | JSON 数组；按升序保存各分割点 decimal；K=1 写 `[]` |
| SSE 结果 JSON | `sse_by_k_json` | json | 必须 | Jenks/BIC | JSON 对象；键为字符串形式的 K，值为 SSE decimal |
| BIC 结果 JSON | `bic_by_k_json` | json | 必须 | Jenks/BIC | JSON 对象；键为字符串形式的 K，值为 BIC decimal |
| 表现分组 | `performance_group` | varchar(64) | 必须 | 本算法第 22 章 Jenks+BIC 分组 | 见第 29.6 节状态约束 |
| 是否正式锚点 | `is_formal_anchor` | tinyint | 必须 | 本算法第 23 章正式锚点准入 | `1` 是正式锚点，`0` 不是 |
| 锚点生命周期状态 | `anchor_lifecycle_status` | varchar(64) | 必须 | 本算法第 24 章当前/历史锚点 | 见第 29.6 节状态约束 |
| 锚点证据类型 | `anchor_evidence_type` | varchar(64) | 必须 | 本算法第 23-27 章锚点证据判定 | 见第 29.6 节状态约束 |

稳定性、属性和状态字段：

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| Top1 门店销售占比 | `top1_store_sales_share` | decimal(18,8) | 必须 | 本算法第 25.1 节门店集中度 | 最大单店销售额 / 该 SKU 总销售额 |
| 门店销售 HHI | `store_sales_hhi` | decimal(18,8) | 必须 | 本算法第 25.1 节门店集中度 | 门店销售集中度 |
| 留一门店锚点稳定率 | `leave_one_store_anchor_rate` | decimal(18,8) | 必须 | 本算法第 25.2 节留一门店验证 | 删除单店后仍为锚点的比例 |
| 门店稳定性状态 | `store_stability_status` | varchar(64) | 必须 | 本算法第 25.2 节留一门店验证 | 见第 29.6 节状态约束 |
| 留一月锚点稳定率 | `leave_one_month_anchor_rate` | decimal(18,8) | 必须 | 本算法第 26 章时间稳定性验证 | 删除单月后仍为锚点的比例 |
| 时间稳定性状态 | `time_stability_status` | varchar(64) | 必须 | 本算法第 26 章时间稳定性验证 | 见第 29.6 节状态约束 |
| 主材料 | `main_ingredient` | varchar(128) | 建议 | 商品基础表/商品名称解析 | 商品主材料 |
| 商品形态 | `product_form` | varchar(128) | 建议 | 商品基础表/商品名称解析 | 商品形态 |
| 配料 | `ingredient` | varchar(512) | 建议 | 商品基础表/商品名称解析 | 关键配料 |
| 口味 | `flavor` | varchar(128) | 建议 | 商品基础表/商品名称解析 | 商品口味 |
| 加工方式 | `processing_method` | varchar(128) | 建议 | 商品基础表/商品名称解析 | 加工方式 |
| 烹饪方式 | `cooking_method` | varchar(128) | 建议 | 商品基础表/商品名称解析 | 烹饪方式 |
| 净含量 | `net_content` | decimal(18,6) | 建议 | 商品基础表规格解析 | 商品净含量 |
| 包装类型 | `package_type` | varchar(128) | 建议 | 商品基础表/商品名称解析 | 包装形态 |
| 温层 | `temperature_layer` | varchar(64) | 建议 | `dim_sku.temperature_layer` | 冷藏、冷冻、常温等 |
| 品牌 | `brand_name` | varchar(128) | 建议 | `dim_sku.brand_name` | 商品品牌 |
| 属性来源 JSON | `attribute_source_json` | json | 必须 | 商品基础表/属性加工规则 | JSON 对象；键为属性英文字段名，值为 `MASTER_DATA` / `ATTRIBUTE_DICTIONARY` / `NAME_RULE` / `UNKNOWN` |
| 属性置信度 JSON | `attribute_confidence_json` | json | 必须 | 属性加工规则 | JSON 对象；键为属性英文字段名，值为 decimal 置信度或 `NULL` |
| 商品状态编码 | `product_status_code` | varchar(8) | 建议 | `dim_product_status` | `A` / `O` / `S` / `D` / `B`；V1 不参与评分，缺失写 NULL |
| 商品状态可用性 | `product_status_availability` | varchar(32) | 必须 | `dim_product_status` + 本算法第 18 节商品状态可用性判定 | `AVAILABLE` 或 `NOT_AVAILABLE`；缺失不得编造停售/季节原因 |
| 结果状态 | `result_status` | varchar(64) | 必须 | 本算法第 28 章结果状态设计 | 见第 29.6 节状态约束 |
| 盈利状态 | `profitability_status` | varchar(64) | 必须 | 本算法第 16.4 节毛利底线 | 见第 29.6 节状态约束 |
| 证据状态 | `evidence_status` | varchar(64) | 必须 | 本算法第 13 章统计证据 | 见第 29.6 节状态约束 |
| 自然动销状态 | `natural_sales_status` | varchar(64) | 必须 | 本算法第 14 章自然动销 | 见第 29.6 节状态约束 |
| 订购覆盖状态 | `order_coverage_status` | varchar(64) | 必须 | 本算法第 10.3-10.4 节订购覆盖 | 见第 29.6 节状态约束 |
| 属性状态 | `attribute_status` | varchar(64) | 必须 | 本算法第 17 章商品属性 | 见第 29.6 节状态约束 |
| 数据质量标记 JSON | `data_quality_flags` | json | 必须 | 本算法第 32 章数据质量验收 | JSON 数组；每项为稳定英文标记；无标记写 `[]`；范围回退、字段缺失、冲突等降级必须显式记录 |
| 计算时间 | `calculated_at` | datetime | 必须 | 系统生成 | 结果写入时间 |

### 29.3 标准商品表现：`mart_target_profile_product_performance`

一行代表：一个周期、一个范围、一个门店群、一个消费者画像和一个标准商品的表现结果。

主键：

```text
sku_performance_model_version
+ performance_start_date
+ performance_end_date
+ scope_version
+ scope_type
+ scope_id
+ category_granularity
+ category_code
+ store_group_type
+ final_level
+ final_profile
+ standard_product_key
```

本表由 `mart_target_profile_sku_performance` 聚合得到。V1 优先按商品基础表 `spu_id` 聚合；`spu_id` 缺失时 `standard_product_key = sku_id`，`standard_product_mode = SKU_ONLY`。

标准商品层的在售状态必须在成员 SKU 状态稳定后重新聚合，不能从代表 SKU 直接继承：

```text
1. 成员 SKU 必须使用同一 `listing_snapshot_date` 和 `listing_scope_rule_version`，并先验证有效门店覆盖完整、成员集合无冲突、成员状态均来自同一快照。
2. 任一成员 SKU 状态为 NULL、成员覆盖不足、快照不一致或标准商品成员集合冲突时，标准商品两个字段都写 NULL，并写入 `data_quality_flags`（覆盖/快照不可计算统一使用 `DATA_INSUFFICIENT`；成员集合主键冲突同时使用 `DUPLICATE_KEY`）与 `process_algo04_run_audit`；此时不得继续按 ACTIVE/INACTIVE 推断。
3. 在第 1-2 步通过后，任一成员 SKU 为 ACTIVE，即标准商品 `orderable_sellable_flag = 1`、`listing_status = ACTIVE`（当前 V1 提案 `ANY_ACTIVE_STORE_V1`）。
4. 在第 1-2 步通过后，成员 SKU 全部为 INACTIVE，标准商品 `orderable_sellable_flag = 0`、`listing_status = INACTIVE`。
5. `listing_status = NULL` 只能表示当前在售不可判断，不得转写为 `HISTORICAL_ANCHOR`；历史锚点必须有明确 `listing_status = INACTIVE`。
```

标准商品层的销售额、去重小票/会员、成本、CRITIC、Jenks/BIC 和锚点准入仍按第 17.4 节重新计算；不得把成员 SKU 分数或代表 SKU 状态冒充标准商品结论。

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| SKU 表现模型版本 | `sku_performance_model_version` | varchar(64) | 必须 | 算法 04 参数 | 算法 04 本次计算版本 |
| 数据周期开始日期 | `performance_start_date` | date | 必须 | `mart_target_profile_sku_performance.performance_start_date` + 本算法第 29.3 节标准商品层聚合 | 统计周期开始日期 |
| 数据周期结束日期 | `performance_end_date` | date | 必须 | `mart_target_profile_sku_performance.performance_end_date` + 本算法第 29.3 节标准商品层聚合 | 统计周期结束日期 |
| 范围版本 | `scope_version` | varchar(64) | 必须 | `mart_target_profile_sku_performance.scope_version` + 本算法第 29.3 节标准商品层聚合 | 城市算法区域版本 |
| 范围类型 | `scope_type` | varchar(32) | 必须 | `mart_target_profile_sku_performance.scope_type` + 本算法第 29.3 节标准商品层聚合 | `CITY` / `CITY_CLUSTER` |
| 范围编码 | `scope_id` | varchar(64) | 必须 | `mart_target_profile_sku_performance.scope_id` + 本算法第 29.3 节标准商品层聚合 | 城市或城市群编码 |
| 范围名称 | `scope_name` | varchar(128) | 必须 | `mart_target_profile_sku_performance.scope_name` + 本算法第 29.3 节标准商品层聚合 | 城市或城市群名称 |
| 品类颗粒度 | `category_granularity` | varchar(32) | 必须 | `mart_target_profile_sku_performance.category_granularity` + 本算法第 29.3 节标准商品层聚合 | 大类 / 中类 / 小类 |
| 品类编码 | `category_code` | varchar(64) | 必须 | `mart_target_profile_sku_performance.category_code` + 本算法第 29.3 节标准商品层聚合 | 当前计算品类编码 |
| 品类名称 | `category_name` | varchar(128) | 必须 | `mart_target_profile_sku_performance.category_name` + 本算法第 29.3 节标准商品层聚合 | 当前计算品类名称 |
| 门店群类型 | `store_group_type` | varchar(32) | 必须 | `mart_target_profile_sku_performance.store_group_type` + 本算法第 29.3 节标准商品层聚合 | `FINAL_LEVEL` / `ALL_RATED` |
| 门店品类等级 | `final_level` | varchar(32) | 必须 | `mart_target_profile_sku_performance.final_level` + 本算法第 29.3 节标准商品层聚合 | 当前门店群等级 |
| 消费者画像 | `final_profile` | varchar(128) | 必须 | `mart_target_profile_sku_performance.final_profile` + 本算法第 29.3 节标准商品层聚合 | 目标消费者画像 |
| 会员过滤规则版本 | `member_filter_rule_version` | varchar(64) | 必须 | `mart_target_profile_sku_performance.member_filter_rule_version` + 本算法第 29.3 节标准商品层聚合 | 有效会员过滤规则版本 |
| 门店品类等级开始日期 | `category_level_start_date` | date | 必须 | `mart_target_profile_sku_performance.category_level_start_date` + 本算法第 29.3 节标准商品层聚合 | 算法 02 结果周期开始日期 |
| 门店品类等级结束日期 | `category_level_end_date` | date | 必须 | `mart_target_profile_sku_performance.category_level_end_date` + 本算法第 29.3 节标准商品层聚合 | 算法 02 结果周期结束日期 |
| 消费者贡献开始日期 | `consumer_contribution_start_date` | date | 必须 | `mart_target_profile_sku_performance.consumer_contribution_start_date` + 本算法第 29.3 节标准商品层聚合 | 算法 03 结果周期开始日期 |
| 消费者贡献结束日期 | `consumer_contribution_end_date` | date | 必须 | `mart_target_profile_sku_performance.consumer_contribution_end_date` + 本算法第 29.3 节标准商品层聚合 | 算法 03 结果周期结束日期 |
| 源数据版本 | `source_data_version` | varchar(128) | 必须 | `mart_target_profile_sku_performance.source_data_version` + 本算法第 29.3 节标准商品层聚合 | 统一输入快照版本 |
| 上游版本指纹 | `upstream_version_fingerprint` | varchar(512) | 必须 | `mart_target_profile_sku_performance.upstream_version_fingerprint` + 本算法第 29.3 节标准商品层聚合 | 完整上游版本和源数据指纹 |
| 在售快照日期 | `listing_snapshot_date` | date | 必须 | SKU 表现表 `listing_snapshot_date` + 标准商品层成员 SKU 聚合 | 标准商品层当前可订可售状态使用的锁定快照日期 |
| 在售范围聚合规则版本 | `listing_scope_rule_version` | varchar(64) | 必须 | `mart_target_profile_sku_performance.listing_scope_rule_version` / 调度参数 + 本算法第 10.1.1 节有效门店集合 | 例如 `ANY_ACTIVE_STORE_V1`；标准商品层沿用同批范围规则 |
| 是否可订可售 | `orderable_sellable_flag` | tinyint | 必须 | SKU 表现表 `orderable_sellable_flag` + 本算法第 29.3 节标准商品层聚合 | 成员 SKU 至少一个已确认 ACTIVE 时为 `1`；全量覆盖且全部 INACTIVE 时为 `0`；状态未知或覆盖不足时为 `NULL` |
| 在售状态 | `listing_status` | varchar(64) | 必须 | SKU 表现表 `listing_status` + 本算法第 29.3 节标准商品层聚合 | `ACTIVE` / `INACTIVE` / `NULL`；`NULL` 不得降级为历史锚点 |
| 标准商品主键 | `standard_product_key` | varchar(128) | 必须 | `mart_target_profile_sku_performance.standard_product_key` + 本算法第 17.4、29.3 节归并 | SPU 有效时取 `spu_id`，否则取 `sku_id` |
| 标准商品名称 | `standard_product_name` | varchar(256) | 必须 | `dim_sku.spu_name` / `dim_sku.sku_name` + 本算法第 17.4、29.3 节代表 SKU 归并 | SPU 名称或代表 SKU 名称 |
| 标准商品模式 | `standard_product_mode` | varchar(64) | 必须 | `mart_target_profile_sku_performance.standard_product_mode` + 本算法第 17.4 节标准商品归并 | `SPU_MAPPED` / `SKU_ONLY` |
| SPU 编码 | `spu_id` | varchar(64) | 建议 | `dim_sku.spu_id` | 商品基础表 SPU 编码 |
| SPU 名称 | `spu_name` | varchar(256) | 建议 | `dim_sku.spu_name` | 商品基础表 SPU 名称 |
| 代表 SKU 编码 | `representative_sku_id` | varchar(64) | 必须 | `mart_target_profile_sku_performance.sku_id` + 本算法第 17.4 节标准商品归并 | 展示和追溯使用的代表 SKU |
| 成员 SKU 列表 JSON | `member_sku_list_json` | json | 必须 | `mart_target_profile_sku_performance.sku_id` + 本算法第 17.4 节标准商品归并 | JSON 数组；每项为 `sku_id` 字符串；无成员不写虚假 SKU，写 `[]` |
| 成员 SKU 数 | `member_sku_cnt` | bigint | 必须 | `mart_target_profile_sku_performance.sku_id` + 本算法第 17.4 节标准商品归并 | 标准商品下 SKU 数 |
| 标准商品销售额 | `product_sales_amt` | decimal(18,6) | 必须 | `mart_target_profile_sku_performance` + 本算法第 29.3 节标准商品层重算 | 标准商品层目标画像销售额 |
| 标准商品销售标准量 | `product_sales_qty` | decimal(18,6) | 必须 | `mart_target_profile_sku_performance` + 本算法第 29.3 节标准商品层重算 | 标准商品层目标画像销售标准量 |
| 标准商品小票数 | `product_ticket_cnt` | bigint | 必须 | `mart_target_profile_sku_performance` 明细回溯 + 本算法第 29.3 节去重 | 标准商品层去重小票数 |
| 标准商品购买会员数 | `product_buyer_cnt` | bigint | 必须 | `mart_target_profile_sku_performance` 明细回溯 + 本算法第 29.3 节去重 | 标准商品层去重会员数 |
| 标准商品成本额 | `product_cost_amt` | decimal(18,6) | 必须 | `mart_target_profile_sku_performance` + 本算法第 16.3 节标准商品层成本分摊 | 标准商品层目标画像成本金额 |
| 标准商品毛利额 | `product_margin_amt` | decimal(18,6) | 必须 | `mart_target_profile_sku_performance` + 本算法第 29.3 节标准商品层重算 | 标准商品层目标画像毛利额 |
| 标准商品毛利率 | `product_margin_rate` | decimal(18,8) | 必须 | `mart_target_profile_product_performance.product_margin_amt/product_sales_amt` | 标准商品层目标画像毛利率 |
| 标准商品总销售额 | `product_total_sales_amt` | decimal(18,6) | 必须 | `valid_all_txn` + 本算法第 29.3 节标准商品层聚合 | 标准商品层全量销售额 |
| 标准商品总毛利额 | `product_total_margin_amt` | decimal(18,6) | 必须 | `mart_sku_margin_loss.full_link_margin_amt` + 本算法第 29.3 节标准商品层聚合 | 标准商品层全量毛利额 |
| 标准商品目标画像渗透率 | `product_target_penetration` | decimal(18,8) | 必须 | `mart_target_profile_sku_performance` 明细回溯 + 本算法第 29.3 节标准商品层重算 | 目标画像标准商品购买会员数 / 目标画像品类购买会员数 |
| 标准商品参考画像渗透率 | `product_reference_penetration` | decimal(18,8) | 必须 | `mart_target_profile_sku_performance` 明细回溯 + 本算法第 29.3 节标准商品层重算 | 参考画像标准商品购买会员数 / 参考画像品类购买会员数 |
| 标准商品偏好指数 95% 下界 | `product_preference_lower_95` | decimal(18,8) | 必须 | 本算法第 29.3 节标准商品层 Jeffreys 重算 | 标准商品层正式评分使用的偏好下界；无参考画像写 NULL |
| 标准商品画像贡献维度分 | `product_contribution_dimension_score` | decimal(18,8) | 必须 | 本算法第 29.3 节标准商品层 CRITIC 重算 | 标准商品层 CRITIC 贡献维度分 |
| 标准商品画像偏好维度分 | `product_preference_dimension_score` | decimal(18,8) | 必须 | 本算法第 29.3 节标准商品层 CRITIC 重算 | 标准商品层 CRITIC 偏好维度分；无参考画像写 NULL |
| 标准商品自然动销维度分 | `product_natural_sales_dimension_score` | decimal(18,8) | 必须 | 本算法第 29.3 节标准商品层 CRITIC 重算 | 标准商品层 CRITIC 自然动销维度分 |
| 标准商品毛利维度分 | `product_margin_dimension_score` | decimal(18,8) | 必须 | 本算法第 29.3 节标准商品层 CRITIC 重算 | 标准商品层 CRITIC 毛利维度分 |
| 标准商品维度权重 JSON | `product_dimension_weights_json` | json | 必须 | 本算法第 29.3 节标准商品层 CRITIC 参数 | JSON 对象；键为维度编码，值为权重 |
| 标准商品综合表现分 | `product_performance_score` | decimal(18,8) | 必须 | 本算法第 29.3 节标准商品层 CRITIC 重算 | 标准商品层综合表现分 |
| 标准商品选中分组数量 | `product_selected_cluster_count` | int | 必须 | 本算法第 29.3 节标准商品层 Jenks/BIC 重算 | 标准商品层选中的 K；K=1 时不产生正式高表现组 |
| 标准商品 Jenks 分割点 JSON | `product_jenks_breaks_json` | json | 必须 | 本算法第 29.3 节标准商品层 Jenks/BIC 重算 | JSON 数组；无分割点写 `[]` |
| 标准商品 SSE JSON | `product_sse_by_k_json` | json | 必须 | 本算法第 29.3 节标准商品层 Jenks/BIC 重算 | JSON 对象；键为 K，值为 SSE |
| 标准商品 BIC JSON | `product_bic_by_k_json` | json | 必须 | 本算法第 29.3 节标准商品层 Jenks/BIC 重算 | JSON 对象；键为 K，值为 BIC |
| 表现分组 | `performance_group` | varchar(64) | 必须 | 本算法第 29.3 节标准商品层 Jenks/BIC 重算 | 见第 29.6 节状态约束 |
| 是否正式锚点 | `is_formal_anchor` | tinyint | 必须 | 本算法第 23 章标准商品层锚点准入 | `1` 是正式锚点，`0` 不是 |
| 锚点生命周期状态 | `anchor_lifecycle_status` | varchar(64) | 必须 | 本算法第 24 章标准商品层当前/历史锚点 | 见第 29.6 节状态约束 |
| 锚点证据类型 | `anchor_evidence_type` | varchar(64) | 必须 | 本算法第 23-27 章标准商品层证据判定 | 见第 29.6 节状态约束 |
| 标准商品盈利状态 | `profitability_status` | varchar(64) | 必须 | 本算法第 29.3 节标准商品层毛利重算 | 目标画像和整体标准商品毛利底线状态 |
| 标准商品证据状态 | `evidence_status` | varchar(64) | 必须 | 本算法第 29.3 节标准商品层统计重算 | 标准商品层统计证据状态 |
| 标准商品自然动销状态 | `natural_sales_status` | varchar(64) | 必须 | 本算法第 29.3 节标准商品层自然动销重算 | 标准商品层自然动销窗口状态 |
| 标准商品门店稳定性状态 | `store_stability_status` | varchar(64) | 必须 | 本算法第 29.3 节标准商品层留一门店重算 | 标准商品层留一门店状态 |
| 标准商品时间稳定性状态 | `time_stability_status` | varchar(64) | 必须 | 本算法第 29.3 节标准商品层留一月重算 | 标准商品层留一月状态 |
| 结果状态 | `result_status` | varchar(64) | 必须 | 本算法第 28 章结果状态设计 / 第 29.3 节标准商品层 | 见第 29.6 节状态约束 |
| 上游闸门状态 | `upstream_gate_status` | varchar(64) | 必须 | `mart_target_profile_sku_performance.upstream_gate_status` + 本算法第 29.3 节标准商品层发布闸门 | 上游结果、版本和周期是否允许标准商品层发布 |
| 数据质量标记 JSON | `data_quality_flags` | json | 必须 | `mart_target_profile_sku_performance.data_quality_flags` + 本算法第 32 章标准商品层质量聚合 | JSON 数组；成员 SKU 质量标记去重汇总；无质量问题写 `[]` |
| 计算时间 | `calculated_at` | datetime | 必须 | 系统生成 | 结果写入时间 |

### 29.4 锚点汇总：`mart_target_profile_anchor_summary`

一行代表：一个周期、一个范围、一个门店群和一个消费者画像下的锚点汇总结果。

主键：

```text
sku_performance_model_version
+ performance_start_date
+ performance_end_date
+ scope_version
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
6. 标准商品成员状态冲突、覆盖不足、快照不一致或成员集合冲突时，canonical 实体保留诊断行但不进入正式锚点 JSON/计数。
```

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| SKU 表现模型版本 | `sku_performance_model_version` | varchar(64) | 必须 | 算法 04 参数 | 算法 04 本次计算版本 |
| 数据周期开始日期 | `performance_start_date` | date | 必须 | 调度参数 | 统计周期开始日期 |
| 数据周期结束日期 | `performance_end_date` | date | 必须 | 调度参数 | 统计周期结束日期 |
| 范围版本 | `scope_version` | varchar(64) | 必须 | `dim_city_algorithm_region` 数据快照 / 调度参数 | 城市算法区域版本 |
| 范围类型 | `scope_type` | varchar(32) | 必须 | `dim_city_algorithm_region` + 本算法范围映射 | `CITY` / `CITY_CLUSTER` |
| 范围编码 | `scope_id` | varchar(64) | 必须 | `dim_city_algorithm_region.algorithm_region_code` / 本算法范围映射 | 城市或城市群编码 |
| 范围名称 | `scope_name` | varchar(128) | 必须 | `dim_city_algorithm_region.algorithm_region_name` / 本算法范围映射 | 城市或城市群名称 |
| 品类颗粒度 | `category_granularity` | varchar(32) | 必须 | `dim_sku` + 本算法品类颗粒度映射 | 大类 / 中类 / 小类 |
| 品类编码 | `category_code` | varchar(64) | 必须 | `dim_sku.category_level1_code/category_level2_code/category_level3_code` + 本算法品类颗粒度映射 | 当前计算品类编码 |
| 品类名称 | `category_name` | varchar(128) | 必须 | `dim_sku.category_level1_name/category_level2_name/category_level3_name` + 本算法品类颗粒度映射 | 当前计算品类名称 |
| 门店群类型 | `store_group_type` | varchar(32) | 必须 | `mart_store_category_level.final_level` + 本算法第 3.1 节范围分组 | `FINAL_LEVEL` / `ALL_RATED` |
| 门店品类等级 | `final_level` | varchar(32) | 必须 | `mart_store_category_level.final_level` | 当前门店群等级 |
| 消费者画像 | `final_profile` | varchar(128) | 必须 | `dim_customer_profile.final_profile` / `mart_store_group_consumer_contribution.final_profile` | 当前消费者画像 |
| 会员过滤规则版本 | `member_filter_rule_version` | varchar(64) | 必须 | `dim_customer_profile` / `mart_store_group_consumer_contribution` | 有效会员过滤规则版本 |
| 门店品类等级开始日期 | `category_level_start_date` | date | 必须 | `mart_store_category_level` | 算法 02 结果周期开始日期 |
| 门店品类等级结束日期 | `category_level_end_date` | date | 必须 | `mart_store_category_level` | 算法 02 结果周期结束日期 |
| 消费者贡献开始日期 | `consumer_contribution_start_date` | date | 必须 | `mart_store_group_consumer_contribution.contribution_start_date`（本卡别名） | 算法 03 结果周期开始日期 |
| 消费者贡献结束日期 | `consumer_contribution_end_date` | date | 必须 | `mart_store_group_consumer_contribution.contribution_end_date`（本卡别名） | 算法 03 结果周期结束日期 |
| 源数据版本 | `source_data_version` | varchar(128) | 必须 | 调度参数 + 输入快照 | 统一输入快照版本 |
| 上游版本指纹 | `upstream_version_fingerprint` | varchar(512) | 必须 | 本算法第 4.2 节版本指纹生成 | 完整上游版本、周期、规则和源数据指纹 |
| 在售快照日期 | `listing_snapshot_date` | date | 必须 | SKU 表现表 / 标准商品表现表 | 锚点汇总所引用的当前可订可售快照日期 |
| 在售范围聚合规则版本 | `listing_scope_rule_version` | varchar(64) | 必须 | 调度参数 + 本算法第 10.1.1 节有效门店集合 | 例如 `ANY_ACTIVE_STORE_V1`；用于解释当前/历史锚点判定 |
| 当前锚点 SKU JSON | `active_anchor_skus_json` | json | 必须 | `canonical_anchor_set`（由本算法第 29.4.1 节按 SKU/标准商品表现表生成） | JSON 数组；每项为 canonical 实体，至少含 `standard_product_key`、`representative_sku_id`、`source_layer`、`anchor_lifecycle_status`、`performance_score`；无结果写 `[]` |
| 历史锚点 SKU JSON | `historical_anchor_skus_json` | json | 必须 | `canonical_anchor_set` + 本算法第 29.4.1 节筛选 | JSON 数组；每项为 canonical 实体，至少含 `standard_product_key`、`representative_sku_id`、`source_layer`、`anchor_lifecycle_status`、`listing_status`；无结果写 `[]` |
| 低订购高表现 SKU JSON | `low_order_high_performance_skus_json` | json | 必须 | `canonical_anchor_set` + 本算法第 29.4.1 节筛选 | JSON 数组；每项至少含 canonical 实体键、`representative_sku_id`、`source_layer`、`store_order_rate`、`performance_score`；SKU 证据放 `evidence_sku_ids`；无结果写 `[]` |
| 时间敏感锚点 SKU JSON | `time_sensitive_anchor_skus_json` | json | 必须 | `canonical_anchor_set` + 本算法第 29.4.1 节筛选 | JSON 数组；每项至少含 canonical 实体键、`representative_sku_id`、`source_layer`、`time_stability_status`；无结果写 `[]` |
| 门店集中锚点 SKU JSON | `store_concentrated_anchor_skus_json` | json | 必须 | `canonical_anchor_set` + 本算法第 29.4.1 节筛选 | JSON 数组；每项至少含 canonical 实体键、`representative_sku_id`、`source_layer`、`store_stability_status`；无结果写 `[]` |
| 相对锚点候选 JSON | `relative_anchor_candidates_json` | json | 必须 | `canonical_anchor_set` + 本算法第 29.4.1 节筛选 | JSON 数组；每项至少含 canonical 实体键、`representative_sku_id`、`source_layer`、`anchor_evidence_type`、`result_status`；无结果写 `[]` |
| 正式锚点数量 | `formal_anchor_cnt` | bigint | 必须 | `canonical_anchor_set` + 本算法第 29.4.1 节汇总 | canonical 实体中 `is_formal_anchor = 1` 的数量；同一 `standard_product_key` 只计 1 次 |
| 历史锚点数量 | `historical_anchor_cnt` | bigint | 必须 | `canonical_anchor_set` + 本算法第 29.4.1 节汇总 | canonical 实体中生命周期为 `HISTORICAL_ANCHOR` 的数量；同一 `standard_product_key` 只计 1 次 |
| 结果状态 | `result_status` | varchar(64) | 必须 | 本算法第 28 章结果状态设计 / 第 29.4 节锚点汇总 | 见第 29.6 节状态约束 |
| 上游闸门状态 | `upstream_gate_status` | varchar(64) | 必须 | 本算法第 2.2 节 | 上游结果、版本和周期是否允许锚点汇总发布 |
| 质量指标 JSON | `quality_metrics_json` | json | 必须 | 本算法第 29.6.1 节 JSON 结构约束 + 第 32 章质量验收 | JSON 对象；至少含 `sku_cnt`、`valid_sku_cnt`、`formal_anchor_cnt`、`reconciliation_status`、`missing_field_cnt`；无法计算的值写 JSON `null` |
| 数据质量标记 JSON | `data_quality_flags` | json | 必须 | `mart_target_profile_sku_performance.data_quality_flags` / `mart_target_profile_product_performance.data_quality_flags` + `canonical_anchor_set` + 本算法第 32 章汇总 | JSON 数组；汇总范围内质量标记去重后写入；无质量问题写 `[]` |
| 计算时间 | `calculated_at` | datetime | 必须 | 系统生成 | 结果写入时间 |

### 29.5 参数表：`mart_target_profile_sku_performance_params`

一行代表：一个参数版本、一个参数作用范围和一个参数的复算配置。

主键：

```text
sku_performance_model_version
+ parameter_scope_key
+ param_group
+ param_code
```

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| SKU 表现模型版本 | `sku_performance_model_version` | varchar(64) | 必须 | 算法 04 参数 | 算法 04 本次计算版本 |
| 参数作用范围键 | `parameter_scope_key` | varchar(256) | 必须 | 本算法第 29.5 节参数作用范围生成 | 范围、品类、门店群、画像等组成的参数作用范围 |
| 会员画像版本 | `profile_model_version` | varchar(64) | 必须 | 算法 01 `dim_customer_profile` | 参数对应的会员画像版本 |
| 会员过滤规则版本 | `member_filter_rule_version` | varchar(64) | 必须 | 算法 01/03 正式结果 | 参数对应的会员过滤规则版本 |
| 门店品类等级版本 | `category_level_model_version` | varchar(64) | 必须 | 算法 02 `mart_store_category_level` | 参数对应的门店等级版本 |
| 门店品类等级开始日期 | `category_level_start_date` | date | 必须 | 算法 02 正式结果 | 参数对应的算法 02 周期开始 |
| 门店品类等级结束日期 | `category_level_end_date` | date | 必须 | 算法 02 正式结果 | 参数对应的算法 02 周期结束 |
| 门店品类等级周期 | `category_level_period` | varchar(32) | 必须 | 算法 02 正式结果 | 参数对应的算法 02 周期，格式 `start/end` |
| 消费者贡献版本 | `consumer_contribution_model_version` | varchar(64) | 必须 | 算法 03 `mart_store_group_consumer_contribution` | 参数对应的消费者贡献版本 |
| 消费者贡献开始日期 | `consumer_contribution_start_date` | date | 必须 | `mart_store_group_consumer_contribution.contribution_start_date`（本卡别名） | 参数对应的算法 03 周期开始 |
| 消费者贡献结束日期 | `consumer_contribution_end_date` | date | 必须 | `mart_store_group_consumer_contribution.contribution_end_date`（本卡别名） | 参数对应的算法 03 周期结束 |
| 消费者贡献周期 | `consumer_contribution_period` | varchar(32) | 必须 | 算法 03 正式结果 | 参数对应的算法 03 周期，格式 `start/end` |
| 源数据版本 | `source_data_version` | varchar(128) | 必须 | 调度参数 + 输入快照 | 参数使用的统一输入快照版本 |
| 上游版本指纹 | `upstream_version_fingerprint` | varchar(512) | 必须 | 本算法第 4.2 节版本指纹生成 | 参数使用的完整版本指纹 |
| 在售范围聚合规则版本 | `listing_scope_rule_version` | varchar(64) | 必须 | 调度参数 + 本算法第 10.1.1 节有效门店集合 | 例如 `ANY_ACTIVE_STORE_V1`；参数变更必须全量重算 |
| 参数分组 | `param_group` | varchar(64) | 必须 | 本算法第 20-22、11、15、16、10.1 章参数生成 | `CRITIC` / `JENKS_BIC` / `JEFFREYS` / `UNIT_MAPPING` / `COST` / `PROMOTION` / `LISTING_SCOPE` |
| 参数编码 | `param_code` | varchar(128) | 必须 | 本算法第 29.5 节参数编码规则 | 参数唯一编码 |
| 参数名称 | `param_name` | varchar(256) | 必须 | 本算法第 29.5 节参数字典 | 参数中文名称 |
| 指标编码 | `metric_code` | varchar(128) | 建议 | 本算法第 20-22 章指标定义 | 参数对应的指标编码 |
| 参数数值 | `param_value_decimal` | decimal(18,8) | 建议 | 本算法第 20-22 章参数计算 | 数值型参数 |
| 参数文本值 | `param_value_text` | varchar(512) | 建议 | 本算法第 29.5 节参数字典 | 文本型参数 |
| 参数 JSON 值 | `param_value_json` | json | 建议 | 本算法第 15、20-22 章参数计算 | JSON 对象或数组；结构由 `param_code` 决定，必须写入结构版本和键名；无 JSON 参数写 `NULL` |
| 样本数 | `sample_cnt` | bigint | 建议 | 本算法第 13、20-22 章样本统计 | 参数计算使用的样本数 |
| 是否回退 | `fallback_flag` | tinyint | 必须 | 本算法第 20.3、21.4、11.1 节回退判定 | `1` 使用回退参数，`0` 未回退 |
| 回退原因 | `fallback_reason` | varchar(512) | 建议 | 本算法第 20.3、21.4、11.1 节回退判定 | 样本不足、MAD 为 0、单位未知等原因 |
| 关联算法步骤 | `algorithm_step` | varchar(128) | 必须 | 本算法第 29.5 节参数关联步骤 | 该参数用于哪个计算步骤 |
| 计算时间 | `calculated_at` | datetime | 必须 | 系统生成 | 参数写入时间 |

### 29.5.1 过程审计表：`process_algo04_run_audit`

该表只记录每次算法 04 运行和字段级闸门结果，不作为下游业务结果。上游缺失、主键重复、金额对账失败、物理字段缺失或重跑时必须写入；正式结果阻断时也必须保留审计记录。

一行代表：一个运行批次、一个范围/品类/门店群/画像处理单元和一个审计事件。

主键：

```text
run_id + audit_scope_key + audit_event_code
```

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 运行批次ID | `run_id` | varchar(64) | 必须 | 调度系统 | 本次算法 04 运行唯一标识 |
| 算法版本 | `sku_performance_model_version` | varchar(64) | 必须 | 本算法参数 | 本次算法 04 版本 |
| 数据周期开始日期 | `performance_start_date` | date | 必须 | 调度参数 | 本次计算周期开始 |
| 数据周期结束日期 | `performance_end_date` | date | 必须 | 调度参数 | 本次计算周期结束 |
| 审计范围键 | `audit_scope_key` | varchar(512) | 必须 | 本算法范围键 | 范围、品类、门店群和画像组合 |
| 上游版本指纹 | `upstream_version_fingerprint` | varchar(512) | 必须 | 本算法第 4.2 节版本指纹生成 | 完整输入版本指纹 |
| 在售范围聚合规则版本 | `listing_scope_rule_version` | varchar(64) | 必须 | 调度参数 + 本算法第 10.1.1 节有效门店集合 | 例如 `ANY_ACTIVE_STORE_V1`；用于追溯本次在售聚合规则 |
| 审计事件编码 | `audit_event_code` | varchar(128) | 必须 | 本算法第 2.2、6、32 章闸门事件定义 | 例如 `UPSTREAM_RESULT_MISSING`、`DUPLICATE_KEY`、`RECONCILIATION_FAILED` |
| 审计状态 | `audit_status` | varchar(32) | 必须 | 本算法第 32 章质量闸门 | `PASS` / `BLOCKED` / `WARNING` |
| 审计明细 JSON | `audit_detail_json` | json | 必须 | 本算法第 32 章质量闸门 | JSON 对象；包含表名、字段、样本数、差异值和处理动作；无明细写 `{}` |
| 正式结果写入标记 | `formal_write_flag` | tinyint | 必须 | 本算法第 2.3、2.4 节写入边界 | `1` 已允许正式写入，`0` 未允许 |
| 计算时间 | `calculated_at` | datetime | 必须 | 系统生成 | 审计写入时间 |

### 29.6 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
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
| `repurchase_calc_status` | 复购计算状态 | `OK` | 复购计算成功 | 分母大于 0 且观察窗口完整 |
| `repurchase_calc_status` | 复购计算状态 | `DENOMINATOR_ZERO` | 复购分母为 0 | 可观察首购会员数为 0 |
| `repurchase_calc_status` | 复购计算状态 | `INSUFFICIENT_WINDOW` | 观察窗口不足 | 周期尾部无法观察完整 T+1 到 T+7 |
| `audit_status` | 审计状态 | `PASS` | 审计通过 | 本项质量检查通过 |
| `audit_status` | 审计状态 | `BLOCKED` | 审计阻断 | 本项失败，禁止写入受影响正式结果 |
| `audit_status` | 审计状态 | `WARNING` | 审计警告 | 可保留诊断，但需写明降级或缺失 |
| `formal_write_flag` | 正式结果写入标记 | `1` | 允许正式写入 | 该范围通过字段级交付闸门 |
| `formal_write_flag` | 正式结果写入标记 | `0` | 禁止正式写入 | 上游、字段、对账或质量闸门未通过 |
| `upstream_gate_status` | 上游闸门状态 | `PASS` | 上游可消费 | 必需上游表、版本、周期和唯一性均通过 |
| `upstream_gate_status` | 上游闸门状态 | `UPSTREAM_RESULT_MISSING` | 上游正式结果缺失 | 算法 02/03 正式表或必要字段未交付 |
| `upstream_gate_status` | 上游闸门状态 | `UPSTREAM_VERSION_ERROR` | 上游版本不一致 | 上游周期、范围或版本指纹不一致 |
| `valid_transaction_filter_method` | 有效交易过滤方式 | `SOURCE_TABLE_CLEANED` | 源表已清洗 | 数据开发确认 Doris 主表已保留有效正向销售 |
| `valid_transaction_filter_method` | 有效交易过滤方式 | `RULE_FILTERED` | 算法任务内过滤 | 算法 04 按 `order_status`、`is_return`、`usual_amt`、`weight` 等字段过滤 |
| `standard_product_mode` | 标准商品模式 | `SPU_MAPPED` | 已按 SPU 归并 | 商品基础表有有效 `spu_id` |
| `standard_product_mode` | 标准商品模式 | `SKU_ONLY` | 只按销售 SKU 计算 | `spu_id` 为空或无法稳定映射 |
| `orderable_sellable_flag` | 是否可订可售 | `1` | 当前范围快照可订且可售 | SKU 层按第 10.1 节、标准商品层按第 29.3 节完成有效门店/成员覆盖校验后判定为可订可售 |
| `orderable_sellable_flag` | 是否可订可售 | `0` | 当前范围快照已确认不可订或不可售 | SKU 层有效状态覆盖完整且均不满足可订可售；标准商品层成员状态覆盖完整且全部为 INACTIVE |
| `orderable_sellable_flag` | 是否可订可售 | `NULL` | 在售状态不可判断 | 候选/有效门店覆盖不足、无有效状态行、快照不一致、成员状态未知或主键冲突；同时写运行审计，不进入正式锚点 |
| `listing_status` | 在售状态 | `ACTIVE` | 当前范围内可订可售 | SKU 层按第 10.1 节、标准商品层按第 29.3 节判定为 `orderable_sellable_flag = 1` |
| `listing_status` | 在售状态 | `INACTIVE` | 当前范围内不可订或不可售 | SKU 层有效状态覆盖完整且均不满足 `is_saleable = 1 AND is_orderable = 1`；标准商品层成员状态覆盖完整且全部为 INACTIVE |
| `listing_status` | 在售状态 | `NULL` | 在售状态不可判断 | 候选/有效门店覆盖不足、无有效状态行、快照不一致、成员状态未知或主键冲突；同时写运行审计，不进入正式锚点，也不得转成 `HISTORICAL_ANCHOR` |
| `orderable_scope` | 订购范围口径 | `STORE_SKU_ORDERABLE` | 门店 SKU 可订范围 | 仅在可订可售表按合同稳定交付并通过覆盖验收后使用 |
| `orderable_scope` | 订购范围口径 | `GROUP_ALL_STORES` | 门店群全部门店兼容回退 | 仅当合同批准的全局可订范围事实带版本/快照来源且门店级范围不可用时使用；只解决分母范围，不补造订购分子，并写 `ORDERABLE_SCOPE_DEGRADED` |
| `orderable_scope` | 订购范围口径 | `NULL` | 订购范围不可判断 | 门店级可订范围缺失或字段不完整，且没有经批准的全局可订范围事实；同时将订购覆盖字段写 `NULL + DATA_INSUFFICIENT` 并记录运行审计 |
| `measurement_mapping_status` | 计量映射状态 | `MAPPED` | 计量单位可识别 | 商品基础表单位可映射到重量或数量 |
| `measurement_mapping_status` | 计量映射状态 | `UNKNOWN` | 计量单位未知 | 商品基础表单位缺失或无法识别 |
| `measurement_mapping_status` | 计量映射状态 | `UNIT_CONVERSION_ERROR` | 单位换算异常 | 单位重量或换算系数缺失且指标必须换算 |
| `cost_source` | 成本来源 | `FULL_CHAIN_MARGIN_DERIVED_COST` | 全链路毛利反推成本 | 使用毛利损耗表销售额和全链路毛利额反推成本 |
| `cost_source` | 成本来源 | `ARRIVAL_COST_TAX_INCLUDED` | 出库到店含税成本 | 全链路毛利口径无法稳定取数时，使用门店商品日价格表出库到店成本含税作为备选 |
| `cost_source` | 成本来源 | `SOURCE_MISSING` | 成本来源缺失 | 毛利损耗表缺少销售额或全链路毛利额 |
| `cost_allocation_method` | 成本分摊方法 | `UNIT_COST_BY_STANDARD_QTY` | 按销售标准量单位成本分摊 | V1 默认口径，`weight` 作为销售标准量 |
| `cost_allocation_method` | 成本分摊方法 | `SALES_AMOUNT_SHARE_DEGRADED` | 销售额占比分摊降级 | 个别 SKU 或日期销售标准量异常时的兜底口径 |
| `cost_allocation_status` | 成本分摊状态 | `COST_ALLOCATED_V1` | 成本分摊成功 | 销售标准量和成本分母均有效，使用默认单位成本口径 |
| `cost_allocation_status` | 成本分摊状态 | `COST_ALLOCATED_DEGRADED` | 成本分摊降级成功 | 销售标准量异常，使用销售额占比分摊兜底 |
| `cost_allocation_status` | 成本分摊状态 | `COST_NOT_ALLOCATED` | 成本未分摊 | 默认口径和降级口径都不能可靠计算 |
| `cost_allocation_status` | 成本分摊状态 | `SOURCE_MISSING` | 成本分摊来源缺失 | 成本或销售标准量来源缺失 |
| `cost_allocation_status` | 成本分摊状态 | `ZERO_DENOMINATOR` | 成本分摊分母为 0 | 该日门店 SKU 总销售标准量为 0 |
| `promotion_identify_method` | 促销识别方式 | `DISCOUNT_PROXY_V1` | 折扣代理口径 | V1 无促销活动表，使用 `discount_amt > 0` 识别促销代理 |
| `preference_reference_status` | 偏好参考组状态 | `HAS_REFERENCE_PROFILE` | 有参考画像 | 同一比较组内存在非目标画像有效消费 |
| `preference_reference_status` | 偏好参考组状态 | `NO_REFERENCE_PROFILE` | 没有参考画像 | 同一比较组只有目标画像；对应原始业务规则的 `NO_REFERENCE_PROFILE`，偏好指数不适用 |
| `result_status` | 结果状态 | `SUCCESS` | 计算成功 | 当前比较组正常产出结果 |
| `result_status` | 结果状态 | `SINGLE_SKU` | 只有一个有效 SKU | 比较组内只有 1 个有效 SKU |
| `result_status` | 结果状态 | `NO_OBVIOUS_HIGH_SKU` | 无明显高表现 SKU | Jenks/BIC 未形成高表现组 |
| `result_status` | 结果状态 | `NO_TARGET_PROFILE_CONSUMPTION` | 目标画像无有效消费 | 当前范围目标画像没有有效消费 |
| `result_status` | 结果状态 | `NO_VALID_SKU` | 无有效 SKU | 商品、交易或在售过滤后无有效 SKU |
| `result_status` | 结果状态 | `DATA_INCOMPLETE` | 数据不完整 | 核心输入缺失但可保留诊断 |
| `result_status` | 结果状态 | `PRODUCT_MASTER_CONFLICT` | 商品主数据冲突 | 同一销售 SKU 匹配多条当前商品基础记录 |
| `result_status` | 结果状态 | `SELL_THROUGH_DATA_ERROR` | 售罄数据异常 | 到货或销售标准量无法构造有效售罄率 |
| `result_status` | 结果状态 | `UPSTREAM_VERSION_ERROR` | 上游版本错误 | 算法 01/02/03 混用多个正式版本或缺失 |
| `result_status` | 结果状态 | `UPSTREAM_RESULT_MISSING` | 上游正式结果缺失 | 必要上游正式表或字段未交付；只写审计，不写正式明细 |
| `result_status` | 结果状态 | `NOT_CALCULABLE` | 当前单元不可计算 | 上游状态为 NOT_CALCULABLE 或核心分母/字段不可用 |
| `result_status` | 结果状态 | `UPSTREAM_RECONCILIATION_ERROR` | 上游对账异常 | 与算法 03 销售额、会员数或门店群对账失败 |
| `profitability_status` | 盈利状态 | `POSITIVE_MARGIN` | 毛利为正 | 目标画像 SKU 毛利额大于 0 |
| `profitability_status` | 盈利状态 | `NON_POSITIVE_MARGIN` | 毛利非正 | 目标画像 SKU 毛利额小于等于 0 |
| `profitability_status` | 盈利状态 | `COST_SOURCE_MISSING` | 成本来源缺失 | 无法计算目标画像 SKU 毛利 |
| `evidence_status` | 证据状态 | `SUFFICIENT` | 证据充分 | 渗透、复购、偏好等样本达到正式评分要求 |
| `evidence_status` | 证据状态 | `LOW_EVIDENCE` | 低证据 | 小样本或区间下界不足，不能作为正式锚点 |
| `time_stability_status` | 时间稳定性状态 | `STABLE` | 时间稳定 | 留一月验证仍保持锚点或高表现 |
| `time_stability_status` | 时间稳定性状态 | `TIME_SENSITIVE` | 时间敏感 | 只在特定月份或时段表现突出 |
| `time_stability_status` | 时间稳定性状态 | `INSUFFICIENT_TIME_SAMPLE` | 时间样本不足 | 有效月份不足以做稳定性验证 |
| `store_stability_status` | 门店稳定性状态 | `STABLE` | 门店稳定 | 留一门店验证仍保持锚点或高表现 |
| `store_stability_status` | 门店稳定性状态 | `STORE_CONCENTRATED` | 门店集中 | 表现集中在少数门店 |
| `store_stability_status` | 门店稳定性状态 | `INSUFFICIENT_STORE_SAMPLE` | 门店样本不足 | 有效门店不足以做稳定性验证 |
| `natural_sales_status` | 自然动销状态 | `VALID` | 自然动销有效 | 存在可计算的 19:30 前非促销自然动销窗口 |
| `natural_sales_status` | 自然动销状态 | `NO_NATURAL_SALES_WINDOW` | 无自然销售窗口 | 全部销售依赖促销代理或时段折扣 |
| `order_coverage_status` | 订购覆盖状态 | `HIGH` | 订购覆盖高 | 订购覆盖位于高覆盖组 |
| `order_coverage_status` | 订购覆盖状态 | `LOW` | 订购覆盖低 | 订购覆盖低但表现可单独解释 |
| `order_coverage_status` | 订购覆盖状态 | `NO_OBVIOUS_SPLIT` | 无明显分组 | 订购覆盖未形成明显高低分组 |
| `order_coverage_status` | 订购覆盖状态 | `DATA_INSUFFICIENT` | 订购覆盖不可计算 | 没有商品计量类型对应的真实 `order_qty` 或 `order_weight_kg`，或没有可订范围字段 |
| `attribute_status` | 属性状态 | `COMPLETE` | 属性较完整 | 商品属性满足解释字段要求 |
| `attribute_status` | 属性状态 | `ATTRIBUTE_INCOMPLETE` | 属性不完整 | 商品属性缺失，不阻断经营表现计算 |
| `attribute_source_json` | 属性来源 JSON | 对象值 `MASTER_DATA` / `ATTRIBUTE_DICTIONARY` / `NAME_RULE` / `UNKNOWN` | 每个属性的来源闭集 | JSON 对象的每个键必须是正式属性字段名；未知来源写 `UNKNOWN` |
| `attribute_confidence_json` | 属性置信度 JSON | 对象值为 0-1 decimal 或 `NULL` | 每个属性的识别置信度 | 键必须与 `attribute_source_json` 一致 |
| `data_quality_flags` | 数据质量标记 JSON | 数组值 `PRICE_SOURCE_MISSING` / `UNIT_CONVERSION_ERROR` / `DUPLICATE_KEY` / `RECONCILIATION_FAILED` / `DATA_INSUFFICIENT` / `COST_ALLOCATION_DEGRADED` / `ORDERABLE_SCOPE_DEGRADED` | 数据质量问题集合 | 无问题写 `[]`；使用全局可订范围兼容回退时必须包含 `ORDERABLE_SCOPE_DEGRADED`；不得用自由中文替代稳定英文标记 |
| `sse_by_k_json.status` / `bic_by_k_json.status` | 分组参数 JSON 状态 | `CALCULATED` | 已计算 | 至少有一个有效消费者类型且对应 K 值按第 22 章完成计算 |
| `sse_by_k_json.status` / `bic_by_k_json.status` | 分组参数 JSON 状态 | `NOT_APPLICABLE` | 不适用 | 单一有效类型或本结果不需要运行 Jenks/BIC；K 值写 `null` |
| `sse_by_k_json.status` / `bic_by_k_json.status` | 分组参数 JSON 状态 | `NOT_CALCULABLE` | 无法计算 | 上游/核心分母/字段闸门阻断；K 值写 `null`，不伪造参数 |
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
| `fallback_flag` | 是否回退 | `0` / `1` | 参数是否使用回退 | 参数表中 `1` 表示该参数因样本不足、MAD 为 0、单位未知等原因使用回退口径 |
| `param_group` | 参数分组 | `CRITIC` | CRITIC 参数 | 维度内或维度间动态权重、相关矩阵 |
| `param_group` | 参数分组 | `JENKS_BIC` | Jenks/BIC 参数 | 动态分组、断点、SSE 和 BIC |
| `param_group` | 参数分组 | `JEFFREYS` | Jeffreys 参数 | 统计先验、区间和下界 |
| `param_group` | 参数分组 | `UNIT_MAPPING` | 计量映射参数 | 单位、换算和计量类型 |
| `param_group` | 参数分组 | `COST` | 成本参数 | 成本来源和分摊口径 |
| `param_group` | 参数分组 | `PROMOTION` | 促销参数 | 促销识别和折扣阶梯口径 |
| `param_group` | 参数分组 | `LISTING_SCOPE` | 范围级在售聚合参数 | 保存 `listing_scope_rule_version` 及任一/全部门店聚合规则；业务确认前不得作为可发布参数 |
| `product_status_availability` | 商品状态可用性 | `AVAILABLE` | 商品状态可用 | `dim_product_status` 在当前区域和快照提供有效记录 |
| `product_status_availability` | 商品状态可用性 | `NOT_AVAILABLE` | 商品状态不可用 | V1 缺失、冲突或未接入状态资产 |
| `product_status_code` | 商品状态编码 | `A` | 全年品 | `dim_product_status` 标记为全年品 |
| `product_status_code` | 商品状态编码 | `O` | 试卖品 | `dim_product_status` 标记为试卖品 |
| `product_status_code` | 商品状态编码 | `S` | 季节品 | `dim_product_status` 标记为季节品 |
| `product_status_code` | 商品状态编码 | `D` | 淘汰品 | `dim_product_status` 标记为淘汰品 |
| `product_status_code` | 商品状态编码 | `B` | 备选品 | `dim_product_status` 标记为备选品 |

### 29.6.1 `quality_metrics_json` 结构约束

`mart_target_profile_anchor_summary.quality_metrics_json` 必须是 JSON 对象，固定至少包含：

```text
sku_cnt
valid_sku_cnt
formal_anchor_cnt
reconciliation_status
missing_field_cnt
```

其中 `reconciliation_status` 只允许以下取值：

| JSON 键 | 允许取值 | 含义 | 触发条件 |
|---|---|---|---|
| `reconciliation_status` | `PASS` | 对账通过 | 算法 03、全量有效交易、目标画像金额/会员/门店范围等对账均通过容差 |
| `reconciliation_status` | `FAILED` | 对账失败 | 差异超过容差、主键/覆盖冲突或发现重复计入；同时写 `RECONCILIATION_FAILED` |
| `reconciliation_status` | `NOT_CALCULABLE` | 无法对账 | 上游正式结果缺失、必要分母不可得或本处理单元被上游闸门阻断 |

单个指标无法计算时，该键的值写 JSON `null`；整个汇总没有可计算指标时写 `{}`，不能用 `0`、空字符串或自由中文替代。

### 29.6.2 嵌套 JSON 枚举约束

正式输出表中的嵌套 JSON 枚举必须按以下闭集写入，不能让开发自行扩展英文取值：

| JSON 路径 | 类型 | 允许取值 | 中文含义与来源 | 缺失写法 |
|---|---|---|---|---|
| `active_anchor_skus_json[*].source_layer`、`historical_anchor_skus_json[*].source_layer`、`low_order_high_performance_skus_json[*].source_layer`、`time_sensitive_anchor_skus_json[*].source_layer`、`store_concentrated_anchor_skus_json[*].source_layer`、`relative_anchor_candidates_json[*].source_layer` | string | `PRODUCT` | canonical 实体来自 `mart_target_profile_product_performance`；仅当 `standard_product_mode = SPU_MAPPED` 使用 | 无结果时数组写 `[]`；诊断实体不进入正式 JSON |
| 同上 | string | `SKU` | canonical 实体来自 `mart_target_profile_sku_performance`；仅当 `standard_product_mode = SKU_ONLY` 使用 | 同上 |
| 各锚点 JSON 的 `performance_score` | number 或 `null` | `product_performance_score` / `sku_performance_score` | 按 `source_layer` 取对应层的正式表现分 | 来源层对应表现分不可计算时写 JSON `null`，不写 0 |
| 各锚点 JSON 的 `member_sku_list` / `evidence_sku_ids` | string 数组 | 销售 SKU 编码 | 分别表示标准商品成员和 SKU 级证据 | 无成员或无 SKU 级证据时写 `[]`；不得填入标准商品名称或重复编码 |
| `before_after_promotion_price.price_source` | string | `PRICE_TABLE_ORIGINAL_DORIS_USUAL_AMT_PER_WEIGHT` | `before_price` 来自 `mart_store_sku_daily_price.original_sale_price`；`after_price` 来自有效 Doris 交易 `usual_amt / weight` 的成交单价 | 任一来源缺失、价格分母无效或无法关联时，整个 `before_after_promotion_price` 写 JSON `null`，并在 `data_quality_flags` 写 `PRICE_SOURCE_MISSING` |

---

## 30. 产品端应用边界

产品默认按同一比较组内：

```text
sku_performance_score
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
3. 为后续组合保留锚点的主材料、口味、形态和规格
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

### 32.1 上游对账

检查：

```text
算法 04 SKU 销售额合计 = 算法 03 对应画像销售额
算法 04 使用的 final_profile 与算法 01 唯一
算法 04 使用的 final_level 与算法 02 唯一
```

### 32.2 唯一性

正式结果表不允许同一唯一粒度重复。

### 32.3 公式复算

抽样复算：

```text
sku_sales_share
target_profile_category_sales_amt
target_profile_category_ticket_cnt
target_profile_category_buyer_cnt
sku_buyer_penetration
repurchase_rate_7d_pre19
preference_index
Jeffreys 95% 下界
non_promo_pre1930_sell_through_rate
target_profile_pre1930_absorption_rate
target_profile_sku_margin_amt
sku_performance_score
Jenks+BIC 分组
is_formal_anchor
original_price / target_profile_avg_paid_price / reference_profile_avg_paid_price
standardized_paid_price / before_after_promotion_price / actual_discount_rate
标准商品层去重、CRITIC、Jenks/BIC 和锚点准入
```

### 32.4 分层追溯

必须能从正式结果追溯到：

```text
小票商品明细
会员画像版本
门店品类等级版本
消费者贡献版本
商品基础表
到货/订购数据
毛利数据
可订可售快照
参数表
```

### 32.5 稳定性与后验

检查：

```text
留一门店验证
留一月验证
下一周期后验表现
```

### 32.6 边界场景

必须覆盖：

```text
只有 1 个有效 SKU
只有 2 个有效 SKU
没有参考画像
小样本 1/1 复购
无自然销售窗口
不可订或不可售但历史表现好
目标画像毛利不为正
商品映射冲突
计量单位无法转换
```

### 32.7 字段级交付闸门

逐张检查五类正式表和 `process_algo04_run_audit`：

```text
1. 字段合同表头严格为：中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释。
2. 所有 `_status`、`_flag`、`_method` 和承载枚举的 `*_source` 都能在第 29.6 节逐值解释。
3. JSON 字段明确对象/数组、键名、值类型和空值写法；不能只写未定义的泛化字符串类型。
4. 每个比率、得分和判断字段能由分子、分母或参数表复算。
5. 正式结果包含上游周期、过滤规则、源数据版本和版本指纹；模型版本变化不得覆盖不同输入结果。
6. 上游缺失、无消费、无 SKU、NOT_CALCULABLE 和数据不完整场景按写入边界处理，不伪造明细。
```

---

## 33. 当前已确认口径

| 事项 | 结论 |
|---|---|
| 无促销活动表 | V1 使用 `discount_amt > 0` 代理 |
| 促销识别标记 | `promotion_identify_method = DISCOUNT_PROXY_V1` |
| SKU 维度复购 | V1 先产出 `mart_sku_repurchase_7d_pre19` |
| 独立换码/替代关系不接入 | V1 使用商品基础表现有 SPU；SPU 缺失时 `standard_product_mode = SKU_ONLY` |
| 商品属性缺失 | 不阻断经营表现计算，标记 `ATTRIBUTE_INCOMPLETE` |
| 小票销售标准量字段 | 算法 04 使用 `sales_standard_qty = weight`；计量类型和单位由商品基础表解释，字段事实详见 Doris 字段字典 |
| 毛利损耗表数量字段 | 数据开发可按数据合同交付进货数量、进货重量、订购数量订购单位、订购数量重量口径 |

---

## 34. 开发交付验收项

毛利损耗表、可订可售表和价格表的粒度已按数据合同确定；开发交付时按合同验收是否稳定产出。

| 编号 | 验收项 | 影响 |
|---|---|---|
| D1 | 抽样验收 `sales_standard_qty = weight` 与商品基础表单位是否匹配 | 目标画像标准销售量、毛利、售罄率、折扣阶梯 |
| D2 | 毛利损耗表按数据合同在营业日期 + 门店编码 + 交易商品编码粒度稳定、唯一地提供销售额和全链路毛利额 | 成本反推 |
| D3 | 门店 SKU 可订可售表按数据合同在日期 + 门店编码 + 销售商品编码粒度主键唯一，并稳定提供是否可订、是否可售 | 当前在售、正式锚点 |
| D4 | 毛利损耗表按数据合同稳定提供门店进货数量、门店进货重量、门店订购数量（订购单位）、门店订购数量（重量口径）；订购与收货字段分开使用 | 有效在售 SKU 日、售罄率、订购覆盖 |
| D5 | Doris 有效交易过滤按 `order_status`、`is_return`、`refund_type`、`business_source` 等字段完成，测试交易和异常交易不进入结果 | 有效交易口径 |
| D6 | 算法 02 正式交付 `SUCCESS/NOT_CALCULABLE` 行并保持主键唯一；算法 03 正式交付可消费状态和唯一粒度 | 上游目标画像和门店群 |
| D7 | 正式表字段、JSON 结构、状态枚举、版本血缘与本卡一致 | 字段级交付闸门 |

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

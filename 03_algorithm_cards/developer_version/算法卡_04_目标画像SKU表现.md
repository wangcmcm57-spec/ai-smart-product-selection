# 算法卡_04_目标画像 SKU 表现算法

更新时间：2026-08-03

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

### 2.1 运行流程和表关系

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
category_level_model_version
consumer_contribution_model_version
category_mapping_version
sku_attribute_version
sku_performance_algorithm_version
```

算法 01、02、03 任一正式版本或范围版本变化时，算法 04 必须全量重算。

禁止同一批结果混用不同周期、不同画像版本或不同门店群结果。

### 4.3 当前在售快照

历史表现使用正式 3 个月周期。

当前在售状态读取计算时最新正式商品基础表或可订可售表快照：

```text
listing_snapshot_date
orderable_sellable_flag
```

下一次正式运行时重新读取当前状态，不修改已发布历史版本。

---

## 5. 输入数据与字段合同

### 5.1 必需数据集

| 逻辑数据集 | 是否必需 | 用途 | V1 来源说明 |
|---|---|---|---|
| 算法 01 正式会员画像 | 必须 | 取得每名会员唯一 `final_profile` | `dim_customer_profile` |
| 算法 02 正式门店品类等级 | 必须 | 取得正式门店群和 `final_level` | `mart_store_category_level` |
| 算法 03 消费者贡献结果 | 必须 | 取得主力、相对主力和消费者类型范围 | `mart_store_group_consumer_contribution` |
| 小票商品明细 | 必须 | 销售、销量、小票、会员及购买时间 | Doris 小票商品明细 |
| 商品基础表 | 必须 | 商品编码、名称、品类、单位、单位重量和现有 SPU；独立换码/替代关系不作为 V1 输入 | 商品基础表 |
| 实际到货/订购明细 | 必须 | 有效在售 SKU 日、实际收货量、订购覆盖 | 毛利损耗表 + 门店 SKU 可订可售表 |
| 商品毛利明细 | 必须 | 销售额、全链路毛利额；成本金额由销售额和全链路毛利额反推 | 毛利损耗表，字段稳定性由开发交付验收 |
| 折扣代理字段 | 必须 | 非促销 SKU 日、实付价格和折扣阶梯 | V1 不接促销活动表，用 Doris `discount_amt > 0` 代理 |
| 日历、门店、城市群 | 必须 | 日期、月份、门店及正式范围 | 门店基础表 + 城市算法区域映射表 |
| 7 天复购结果 | 必须 | 复购分子、分母、原始复购率 | V1 先产出 `mart_sku_repurchase_7d_pre19` |

### 5.2 Doris 小票商品明细字段

| 中文字段名 | 英文字段名 | Doris 候选字段 | 是否必须 | 中文注释 |
|---|---|---|---|---|
| 订单商品明细ID | order_item_id | order_item_id | 必须 | 商品行唯一键 |
| 小票ID | ticket_id | order_id | 必须 | 已确认公司级唯一，可作为 `ticket_key` |
| 门店编码 | store_id | store_id | 必须 | 与门店和算法 02 对齐 |
| 会员ID | customer_id | customer_id | 必须 | 与算法 01 会员画像对齐 |
| 销售SKU编码 | sku_id | article_id | 必须 | 与商品基础表交易商品编码对齐 |
| 营业日期 | business_date | business_date | 必须 | 交易营业日期 |
| 销售时间 | sale_time | inc_time | 必须 | 判断 19:00 复购和 19:30 自然动销 |
| 商品行实付金额 | paid_sales_amt | usual_amt | 必须 | 目标画像 SKU 销售额 |
| 商品行优惠金额 | discount_amt | discount_amt | 条件必须 | V1 促销/折扣代理 |
| 销售标准量 | sales_standard_qty | weight | 必须 | 算法统一使用 `sales_standard_qty = weight`；计量类型和单位由商品基础表解释，字段事实详见 Doris 字段字典 |
| 是否时段促销 | is_hour_promotion | is_hour_promotion | 可选 | 折扣解释 |
| 小时优惠金额 | hour_discount_amt | hour_discount_amt | 可选 | 不是商品行时段折扣金额，不直接按行求和 |
| 订单状态 | order_status | order_status | 必须 | 有效交易过滤，V1 保留 `os.completed` |
| 是否退货 | is_return | is_return | 必须 | 有效交易过滤，V1 保留 `0` |
| 退款类型 | refund_type | refund_type | 条件必须 | 退款/冲销过滤辅助字段，按 Doris 字段字典和开发清洗口径执行 |
| 业务来源 | business_source | business_source | 可选 | 测试交易或特殊来源过滤辅助字段 |

### 5.3 商品基础表字段

| 中文字段名 | 英文字段名 | 是否必须 | 中文注释 |
|---|---|---|---|
| 交易商品编码 | sku_id | 必须 | 与 Doris `article_id` 对齐 |
| 商品名称 | sku_name | 必须 | SKU 展示名称 |
| SPU编码 | spu_id | 可选 | 标准商品层聚合 |
| 大类编码 | large_category_code | 条件必须 | 大类计算 |
| 大类名称 | large_category_name | 条件必须 | 大类计算 |
| 中类编码 | middle_category_code | 条件必须 | 中类计算 |
| 中类名称 | middle_category_name | 条件必须 | 中类计算 |
| 小类编码 | small_category_code | 条件必须 | 小类计算 |
| 小类名称 | small_category_name | 条件必须 | 小类计算 |
| 单位 | source_unit | 必须 | 计量标准化 |
| 单位重量 | unit_weight | 条件必须 | 商品基础表已有单位重量；定量包装、件转重量时使用 |
| 净含量 | net_content | 条件必须 | 可由商品基础表规格解析；用于定量包装解释 |
| 主材料 | main_ingredient | 可选 | 商品属性输出，缺失不阻断经营表现 |
| 商品形态 | product_form | 可选 | 商品属性输出，缺失不阻断经营表现 |
| 配料 | ingredient | 可选 | 商品属性输出，缺失不阻断经营表现 |
| 口味 | flavor | 可选 | 商品属性输出，缺失不阻断经营表现 |
| 加工方式 | processing_method | 可选 | 商品属性输出，缺失不阻断经营表现 |
| 烹饪方式 | cooking_method | 可选 | 商品属性输出，缺失不阻断经营表现 |
| 包装类型 | package_type | 可选 | 商品属性输出，缺失不阻断经营表现 |
| 存储温层 | storage_temperature | 可选 | 商品属性输出，缺失不阻断经营表现 |
| 品牌 | brand | 可选 | 商品属性输出，缺失不阻断经营表现 |

### 5.4 毛利损耗表字段

| 中文字段名 | 英文字段名 | 是否必须 | 中文注释 |
|---|---|---|---|
| 营业日期 | business_date | 必须 | 日期 |
| 门店编码 | store_id | 必须 | 门店 |
| 交易商品编码 | sku_id | 必须 | 销售 SKU |
| 销售额 | sku_total_sales_amt | 必须 | 日门店 SKU 总销售额 |
| 销售数量 | daily_sku_sales_qty | 条件必须 | 计件商品总量校验 |
| 销售重量 | daily_sku_sales_weight | 条件必须 | 称重商品总量校验 |
| 门店进货数量 | actual_received_qty | 条件必须 | 实际验收数量，按商品原经营单位统计；计件商品售罄率分母优先使用 |
| 门店进货重量 | actual_received_weight | 条件必须 | 实际验收数量换算后的重量口径，建议单位 kg；称重商品售罄率分母优先使用 |
| 门店进货金额 | actual_received_amt | 可选 | 到货金额解释 |
| 门店订购数量（订购单位） | order_qty_original | 可选 | 按订购单位统计的原始订购数量，用于订购覆盖、订购满足率和对账；计件商品订购量优先使用 |
| 门店订购数量（重量口径） | order_weight_kg | 可选 | 由订购单位换算成重量后的订购数量，建议单位 kg；称重商品订购量分析优先使用 |
| 门店订购额 | order_amt | 可选 | 订购覆盖 |
| 全链路毛利额 | sku_total_margin_amt | 必须 | SKU 整体毛利优先口径 |
| 全链路毛利率 | sku_total_margin_rate | 可选 | SKU 整体毛利率 |
| 门店毛利额 | store_margin_amt | 可选 | 门店口径解释 |
| 总折扣额 | total_discount_amt | 条件必须 | V1 折扣代理汇总 |
| 促销折扣额 | promotion_discount_amt | 可选 | 若可到 SKU 日粒度，优先用于非促销判断 |
| 时段折扣额 | hour_discount_amt_summary | 可选 | 若可到 SKU 日粒度，折扣阶梯解释 |

### 5.5 门店 SKU 可订可售表字段

| 中文字段名 | 英文字段名 | 是否必须 | 中文注释 |
|---|---|---|---|
| 日期 | business_date | 必须 | 状态日期 |
| 门店编码 | store_id | 必须 | 门店 |
| 销售商品编码 | sku_id | 必须 | 销售 SKU |
| 订购商品编码 | order_sku_id | 必须 | 订购 SKU，可能与销售 SKU 不一致 |
| 是否可售 | is_sellable | 必须 | 1 可售，0 不可售 |
| 是否可订 | is_orderable | 必须 | 1 可订，0 不可订 |
| 数据更新时间 | updated_at | 必须 | 快照更新时间 |

`orderable_sellable_flag` 可按以下规则生成：

```text
is_sellable = 1 AND is_orderable = 1 -> orderable_sellable_flag = 1
否则 -> orderable_sellable_flag = 0
```

### 5.6 门店商品日价格表字段

| 中文字段名 | 英文字段名 | 是否必须 | 中文注释 |
|---|---|---|---|
| 日期 | business_date | 必须 | 日期 |
| 门店编码 | store_id | 必须 | 门店 |
| 销售商品编码 | sku_id | 必须 | 销售 SKU |
| 验收商品编码 | receipt_sku_id | 必须 | 验收/进货 SKU |
| 出库到店成本含税 | arrival_cost_tax_included | 条件必须 | 成本备选口径 |
| 出库到店金额含税 | arrival_amt_tax_included | 可选 | 到店金额解释 |
| 销售原价 | original_sales_price | 可选 | 折扣率和价格解释 |
| 商品平均售价 | avg_paid_price | 可选 | 成交均价 |
| 19点前平均售价 | pre19_avg_paid_price | 可选 | 价格解释 |
| 19点后售价 | after19_price | 可选 | 折扣阶梯解释 |

---

## 6. 前置过滤与对账

### 6.1 有效会员和交易

复用算法 01、03：

```text
customer_id 非空且不以“6”开头
只保留正常完成的正向销售
sales_standard_qty > 0，即 Doris `weight` > 0
实付金额 > 0
剔除退货、取消、冲销、测试交易
剔除赠品/零金额行
剔除算法 01 已标记的异常会员日
```

如果 Doris 表已是清洗后的有效商品明细：

```text
valid_transaction_filter_method = SOURCE_TABLE_CLEANED
```

如果算法 04 任务内过滤：

```text
valid_transaction_filter_method = RULE_FILTERED

order_status = 'os.completed'
AND is_return = 0
AND customer_id IS NOT NULL
AND customer_id <> ''
AND usual_amt > 0
AND weight > 0
```

`refund_type`、`business_source` 等字段用于辅助识别退款、冲销、测试交易或特殊交易来源。若数据开发确认 Doris 主表已清洗完成，可记录 `valid_transaction_filter_method = SOURCE_TABLE_CLEANED`；否则必须在任务内按上述字段过滤后再计算。

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
paid_sales_amt = SUM(usual_amt)
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

---

## 7. 全天行为与时间窗口

### 7.1 全天指标

以下指标使用全天有效会员交易：

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
= SUM(目标画像购买该 SKU 的 paid_sales_amt)

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
orderable_sellable_flag = 1 -> listing_status = ACTIVE
orderable_sellable_flag = 0 -> listing_status = INACTIVE
```

当前在售不以近期是否实际到货判断。

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
ordered_store_cnt
= 周期内实际订购过该 SKU 的门店数

store_order_rate
= ordered_store_cnt / 允许订购该 SKU 的有效门店数

ordered_store_day_rate
= 存在实际收货的门店日数 / 允许订购该 SKU 的有效门店营业日数
```

若只有全局可订可售字段，没有门店级可订清单：

```text
分母 = 门店群全部有效门店
orderable_scope = GROUP_ALL_STORES
```

V1 已有门店 SKU 每日可订可售表，正式计算优先使用门店级可订范围：

```text
orderable_scope = STORE_SKU_ORDERABLE
```

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
source_unit
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

`weight` 的字段事实和样例验证统一维护在 Doris 字段字典中。本算法卡只定义使用规则：读取有效交易中的 `weight`，再关联商品基础表取得 `source_unit`、`measurement_type`、`standard_unit` 和必要的换算关系。

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
preference_reference_status = SINGLE_PROFILE
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
  / 门店群该 SKU 19:30 前总销售标准量
```

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

使用门店商品日价格表 `出库到店成本含税` 聚合到日期 + 门店 + 销售 SKU。

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
storage_temperature：储存温层
brand：品牌
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

---

## 19. 四个一级评分维度

### 19.1 目标画像贡献

```text
sku_sales_share
sku_buyer_penetration_lower_95
target_sales_per_available_store_day
```

### 19.2 目标画像偏好

```text
preference_index_lower_95
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

例如 `SINGLE_PROFILE` 没有偏好参考组。

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
不可订不可售
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
= 贡献周期内有真实销售且表现较好，但当前不可订不可售
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

算法 04 开发交付 5 张可持久化表：1 张前置复购结果表 + 4 类正式结果表。

开发可以有临时表或过程表，但下游正式读取以下表：

| 表名 | 表类型 | 一行代表什么 | 下游用途 |
|---|---|---|---|
| `mart_sku_repurchase_7d_pre19` | 前置中间结果表 | 一个周期 + 一个范围 + 一个消费者画像 + 一个 SKU 的 7 天 19 点前复购结果 | 先由算法 04 计算，再被 SKU 表现主表读取 |
| `mart_target_profile_sku_performance` | 正式结果表 | 一个周期 + 一个范围 + 一个门店群 + 一个消费者画像 + 一个销售 SKU | 算法 04 主表，给算法 05/06/09/10 读取 |
| `mart_target_profile_product_performance` | 正式结果表 | 一个周期 + 一个范围 + 一个门店群 + 一个消费者画像 + 一个标准商品 | 标准商品层表现，V1 用 SPU，SPU 缺失时按 SKU_ONLY |
| `mart_target_profile_anchor_summary` | 正式结果表 | 一个周期 + 一个范围 + 一个门店群 + 一个消费者画像的锚点汇总 | 给业务验收和下游选择默认锚点 |
| `mart_target_profile_sku_performance_params` | 正式参数表 | 一个参数版本 + 一个参数作用范围 + 一个参数 | 复现 CRITIC、Jenks/BIC、Jeffreys、单位映射和口径参数 |

### 29.1 前置表：`mart_sku_repurchase_7d_pre19`

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
| 范围版本 | `scope_version` | varchar(64) | 必须 | 城市算法区域映射表 | 城市算法区域版本 |
| 范围类型 | `scope_type` | varchar(32) | 必须 | 城市算法区域映射表 | `CITY` / `CITY_CLUSTER` |
| 范围编码 | `scope_id` | varchar(64) | 必须 | 城市算法区域映射表 | 城市或城市群编码 |
| 范围名称 | `scope_name` | varchar(128) | 必须 | 城市算法区域映射表 | 城市或城市群名称 |
| 品类颗粒度 | `category_granularity` | varchar(32) | 必须 | 商品基础表 | 大类 / 中类 / 小类 |
| 品类编码 | `category_code` | varchar(64) | 必须 | 商品基础表 | 当前计算品类编码 |
| 品类名称 | `category_name` | varchar(128) | 必须 | 商品基础表 | 当前计算品类名称 |
| 门店群类型 | `store_group_type` | varchar(32) | 必须 | 算法 02 | `FINAL_LEVEL` / `ALL_RATED` |
| 门店品类等级 | `final_level` | varchar(32) | 必须 | 算法 02 `mart_store_category_level` | A/B/C/D 或 ALL_RATED |
| 消费者画像 | `final_profile` | varchar(128) | 必须 | 算法 01 `dim_customer_profile` | 算法 01 最终画像 |
| 会员画像版本 | `profile_model_version` | varchar(64) | 必须 | 算法 01 `dim_customer_profile` | 本次锁定会员画像版本 |
| 门店品类等级版本 | `category_level_model_version` | varchar(64) | 必须 | 算法 02 `mart_store_category_level` | 本次锁定门店品类等级版本 |
| 消费者贡献版本 | `consumer_contribution_model_version` | varchar(64) | 必须 | 算法 03 `mart_store_group_consumer_contribution` | 本次锁定消费者贡献版本 |
| 商品分类版本 | `category_mapping_version` | varchar(64) | 必须 | 商品基础表 | 商品分类口径版本 |
| SKU 编码 | `sku_id` | varchar(64) | 必须 | Doris `article_id` / 商品基础表 | 销售 SKU |
| 7 天复购会员数 | `repeat_buyer_cnt_7d_pre19` | bigint | 必须 | Doris 小票计算 | 首次购买后第 1-7 个自然日且 19:00 前再次购买该 SKU 的会员数 |
| 7 天可观察首购会员数 | `eligible_first_buyer_cnt_7d` | bigint | 必须 | Doris 小票计算 | 首次购买后具备完整 7 天观察窗口的会员数 |
| 7 天 19 点前复购率 | `repurchase_rate_7d_pre19` | decimal(18,8) | 必须 | 本表计算 | `repeat_buyer_cnt_7d_pre19 / eligible_first_buyer_cnt_7d` |
| 计算状态 | `repurchase_calc_status` | varchar(64) | 必须 | 本表计算 | 见第 29.6 节状态约束 |
| 计算时间 | `calculated_at` | datetime | 必须 | 系统生成 | 结果写入时间 |

### 29.2 SKU 表现明细：`mart_target_profile_sku_performance`

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
| 范围版本 | `scope_version` | varchar(64) | 必须 | 城市算法区域映射表 | 城市算法区域版本 |
| 范围类型 | `scope_type` | varchar(32) | 必须 | 城市算法区域映射表 | `CITY` / `CITY_CLUSTER` |
| 范围编码 | `scope_id` | varchar(64) | 必须 | 城市算法区域映射表 | 城市或城市群编码 |
| 范围名称 | `scope_name` | varchar(128) | 必须 | 城市算法区域映射表 | 城市或城市群名称 |
| 品类颗粒度 | `category_granularity` | varchar(32) | 必须 | 商品基础表 | 大类 / 中类 / 小类 |
| 大类编码 | `large_category_code` | varchar(64) | 建议 | 商品基础表 | 商品大类编码 |
| 大类名称 | `large_category_name` | varchar(128) | 建议 | 商品基础表 | 商品大类名称 |
| 中类编码 | `middle_category_code` | varchar(64) | 建议 | 商品基础表 | 商品中类编码 |
| 中类名称 | `middle_category_name` | varchar(128) | 建议 | 商品基础表 | 商品中类名称 |
| 小类编码 | `small_category_code` | varchar(64) | 必须 | 商品基础表 | 商品小类编码 |
| 小类名称 | `small_category_name` | varchar(128) | 必须 | 商品基础表 | 商品小类名称 |
| 品类编码 | `category_code` | varchar(64) | 必须 | 商品基础表 | 与 `category_granularity` 对应的当前计算品类编码 |
| 品类名称 | `category_name` | varchar(128) | 必须 | 商品基础表 | 与 `category_granularity` 对应的当前计算品类名称 |
| 门店群类型 | `store_group_type` | varchar(32) | 必须 | 算法 02 | `FINAL_LEVEL` / `ALL_RATED` |
| 门店品类等级 | `final_level` | varchar(32) | 必须 | 算法 02 `mart_store_category_level` | 当前门店群等级 |
| 门店数 | `store_cnt` | bigint | 必须 | 算法 02 / Doris 聚合 | 当前范围内进入计算的门店数 |
| 消费者画像 | `final_profile` | varchar(128) | 必须 | 算法 01 `dim_customer_profile` | 目标消费者画像 |
| 是否主力画像 | `is_main_profile` | tinyint | 必须 | 算法 03 `mart_store_group_consumer_contribution` | `1` 是正式主力画像，`0` 不是 |
| 是否相对主力候选 | `is_relative_main_candidate` | tinyint | 必须 | 算法 03 `mart_store_group_consumer_contribution` | `1` 是相对主力候选，`0` 不是 |
| 会员画像版本 | `profile_model_version` | varchar(64) | 必须 | 算法 01 `dim_customer_profile` | 本次锁定会员画像版本 |
| 门店品类等级版本 | `category_level_model_version` | varchar(64) | 必须 | 算法 02 `mart_store_category_level` | 本次锁定门店品类等级版本 |
| 消费者贡献版本 | `consumer_contribution_model_version` | varchar(64) | 必须 | 算法 03 `mart_store_group_consumer_contribution` | 本次锁定消费者贡献版本 |
| 商品分类版本 | `category_mapping_version` | varchar(64) | 必须 | 商品基础表 | 商品基础表分类口径版本 |
| 商品属性版本 | `sku_attribute_version` | varchar(64) | 必须 | 商品基础表/属性加工规则 | V1 为商品基础表和名称解析口径版本 |
| 在售快照日期 | `listing_snapshot_date` | date | 必须 | 门店 SKU 可订可售表 | 当前可订可售快照日期 |
| 有效交易过滤方式 | `valid_transaction_filter_method` | varchar(64) | 必须 | 本算法 | 见第 29.6 节状态约束 |

商品、在售和计量字段：

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| SKU 编码 | `sku_id` | varchar(64) | 必须 | Doris `article_id` / 商品基础表 | 销售 SKU |
| 商品编码 | `product_code` | varchar(64) | 必须 | 商品基础表 | 商品主数据编码 |
| SKU 名称 | `sku_name` | varchar(256) | 必须 | 商品基础表 | 商品展示名称 |
| SPU 编码 | `spu_id` | varchar(64) | 建议 | 商品基础表 | 商品基础表现有 SPU 编码 |
| SPU 名称 | `spu_name` | varchar(256) | 建议 | 商品基础表 | 商品基础表现有 SPU 名称 |
| 标准商品主键 | `standard_product_key` | varchar(128) | 必须 | 商品基础表/本算法 | SPU 有效时取 `spu_id`，否则取 `sku_id` |
| 标准商品模式 | `standard_product_mode` | varchar(64) | 必须 | 本算法 | 见第 29.6 节状态约束 |
| 是否可订可售 | `orderable_sellable_flag` | tinyint | 必须 | 门店 SKU 可订可售表 | 当前快照是否可订且可售 |
| 在售状态 | `listing_status` | varchar(64) | 必须 | 门店 SKU 可订可售表 | 见第 29.6 节状态约束 |
| 计量类型 | `measurement_type` | varchar(32) | 必须 | 商品基础表单位/规格解析 | `WEIGHT` / `QUANTITY` / `PIECE_COUNT` / `VOLUME` / `UNKNOWN` |
| 来源单位 | `source_unit` | varchar(32) | 必须 | 商品基础表 | 商品基础表单位 |
| 标准单位 | `standard_unit` | varchar(32) | 必须 | 商品基础表/本算法 | 算法计算使用的标准单位 |
| 单位换算系数 | `conversion_factor` | decimal(18,8) | 条件必须 | 商品基础表单位重量 | 从来源单位换算到标准单位的系数 |
| 计量映射状态 | `measurement_mapping_status` | varchar(64) | 必须 | 本算法 | 见第 29.6 节状态约束 |
| 订购范围口径 | `orderable_scope` | varchar(64) | 必须 | 门店 SKU 可订可售表/本算法 | 见第 29.6 节状态约束 |
| 订购门店数 | `ordered_store_cnt` | bigint | 必须 | 毛利损耗表/可订可售表 | 周期内实际订购或收货过该 SKU 的门店数 |
| 允许订购门店数 | `eligible_orderable_store_cnt` | bigint | 必须 | 门店 SKU 可订可售表 | 当前门店群内允许订购该 SKU 的有效门店数 |
| 门店订购率 | `store_order_rate` | decimal(18,8) | 必须 | 本算法 | 订购门店数 / 允许订购该 SKU 的有效门店数 |
| 允许订购有效门店日数 | `eligible_orderable_store_day_cnt` | bigint | 必须 | 门店 SKU 可订可售表 | 当前门店群内允许订购该 SKU 的有效门店营业日数 |
| 门店订购日率 | `ordered_store_day_rate` | decimal(18,8) | 必须 | 本算法 | 有实际收货的门店日数 / 允许订购的有效门店营业日数 |

行为、偏好和复购字段：

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| SKU 销售额 | `sku_sales_amt` | decimal(18,6) | 必须 | Doris 小票 | 目标画像购买该 SKU 的有效销售额 |
| SKU 销售标准量 | `sku_sales_qty` | decimal(18,6) | 必须 | Doris `weight` | 目标画像购买该 SKU 的销售标准量，`weight` 为计价数量 |
| SKU 小票数 | `sku_ticket_cnt` | bigint | 必须 | Doris `order_id` | 目标画像购买该 SKU 的去重小票数 |
| SKU 购买会员数 | `sku_buyer_cnt` | bigint | 必须 | Doris `customer_id` | 目标画像购买该 SKU 的去重会员数 |
| SKU 销售占比 | `sku_sales_share` | decimal(18,8) | 必须 | 本算法 | 该 SKU 销售额 / 目标画像该品类销售额 |
| SKU 小票渗透率 | `sku_ticket_penetration` | decimal(18,8) | 必须 | 本算法 | 购买该 SKU 的小票数 / 目标画像该品类小票数 |
| SKU 会员渗透率原始值 | `sku_buyer_penetration_raw` | decimal(18,8) | 必须 | 本算法 | 购买该 SKU 的会员数 / 目标画像该品类会员数 |
| SKU 会员渗透率 95% 下界 | `sku_buyer_penetration_lower_95` | decimal(18,8) | 必须 | Jeffreys 区间 | 目标画像会员渗透率 95% 区间下界 |
| SKU 会员渗透率 95% 上界 | `sku_buyer_penetration_upper_95` | decimal(18,8) | 必须 | Jeffreys 区间 | 目标画像会员渗透率 95% 区间上界 |
| 目标画像渗透率 | `target_penetration` | decimal(18,8) | 必须 | 本算法 | 目标画像购买该 SKU 的会员渗透率 |
| 参考画像渗透率 | `reference_penetration` | decimal(18,8) | 必须 | 本算法 | 非目标画像购买该 SKU 的会员渗透率 |
| 偏好参考组状态 | `preference_reference_status` | varchar(64) | 必须 | 算法 03/本算法 | 见第 29.6 节状态约束 |
| 原始偏好指数 | `preference_index_raw` | decimal(18,8) | 必须 | 本算法 | 目标画像渗透率 / 参考画像渗透率 |
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
| 有效门店 SKU 日数 | `available_store_day_cnt` | bigint | 必须 | 毛利损耗表/可订可售表 | 周期内有实际收货条件的门店 SKU 日数 |
| 每有效门店 SKU 日销售额 | `sales_per_available_store_day` | decimal(18,8) | 必须 | 本算法 | 目标画像销售额 / 有效门店 SKU 日数 |
| 每有效门店 SKU 日购买会员数 | `buyers_per_available_store_day` | decimal(18,8) | 必须 | 本算法 | 目标画像购买会员数 / 有效门店 SKU 日数 |
| 实际收货标准量 | `actual_received_standard_qty` | decimal(18,6) | 必须 | 毛利损耗表 + 商品基础表 | 称重商品取门店进货重量；普通计件和枚数型商品取门店进货数量；体积商品可稳定换算时按标准体积口径换算 |
| 19:30 前销售标准量 | `pre1930_sales_standard_qty` | decimal(18,6) | 必须 | Doris `weight` | 有效 SKU 日 19:30 前销售标准量 |
| 非促销有效门店 SKU 日数 | `non_promo_available_store_day_cnt` | bigint | 必须 | Doris + 毛利损耗表 | 19:30 前 `discount_amt = 0` 的有效门店 SKU 日数 |
| 非促销实际收货标准量 | `non_promo_actual_received_standard_qty` | decimal(18,6) | 必须 | Doris + 毛利损耗表 | 非促销有效 SKU 日实际收货标准量 |
| 非促销 19:30 前销售标准量 | `non_promo_pre1930_sales_standard_qty` | decimal(18,6) | 必须 | Doris `weight` | 非促销有效 SKU 日 19:30 前销售标准量 |
| 19:30 前售罄率 | `pre1930_sell_through_rate` | decimal(18,8) | 必须 | Doris + 毛利损耗表 | 19:30 前销售标准量 / 实际收货标准量 |
| 非促销 19:30 前售罄率 | `non_promo_pre1930_sell_through_rate` | decimal(18,8) | 必须 | Doris + 毛利损耗表 | 剔除 `discount_amt > 0` 代理促销后的 19:30 前售罄率 |
| 每有效门店 SKU 日 19:30 前销售量 | `pre1930_sales_volume_per_available_store_day` | decimal(18,8) | 必须 | Doris `weight` | 19:30 前销售标准量 / 有效门店 SKU 日数 |
| 目标画像 19:30 前吸收率 | `target_profile_pre1930_absorption_rate` | decimal(18,8) | 必须 | 本算法 | 目标画像 19:30 前销售标准量 / 门店群该 SKU 19:30 前总销售标准量 |
| 折扣阶梯 JSON | `discount_ladder_json` | json/string | 建议 | Doris 小票 | 19:30 后每半小时销售量、增量售罄率和实际折扣率 |
| 目标画像 SKU 销售额 | `target_profile_sku_sales_amt` | decimal(18,6) | 必须 | Doris 小票 | 目标画像该 SKU 销售额 |
| 目标画像 SKU 成本额 | `target_profile_sku_cost_amt` | decimal(18,6) | 必须 | 毛利损耗表 + 本算法 | 按标准量单位成本分摊到目标画像的 SKU 成本金额 |
| 目标画像 SKU 毛利额 | `target_profile_sku_margin_amt` | decimal(18,6) | 必须 | 本算法 | `target_profile_sku_sales_amt - target_profile_sku_cost_amt` |
| 目标画像 SKU 毛利率 | `target_profile_sku_margin_rate` | decimal(18,8) | 必须 | 本算法 | `target_profile_sku_margin_amt / target_profile_sku_sales_amt` |
| SKU 总销售额 | `sku_total_sales_amt` | decimal(18,6) | 必须 | 毛利损耗表 | 该 SKU 在比较组内全量销售额 |
| SKU 总成本额 | `sku_total_cost_amt` | decimal(18,6) | 必须 | 毛利损耗表 + 本算法 | `sku_total_sales_amt - sku_total_margin_amt` |
| SKU 总毛利额 | `sku_total_margin_amt` | decimal(18,6) | 必须 | 毛利损耗表全链路毛利额 | 该 SKU 在比较组内全链路毛利额 |
| SKU 总毛利率 | `sku_total_margin_rate` | decimal(18,8) | 必须 | 本算法 | `sku_total_margin_amt / sku_total_sales_amt` |
| 成本来源 | `cost_source` | varchar(64) | 必须 | 本算法 | 见第 29.6 节状态约束 |
| 成本分摊方法 | `cost_allocation_method` | varchar(64) | 必须 | 本算法 | V1 默认 `UNIT_COST_BY_STANDARD_QTY` |
| 成本分摊状态 | `cost_allocation_status` | varchar(64) | 必须 | 本算法 | 见第 29.6 节状态约束 |
| SKU 实付均价 | `sku_avg_paid_price` | decimal(18,6) | 建议 | Doris 小票 | 目标画像该 SKU 实付销售额 / 销售标准量 |
| 标准化成交价格 | `standardized_paid_price` | decimal(18,6) | 建议 | 本算法 | 按标准单位换算后的成交价格 |
| 促销识别方式 | `promotion_identify_method` | varchar(64) | 必须 | 本算法 | V1 固定为 `DISCOUNT_PROXY_V1` |

得分和锚点字段：

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 画像贡献维度分 | `contribution_dimension_score` | decimal(18,8) | 必须 | 本算法 | 目标画像贡献维度得分 |
| 画像偏好维度分 | `preference_dimension_score` | decimal(18,8) | 必须 | 本算法 | 目标画像偏好维度得分 |
| 自然动销维度分 | `natural_sales_dimension_score` | decimal(18,8) | 必须 | 本算法 | 19:30 前自然动销维度得分 |
| 毛利维度分 | `margin_dimension_score` | decimal(18,8) | 必须 | 本算法 | 商品毛利维度得分 |
| 维度权重 JSON | `dimension_weights_json` | json/string | 必须 | CRITIC | 两级 CRITIC 计算出的维度权重 |
| 点估计观察分 | `point_evidence_score` | decimal(18,8) | 必须 | 本算法 | 使用后验均值计算的观察分，用于低证据对比 |
| SKU 表现综合分 | `sku_performance_score` | decimal(18,8) | 必须 | 本算法 | 正式保守综合表现分，使用 95% 下界 |
| 选中分组数量 | `selected_cluster_count` | int | 必须 | Jenks/BIC | Jenks+BIC 选择的分组数量 |
| Jenks 分割点 JSON | `jenks_breaks_json` | json/string | 必须 | Jenks/BIC | Jenks 分割点 |
| SSE 结果 JSON | `sse_by_k_json` | json/string | 必须 | Jenks/BIC | 各 K 的 SSE |
| BIC 结果 JSON | `bic_by_k_json` | json/string | 必须 | Jenks/BIC | 各 K 的 BIC |
| 表现分组 | `performance_group` | varchar(64) | 必须 | 本算法 | 见第 29.6 节状态约束 |
| 是否正式锚点 | `is_formal_anchor` | tinyint | 必须 | 本算法 | `1` 是正式锚点，`0` 不是 |
| 锚点生命周期状态 | `anchor_lifecycle_status` | varchar(64) | 必须 | 本算法 | 见第 29.6 节状态约束 |
| 锚点证据类型 | `anchor_evidence_type` | varchar(64) | 必须 | 本算法 | 见第 29.6 节状态约束 |

稳定性、属性和状态字段：

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| Top1 门店销售占比 | `top1_store_sales_share` | decimal(18,8) | 必须 | 本算法 | 最大单店销售额 / 该 SKU 总销售额 |
| 门店销售 HHI | `store_sales_hhi` | decimal(18,8) | 必须 | 本算法 | 门店销售集中度 |
| 留一门店锚点稳定率 | `leave_one_store_anchor_rate` | decimal(18,8) | 必须 | 稳定性验证 | 删除单店后仍为锚点的比例 |
| 门店稳定性状态 | `store_stability_status` | varchar(64) | 必须 | 稳定性验证 | 见第 29.6 节状态约束 |
| 留一月锚点稳定率 | `leave_one_month_anchor_rate` | decimal(18,8) | 必须 | 稳定性验证 | 删除单月后仍为锚点的比例 |
| 时间稳定性状态 | `time_stability_status` | varchar(64) | 必须 | 稳定性验证 | 见第 29.6 节状态约束 |
| 主材料 | `main_ingredient` | varchar(128) | 建议 | 商品基础表/商品名称解析 | 商品主材料 |
| 商品形态 | `product_form` | varchar(128) | 建议 | 商品基础表/商品名称解析 | 商品形态 |
| 配料 | `ingredient` | varchar(512) | 建议 | 商品基础表/商品名称解析 | 关键配料 |
| 口味 | `flavor` | varchar(128) | 建议 | 商品基础表/商品名称解析 | 商品口味 |
| 加工方式 | `processing_method` | varchar(128) | 建议 | 商品基础表/商品名称解析 | 加工方式 |
| 烹饪方式 | `cooking_method` | varchar(128) | 建议 | 商品基础表/商品名称解析 | 烹饪方式 |
| 净含量 | `net_content` | decimal(18,6) | 建议 | 商品基础表规格解析 | 商品净含量 |
| 包装类型 | `package_type` | varchar(128) | 建议 | 商品基础表/商品名称解析 | 包装形态 |
| 存储温层 | `storage_temperature` | varchar(64) | 建议 | 商品基础表 | 冷藏、冷冻、常温等 |
| 品牌 | `brand` | varchar(128) | 建议 | 商品基础表 | 商品品牌 |
| 属性来源 JSON | `attribute_source_json` | json/string | 必须 | 商品基础表/属性加工规则 | 每个属性的来源 |
| 属性置信度 JSON | `attribute_confidence_json` | json/string | 必须 | 属性加工规则 | 每个属性识别的置信度 |
| 结果状态 | `result_status` | varchar(64) | 必须 | 本算法 | 见第 29.6 节状态约束 |
| 盈利状态 | `profitability_status` | varchar(64) | 必须 | 本算法 | 见第 29.6 节状态约束 |
| 证据状态 | `evidence_status` | varchar(64) | 必须 | 本算法 | 见第 29.6 节状态约束 |
| 自然动销状态 | `natural_sales_status` | varchar(64) | 必须 | 本算法 | 见第 29.6 节状态约束 |
| 订购覆盖状态 | `order_coverage_status` | varchar(64) | 必须 | 本算法 | 见第 29.6 节状态约束 |
| 属性状态 | `attribute_status` | varchar(64) | 必须 | 本算法 | 见第 29.6 节状态约束 |
| 数据质量标记 JSON | `data_quality_flags` | json/string | 建议 | 质量校验 | 数据缺失、异常、降级标记集合 |
| 计算时间 | `calculated_at` | datetime | 必须 | 系统生成 | 结果写入时间 |

### 29.3 标准商品表现：`mart_target_profile_product_performance`

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

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| SKU 表现模型版本 | `sku_performance_model_version` | varchar(64) | 必须 | 算法 04 参数 | 算法 04 本次计算版本 |
| 数据周期开始日期 | `performance_start_date` | date | 必须 | 主表继承 | 统计周期开始日期 |
| 数据周期结束日期 | `performance_end_date` | date | 必须 | 主表继承 | 统计周期结束日期 |
| 范围版本 | `scope_version` | varchar(64) | 必须 | 主表继承 | 城市算法区域版本 |
| 范围类型 | `scope_type` | varchar(32) | 必须 | 主表继承 | `CITY` / `CITY_CLUSTER` |
| 范围编码 | `scope_id` | varchar(64) | 必须 | 主表继承 | 城市或城市群编码 |
| 范围名称 | `scope_name` | varchar(128) | 必须 | 主表继承 | 城市或城市群名称 |
| 品类颗粒度 | `category_granularity` | varchar(32) | 必须 | 主表继承 | 大类 / 中类 / 小类 |
| 品类编码 | `category_code` | varchar(64) | 必须 | 主表继承 | 当前计算品类编码 |
| 品类名称 | `category_name` | varchar(128) | 必须 | 主表继承 | 当前计算品类名称 |
| 门店群类型 | `store_group_type` | varchar(32) | 必须 | 主表继承 | `FINAL_LEVEL` / `ALL_RATED` |
| 门店品类等级 | `final_level` | varchar(32) | 必须 | 主表继承 | 当前门店群等级 |
| 消费者画像 | `final_profile` | varchar(128) | 必须 | 主表继承 | 目标消费者画像 |
| 标准商品主键 | `standard_product_key` | varchar(128) | 必须 | 主表聚合 | SPU 有效时取 `spu_id`，否则取 `sku_id` |
| 标准商品名称 | `standard_product_name` | varchar(256) | 必须 | 商品基础表/主表聚合 | SPU 名称或代表 SKU 名称 |
| 标准商品模式 | `standard_product_mode` | varchar(64) | 必须 | 主表继承 | `SPU_MAPPED` / `SKU_ONLY` |
| SPU 编码 | `spu_id` | varchar(64) | 建议 | 商品基础表 | 商品基础表 SPU 编码 |
| SPU 名称 | `spu_name` | varchar(256) | 建议 | 商品基础表 | 商品基础表 SPU 名称 |
| 代表 SKU 编码 | `representative_sku_id` | varchar(64) | 必须 | 主表聚合 | 展示和追溯使用的代表 SKU |
| 成员 SKU 列表 JSON | `member_sku_list_json` | json/string | 必须 | 主表聚合 | 汇总到同一标准商品下的 SKU 列表 |
| 成员 SKU 数 | `member_sku_cnt` | bigint | 必须 | 主表聚合 | 标准商品下 SKU 数 |
| 标准商品销售额 | `product_sales_amt` | decimal(18,6) | 必须 | 主表聚合 | 标准商品层目标画像销售额 |
| 标准商品销售标准量 | `product_sales_qty` | decimal(18,6) | 必须 | 主表聚合 | 标准商品层目标画像销售标准量 |
| 标准商品小票数 | `product_ticket_cnt` | bigint | 必须 | 主表聚合 | 标准商品层去重小票数 |
| 标准商品购买会员数 | `product_buyer_cnt` | bigint | 必须 | 主表聚合 | 标准商品层去重会员数 |
| 标准商品毛利额 | `product_margin_amt` | decimal(18,6) | 必须 | 主表聚合 | 标准商品层目标画像毛利额 |
| 标准商品毛利率 | `product_margin_rate` | decimal(18,8) | 必须 | 主表聚合 | 标准商品层目标画像毛利率 |
| 标准商品综合表现分 | `product_performance_score` | decimal(18,8) | 必须 | 主表聚合/重算 | 标准商品层综合表现分 |
| 表现分组 | `performance_group` | varchar(64) | 必须 | 主表聚合/重算 | 见第 29.6 节状态约束 |
| 是否正式锚点 | `is_formal_anchor` | tinyint | 必须 | 本算法 | `1` 是正式锚点，`0` 不是 |
| 锚点生命周期状态 | `anchor_lifecycle_status` | varchar(64) | 必须 | 本算法 | 见第 29.6 节状态约束 |
| 锚点证据类型 | `anchor_evidence_type` | varchar(64) | 必须 | 本算法 | 见第 29.6 节状态约束 |
| 结果状态 | `result_status` | varchar(64) | 必须 | 本算法 | 见第 29.6 节状态约束 |
| 计算时间 | `calculated_at` | datetime | 必须 | 系统生成 | 结果写入时间 |

### 29.4 锚点汇总：`mart_target_profile_anchor_summary`

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

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| SKU 表现模型版本 | `sku_performance_model_version` | varchar(64) | 必须 | 算法 04 参数 | 算法 04 本次计算版本 |
| 数据周期开始日期 | `performance_start_date` | date | 必须 | 调度参数 | 统计周期开始日期 |
| 数据周期结束日期 | `performance_end_date` | date | 必须 | 调度参数 | 统计周期结束日期 |
| 范围版本 | `scope_version` | varchar(64) | 必须 | 城市算法区域映射表 | 城市算法区域版本 |
| 范围类型 | `scope_type` | varchar(32) | 必须 | 城市算法区域映射表 | `CITY` / `CITY_CLUSTER` |
| 范围编码 | `scope_id` | varchar(64) | 必须 | 城市算法区域映射表 | 城市或城市群编码 |
| 范围名称 | `scope_name` | varchar(128) | 必须 | 城市算法区域映射表 | 城市或城市群名称 |
| 品类颗粒度 | `category_granularity` | varchar(32) | 必须 | 商品基础表 | 大类 / 中类 / 小类 |
| 品类编码 | `category_code` | varchar(64) | 必须 | 商品基础表 | 当前计算品类编码 |
| 品类名称 | `category_name` | varchar(128) | 必须 | 商品基础表 | 当前计算品类名称 |
| 门店群类型 | `store_group_type` | varchar(32) | 必须 | 算法 02 | `FINAL_LEVEL` / `ALL_RATED` |
| 门店品类等级 | `final_level` | varchar(32) | 必须 | 算法 02 | 当前门店群等级 |
| 消费者画像 | `final_profile` | varchar(128) | 必须 | 算法 01/03 | 当前消费者画像 |
| 当前锚点 SKU JSON | `active_anchor_skus_json` | json/string | 必须 | 主表筛选 | 当前可订可售且通过正式准入的锚点 SKU |
| 历史锚点 SKU JSON | `historical_anchor_skus_json` | json/string | 必须 | 主表筛选 | 历史表现好但当前不可订不可售的 SKU |
| 低订购高表现 SKU JSON | `low_order_high_performance_skus_json` | json/string | 必须 | 主表筛选 | 订购覆盖低但表现高的机会 SKU |
| 时间敏感锚点 SKU JSON | `time_sensitive_anchor_skus_json` | json/string | 必须 | 主表筛选 | 对月份或时段依赖较强的锚点 SKU |
| 门店集中锚点 SKU JSON | `store_concentrated_anchor_skus_json` | json/string | 必须 | 主表筛选 | 表现集中在少数门店的锚点 SKU |
| 相对锚点候选 JSON | `relative_anchor_candidates_json` | json/string | 必须 | 主表筛选 | 小样本或双 SKU 场景下的相对锚点候选 |
| 正式锚点数量 | `formal_anchor_cnt` | bigint | 必须 | 本算法 | `is_formal_anchor = 1` 的 SKU 数 |
| 历史锚点数量 | `historical_anchor_cnt` | bigint | 必须 | 本算法 | 历史锚点 SKU 数 |
| 结果状态 | `result_status` | varchar(64) | 必须 | 本算法 | 见第 29.6 节状态约束 |
| 质量指标 JSON | `quality_metrics_json` | json/string | 必须 | 本算法 | 本组结果质量指标汇总 |
| 计算时间 | `calculated_at` | datetime | 必须 | 系统生成 | 结果写入时间 |

### 29.5 参数表：`mart_target_profile_sku_performance_params`

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
| 参数作用范围键 | `parameter_scope_key` | varchar(256) | 必须 | 本算法 | 范围、品类、门店群、画像等组成的参数作用范围 |
| 参数分组 | `param_group` | varchar(64) | 必须 | 本算法 | `CRITIC` / `JENKS_BIC` / `JEFFREYS` / `UNIT_MAPPING` / `COST` / `PROMOTION` |
| 参数编码 | `param_code` | varchar(128) | 必须 | 本算法 | 参数唯一编码 |
| 参数名称 | `param_name` | varchar(256) | 必须 | 本算法 | 参数中文名称 |
| 指标编码 | `metric_code` | varchar(128) | 建议 | 本算法 | 参数对应的指标编码 |
| 参数数值 | `param_value_decimal` | decimal(18,8) | 建议 | 本算法 | 数值型参数 |
| 参数文本值 | `param_value_text` | varchar(512) | 建议 | 本算法 | 文本型参数 |
| 参数 JSON 值 | `param_value_json` | json/string | 建议 | 本算法 | 权重、相关矩阵、Jenks/BIC、Jeffreys、单位映射等复杂参数 |
| 样本数 | `sample_cnt` | bigint | 建议 | 本算法 | 参数计算使用的样本数 |
| 是否回退 | `fallback_flag` | tinyint | 必须 | 本算法 | `1` 使用回退参数，`0` 未回退 |
| 回退原因 | `fallback_reason` | varchar(512) | 建议 | 本算法 | 样本不足、MAD 为 0、单位未知等原因 |
| 关联算法步骤 | `algorithm_step` | varchar(128) | 必须 | 本算法 | 该参数用于哪个计算步骤 |
| 计算时间 | `calculated_at` | datetime | 必须 | 系统生成 | 参数写入时间 |

### 29.6 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `repurchase_calc_status` | 复购计算状态 | `OK` | 复购计算成功 | 分母大于 0 且观察窗口完整 |
| `repurchase_calc_status` | 复购计算状态 | `DENOMINATOR_ZERO` | 复购分母为 0 | 可观察首购会员数为 0 |
| `repurchase_calc_status` | 复购计算状态 | `INSUFFICIENT_WINDOW` | 观察窗口不足 | 周期尾部无法观察完整 T+1 到 T+7 |
| `valid_transaction_filter_method` | 有效交易过滤方式 | `SOURCE_TABLE_CLEANED` | 源表已清洗 | 数据开发确认 Doris 主表已保留有效正向销售 |
| `valid_transaction_filter_method` | 有效交易过滤方式 | `RULE_FILTERED` | 算法任务内过滤 | 算法 04 按 `order_status`、`is_return`、`usual_amt`、`weight` 等字段过滤 |
| `standard_product_mode` | 标准商品模式 | `SPU_MAPPED` | 已按 SPU 归并 | 商品基础表有有效 `spu_id` |
| `standard_product_mode` | 标准商品模式 | `SKU_ONLY` | 只按销售 SKU 计算 | `spu_id` 为空或无法稳定映射 |
| `orderable_sellable_flag` | 是否可订可售 | `0` / `1` | 当前快照是否可订且可售 | `1` 表示门店 SKU 可订可售表中同时可订、可售；否则为 `0` |
| `listing_status` | 在售状态 | `ACTIVE` | 当前可订可售 | 当前快照可订且可售 |
| `listing_status` | 在售状态 | `INACTIVE` | 当前不可订不可售 | 当前快照不可订或不可售 |
| `orderable_scope` | 订购范围口径 | `STORE_SKU_ORDERABLE` | 门店 SKU 可订范围 | V1 使用门店 SKU 每日可订可售表确定允许订购门店和门店日分母 |
| `orderable_scope` | 订购范围口径 | `GROUP_ALL_STORES` | 门店群全部门店回退 | 仅当门店级可订范围无法交付时回退使用，并写入数据质量标记 |
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
| `preference_reference_status` | 偏好参考组状态 | `SINGLE_PROFILE` | 只有目标画像 | 同一比较组只有目标画像，偏好指数不适用 |
| `result_status` | 结果状态 | `SUCCESS` | 计算成功 | 当前比较组正常产出结果 |
| `result_status` | 结果状态 | `SINGLE_SKU` | 只有一个有效 SKU | 比较组内只有 1 个有效 SKU |
| `result_status` | 结果状态 | `NO_OBVIOUS_HIGH_SKU` | 无明显高表现 SKU | Jenks/BIC 未形成高表现组 |
| `result_status` | 结果状态 | `NO_TARGET_PROFILE_CONSUMPTION` | 目标画像无有效消费 | 当前范围目标画像没有有效消费 |
| `result_status` | 结果状态 | `NO_VALID_SKU` | 无有效 SKU | 商品、交易或在售过滤后无有效 SKU |
| `result_status` | 结果状态 | `DATA_INCOMPLETE` | 数据不完整 | 核心输入缺失但可保留诊断 |
| `result_status` | 结果状态 | `PRODUCT_MASTER_CONFLICT` | 商品主数据冲突 | 同一销售 SKU 匹配多条当前商品基础记录 |
| `result_status` | 结果状态 | `SELL_THROUGH_DATA_ERROR` | 售罄数据异常 | 到货或销售标准量无法构造有效售罄率 |
| `result_status` | 结果状态 | `UPSTREAM_VERSION_ERROR` | 上游版本错误 | 算法 01/02/03 混用多个正式版本或缺失 |
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
| `attribute_status` | 属性状态 | `COMPLETE` | 属性较完整 | 商品属性满足解释字段要求 |
| `attribute_status` | 属性状态 | `ATTRIBUTE_INCOMPLETE` | 属性不完整 | 商品属性缺失，不阻断经营表现计算 |
| `performance_group` | 表现分组 | `HIGH_PERFORMANCE` | 高表现组 | Jenks/BIC 判定为高表现 |
| `performance_group` | 表现分组 | `MIDDLE_PERFORMANCE` | 中表现组 | Jenks/BIC 判定为中表现 |
| `performance_group` | 表现分组 | `LOW_PERFORMANCE` | 低表现组 | Jenks/BIC 判定为低表现 |
| `performance_group` | 表现分组 | `NO_OBVIOUS_HIGH_SKU` | 无明显高表现 | 未形成可发布高表现组 |
| `anchor_lifecycle_status` | 锚点生命周期状态 | `ACTIVE_ANCHOR` | 当前锚点 | 当前可订可售且通过正式锚点准入 |
| `anchor_lifecycle_status` | 锚点生命周期状态 | `HISTORICAL_ANCHOR` | 历史锚点 | 贡献周期内表现较好但当前不可订不可售 |
| `anchor_lifecycle_status` | 锚点生命周期状态 | `NOT_ANCHOR` | 非锚点 | 未通过正式锚点准入且不属于历史锚点 |
| `anchor_evidence_type` | 锚点证据类型 | `ACTIVE_STABLE_ANCHOR` | 当前稳定锚点 | 当前可订可售、证据充分且稳定 |
| `anchor_evidence_type` | 锚点证据类型 | `LOW_ORDER_HIGH_PERFORMANCE` | 低订购高表现 | 订购覆盖低但实际表现高 |
| `anchor_evidence_type` | 锚点证据类型 | `TIME_SENSITIVE_ANCHOR` | 时间敏感锚点 | 只在特定月份或时段表现突出 |
| `anchor_evidence_type` | 锚点证据类型 | `STORE_CONCENTRATED_ANCHOR` | 门店集中锚点 | 表现集中在少数门店 |
| `anchor_evidence_type` | 锚点证据类型 | `RELATIVE_ANCHOR_CANDIDATE` | 相对锚点候选 | 小样本或双 SKU 场景下的相对候选 |
| `anchor_evidence_type` | 锚点证据类型 | `NOT_ANCHOR` | 非锚点 | 未通过锚点准入 |
| `fallback_flag` | 是否回退 | `0` / `1` | 参数是否使用回退 | 参数表中 `1` 表示该参数因样本不足、MAD 为 0、单位未知等原因使用回退口径 |

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
sku_buyer_penetration
repurchase_rate_7d_pre19
preference_index
Jeffreys 95% 下界
non_promo_pre1930_sell_through_rate
target_profile_sku_margin_amt
sku_performance_score
Jenks+BIC 分组
is_formal_anchor
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
不可订不可售但历史表现好
目标画像毛利不为正
商品映射冲突
计量单位无法转换
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

本节不是重新向业务确认数据粒度。毛利损耗表、可订可售表和价格表的粒度已经按数据合同确定；开发交付时只需要按合同验收是否稳定产出。

| 编号 | 验收项 | 影响 |
|---|---|---|
| D1 | 抽样验收 `sales_standard_qty = weight` 与商品基础表单位是否匹配 | 目标画像标准销售量、毛利、售罄率、折扣阶梯 |
| D2 | 毛利损耗表按数据合同在营业日期 + 门店编码 + 交易商品编码粒度稳定、唯一地提供销售额和全链路毛利额 | 成本反推 |
| D3 | 门店 SKU 可订可售表按数据合同在日期 + 门店编码 + 销售商品编码粒度主键唯一，并稳定提供是否可订、是否可售 | 当前在售、正式锚点 |
| D4 | 毛利损耗表按数据合同稳定提供门店进货数量、门店进货重量、门店订购数量（订购单位）、门店订购数量（重量口径） | 有效在售 SKU 日、售罄率、订购覆盖 |
| D5 | Doris 有效交易过滤按 `order_status`、`is_return`、`refund_type`、`business_source` 等字段完成，测试交易和异常交易不进入结果 | 有效交易口径 |

---

## 35. 不能做的事

```text
不能把候选新品当成算法 04 已验证的现有锚点
不能用固定销售、复购和毛利权重
不能把订购率直接加入综合得分
不能用 Min-Max 替代稳健标准化
不能用固定人数门槛替代 Jeffreys 证据判断
不能跳过 Jenks+BIC 动态锚点分组
不能把当前不可订不可售商品标成 ACTIVE_ANCHOR
不能将不同比较组的综合得分直接横向比较
不能将综合得分说成新品成功概率
```

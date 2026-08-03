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
新品候选方向生成的商品证据
机会评分和大模型解释的证据
```

### 1.2 算法不做什么

算法 04 不直接回答：

```text
应该开发什么新品
新品应该增加什么配料
新品应该定什么价格
新品是否与现有货盘重复
```

候选新品必须由后续购物篮算法、新品方向生成、价格带算法、竞品趋势、风险过滤等继续产生。

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
购物篮算法：寻找真实关联商品或食材
        ↓
锚点商品属性 + 已验证关联属性
        ↓
历史差销、现有货盘、价格、竞品、趋势和风险过滤
        ↓
具象新品候选
```

锚点与新品必须分开：

```text
现有锚点：黑椒牛柳丝 200g
购物篮关联：圆葱、青椒
候选新品：圆葱黑椒牛柳丝 200g、青椒黑椒牛柳丝 200g
```

算法 04 不得把候选新品提前写成已验证现有锚点。

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

采购手动选择其他消费者类型
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
| 算法 01 正式会员画像 | 必须 | 取得每名会员唯一 `final_profile` | `mart_customer_profile` 或算法 01 正式交付表 |
| 算法 02 正式门店品类等级 | 必须 | 取得正式门店群和 `final_level` | `mart_store_category_level` |
| 算法 03 消费者贡献结果 | 必须 | 取得主力、相对主力和消费者类型范围 | `mart_profile_contribution` 或算法 03 正式交付表 |
| 小票商品明细 | 必须 | 销售、销量、小票、会员及购买时间 | Doris 小票商品明细 |
| 商品基础表 | 必须 | 商品编码、名称、品类、单位、属性、SPU | 商品基础表 |
| 实际到货/订购明细 | 必须 | 有效在售 SKU 日、实际收货量、订购覆盖 | 毛利损耗表 + 门店 SKU 可订可售表 |
| 商品毛利明细 | 必须 | 销售额、成本金额、毛利额 | 毛利损耗表，成本口径需确认 |
| 促销与原价明细 | 必须 | 非促销 SKU 日、实付价格和折扣阶梯 | V1 用 `discount_amt > 0` 代理 |
| 日历、门店、城市群 | 必须 | 日期、月份、门店及正式范围 | 门店基础表 + 城市算法区域映射表 |
| 7 天复购结果 | 必须 | 复购分子、分母、原始复购率 | V1 先产出 `mart_sku_repurchase_7d_pre19` |

### 5.2 Doris 小票商品明细字段

| 中文字段名 | 逻辑字段名 | Doris 候选字段 | 是否必须 | 中文注释 |
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
| 交易状态 | transaction_status | 待开发确认 | 条件必须 | 退货、取消、冲销、测试交易过滤 |

### 5.3 商品基础表字段

| 中文字段名 | 逻辑字段名 | 是否必须 | 中文注释 |
|---|---|---|---|
| 交易商品编码 | sku_id | 必须 | 与 Doris `article_id` 对齐 |
| 商品名称 | sku_name | 必须 | SKU 展示名称 |
| SPU编码 | spu_id | 可选 | 标准商品层聚合 |
| 换码/替代组ID | replacement_group_id | 可选 | 标准商品层聚合 |
| 大类编码/名称 | large_category_code/name | 条件必须 | 大类计算 |
| 中类编码/名称 | middle_category_code/name | 条件必须 | 中类计算 |
| 小类编码/名称 | small_category_code/name | 条件必须 | 小类计算 |
| 单位 | source_unit | 必须 | 计量标准化 |
| 单位重量/净含量 | net_content / unit_weight | 条件必须 | 定量包装、件转重量 |
| 可订可售标记 | orderable_sellable_flag | 条件必须 | 若单独可订可售表提供，可从其取得 |
| 商品属性 | main_ingredient 等 | 可选 | 锚点属性输出，缺失不阻断经营表现 |

### 5.4 毛利损耗表字段

| 中文字段名 | 逻辑字段名 | 是否必须 | 中文注释 |
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

| 中文字段名 | 逻辑字段名 | 是否必须 | 中文注释 |
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

| 中文字段名 | 逻辑字段名 | 是否必须 | 中文注释 |
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
销售数量 > 0
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
```

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
weight = SUM(weight)
sales_qty = SUM(sales_qty)
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
= SUM(目标画像购买该 SKU 的 standard_sales_qty)

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
件、份、盒、包、袋、瓶、个 -> QUANTITY
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

raw_preference_index
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
preference_status = NO_REFERENCE_PROFILE
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
净到货量 = 门店实际收货重量或数量

净到货量 <= 0
-> 不进入售罄率分母
```

异常：

```text
售罄率 < 0 或明显异常
-> result_status = SELL_THROUGH_DATA_ERROR
```

### 14.3 门店群售罄率

```text
pre1930_sell_through_rate
= 门店群非促销 SKU 日 19:30 前销售标准量
  / 门店群非促销 SKU 日实际收货标准量

non_promo_pre1930_sell_through_rate
= 同一非促销窗口内的 19:30 前售罄率
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
= daily_store_sku_cost_amt / daily_store_sku_total_standard_sales_qty

target_profile_daily_store_sku_cost_amt
= target_profile_daily_store_sku_standard_sales_qty
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

由于 Doris `weight` 已确认可统一作为目标画像标准销售量，V1 默认不启用销售额占比分摊成本。

只有在个别 SKU 或个别日期出现 `weight` 缺失、`weight <= 0`、计量类型无法识别等异常，导致目标画像标准销售量无法取得时，才允许进入异常兜底判断：

```text
target_profile_daily_store_sku_cost_amt
= daily_store_sku_cost_amt
 * target_profile_daily_store_sku_sales_amt
 / daily_store_sku_sales_amt

cost_allocation_method = SALES_AMOUNT_SHARE_DEGRADED
cost_allocation_status = COST_ALLOCATED_DEGRADED
```

销售额占比分摊不是默认口径。若需求评审未明确允许异常兜底，则相关 SKU 输出：

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
supplier：供应商
```

### 17.2 来源优先级

```text
1. 商品基础表、配方/BOM、供应商规格书
2. 已审核 SKU 属性字典
3. SKU 名称、商品描述和包装规格规则解析
4. AI 结构化抽取
```

冲突优先级：

```text
配方/BOM > 商品基础表 > 属性字典 > 名称规则 > AI 抽取
```

每个属性保存：

```text
attribute_value
attribute_source
attribute_confidence
attribute_version
```

AI 只能提取文本中实际存在的属性，不能猜测。

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
标准商品层：按正式 spu_id、换码或替代关系汇总同一实物商品
```

仅在商品基础表明确存在同一 `spu_id`、旧新编码或替代关系时合并。

V1 没有可靠 SPU / 换码关系时：

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
ACTIVE_ANCHOR
= 当前可订可售且通过正式锚点准入

HISTORICAL_ANCHOR
= 贡献周期内有真实销售且表现较好，但当前不可订不可售
```

历史锚点进入新品或复开发前必须检查：

```text
停售原因
历史订购表现
供应商状态
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

### 28.1 计算状态

```text
SUCCESS
SINGLE_SKU
NO_OBVIOUS_HIGH_SKU
NO_TARGET_PROFILE_CONSUMPTION
NO_VALID_SKU
DATA_INCOMPLETE
PRODUCT_MASTER_CONFLICT
SELL_THROUGH_DATA_ERROR
UPSTREAM_VERSION_ERROR
UPSTREAM_RECONCILIATION_ERROR
```

### 28.2 独立业务状态

```text
is_formal_anchor
listing_status: ACTIVE / INACTIVE
profitability_status: POSITIVE_MARGIN / NON_POSITIVE_MARGIN
evidence_status: SUFFICIENT / LOW_EVIDENCE
time_stability_status: STABLE / TIME_SENSITIVE / INSUFFICIENT_TIME_SAMPLE
store_stability_status: STABLE / STORE_CONCENTRATED / INSUFFICIENT_STORE_SAMPLE
natural_sales_status: VALID / NO_NATURAL_SALES_WINDOW
order_coverage_status: HIGH / LOW / NO_OBVIOUS_SPLIT
attribute_status: COMPLETE / ATTRIBUTE_INCOMPLETE
```

状态拆分保存，避免创建大量难维护组合标签。

---

## 29. 输出表

算法 04 正式输出按业务原文保留 4 类结果表。

V1 额外新增 1 张前置复购结果表。

### 29.1 前置表：`mart_sku_repurchase_7d_pre19`

| 中文字段名 | 逻辑字段名 | 类型建议 | 是否必须 | 中文注释 |
|---|---|---|---|---|
| 数据周期开始日期 | performance_start_date | DATE | 必须 | 统计周期开始 |
| 数据周期结束日期 | performance_end_date | DATE | 必须 | 统计周期结束 |
| 范围类型 | scope_type | STRING | 必须 | CITY / CITY_CLUSTER |
| 范围ID | scope_id | STRING | 必须 | 城市或城市群编码 |
| 品类颗粒度 | category_granularity | STRING | 必须 | large / middle / small |
| 品类编码 | category_code | STRING | 必须 | 品类编码 |
| 门店群类型 | store_group_type | STRING | 必须 | final_level / ALL_RATED |
| 门店品类等级 | final_level | STRING | 必须 | A/B/C/D 或 ALL_RATED |
| 消费者画像 | final_profile | STRING | 必须 | 算法 01 最终画像 |
| SKU编码 | sku_id | STRING | 必须 | 销售 SKU |
| 7天复购会员数 | repeat_buyer_cnt_7d_pre19 | BIGINT | 必须 | T+1 到 T+7 且 19:00 前复购 |
| 7天可观察首购会员数 | eligible_first_buyer_cnt_7d | BIGINT | 必须 | 有完整观察窗口的首购会员 |
| 7天19点前复购率 | repurchase_rate_7d_pre19 | DECIMAL | 必须 | 复购会员数 / 可观察首购会员数 |
| 复购口径版本 | repurchase_model_version | STRING | 必须 | 复购计算版本 |
| 计算状态 | repurchase_calc_status | STRING | 必须 | OK / DENOMINATOR_ZERO / INSUFFICIENT_WINDOW |
| 更新时间 | calculated_at | DATETIME | 必须 | 任务时间 |

### 29.2 SKU 表现明细：`mart_target_profile_sku_performance`

范围与版本字段：

```text
sku_performance_model_version
performance_start_date / performance_end_date
scope_version / scope_type / scope_id / scope_name
category_granularity
large_category_code / large_category_name
middle_category_code / middle_category_name
small_category_code / small_category_name
store_group_type / final_level / store_cnt
final_profile / is_main_profile / is_relative_main_candidate
profile_model_version
category_level_model_version
consumer_contribution_model_version
category_mapping_version
sku_attribute_version
listing_snapshot_date
```

商品与在售字段：

```text
sku_id / product_code / sku_name
spu_id / replacement_group_id
standard_product_mode
orderable_sellable_flag / listing_status
measurement_type / source_unit / standard_unit / conversion_factor / measurement_mapping_status
ordered_store_cnt / store_order_rate / ordered_store_day_rate
```

原始行为字段：

```text
sku_sales_amt / sku_sales_qty
sku_ticket_cnt / sku_buyer_cnt
sku_sales_share / sku_ticket_penetration
sku_buyer_penetration_raw / sku_buyer_penetration_lower_95 / sku_buyer_penetration_upper_95
target_penetration / reference_penetration
preference_index_raw / smoothed_preference_index / preference_lower_95 / preference_upper_95
repeat_buyer_cnt_7d_pre19
eligible_first_buyer_cnt_7d
repurchase_rate_7d_pre19_raw / repurchase_rate_7d_pre19_lower_95 / repurchase_rate_7d_pre19_upper_95
```

经营与价格字段：

```text
available_store_day_cnt
sales_per_available_store_day
buyers_per_available_store_day
pre1930_sell_through_rate
non_promo_pre1930_sell_through_rate
pre1930_sales_volume_per_available_store_day
target_profile_pre1930_absorption_rate
discount_ladder_json
target_profile_sku_sales_amt
target_profile_sku_cost_amt
target_profile_sku_margin_amt / target_profile_sku_margin_rate
sku_total_sales_amt / sku_total_cost_amt
sku_total_margin_amt / sku_total_margin_rate
cost_source / cost_allocation_method / cost_allocation_status
sku_avg_paid_price / standardized_paid_price
promotion_identify_method
```

得分与锚点字段：

```text
contribution_dimension_score
preference_dimension_score
natural_sales_dimension_score
margin_dimension_score
dimension_weights_json
point_evidence_score
sku_performance_score
selected_cluster_count
jenks_breaks_json
sse_by_k_json
bic_by_k_json
performance_group
is_formal_anchor
anchor_evidence_type
```

稳定性、属性与状态字段：

```text
top1_store_sales_share / store_sales_hhi
leave_one_store_anchor_rate / store_stability_status
leave_one_month_anchor_rate / time_stability_status
main_ingredient / product_form / ingredient / flavor
processing_method / cooking_method / net_content
package_type / storage_temperature / brand / supplier
attribute_source_json / attribute_confidence_json
result_status / profitability_status / evidence_status
natural_sales_status / order_coverage_status / attribute_status
data_quality_flags
calculated_at
```

### 29.3 标准商品表现：`mart_target_profile_product_performance`

按正式：

```text
spu_id / replacement_group_id
```

聚合换码后的同一实物商品，同时保留：

```text
member_sku_list_json
standard_product_mode
replacement_source
```

V1 若无可靠 SPU / 换码关系：

```text
standard_product_mode = SKU_ONLY
product_key = sku_id
```

但标准商品表结构保留。

### 29.4 锚点汇总：`mart_target_profile_anchor_summary`

一条结果代表：

```text
一个周期 + 一个范围 + 一个品类 + 一个门店群 + 一个消费者类型
```

输出：

```text
active_anchor_skus_json
historical_anchor_skus_json
low_order_high_performance_skus_json
time_sensitive_anchor_skus_json
store_concentrated_anchor_skus_json
relative_anchor_candidates_json
result_status
quality_metrics_json
calculated_at
```

### 29.5 参数表：`mart_target_profile_sku_performance_params`

保存：

```text
稳健标准化参数
二级与一级 CRITIC 权重和相关矩阵
Jeffreys 区间参数
Jenks/BIC 参数
计量单位转换关系
商品编码换码关系
属性字典和属性版本
promotion_identify_method
cost_source
```

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

## 31. 开发验收

### 31.1 上游对账

检查：

```text
算法 04 SKU 销售额合计 = 算法 03 对应画像销售额
算法 04 使用的 final_profile 与算法 01 唯一
算法 04 使用的 final_level 与算法 02 唯一
```

### 31.2 唯一性

正式结果表不允许同一唯一粒度重复。

### 31.3 公式复算

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

### 31.4 分层追溯

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

### 31.5 稳定性与后验

检查：

```text
留一门店验证
留一月验证
下一周期后验表现
```

### 31.6 边界场景

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

## 32. 当前已确认口径

| 事项 | 结论 |
|---|---|
| 无促销活动表 | V1 使用 `discount_amt > 0` 代理 |
| 促销识别标记 | `promotion_identify_method = DISCOUNT_PROXY_V1` |
| SKU 维度复购 | V1 先产出 `mart_sku_repurchase_7d_pre19` |
| SPU / 换码关系不足 | V1 允许 `standard_product_mode = SKU_ONLY`，但保留标准商品层设计 |
| 商品属性缺失 | 不阻断经营表现计算，标记 `ATTRIBUTE_INCOMPLETE` |
| 小票销售标准量字段 | 算法 04 使用 `sales_standard_qty = weight`；计量类型和单位由商品基础表解释，字段事实详见 Doris 字段字典 |
| 毛利损耗表数量字段 | 数据开发可按数据合同交付进货数量、进货重量、订购数量订购单位、订购数量重量口径 |

---

## 33. 当前仍需开发确认

| 编号 | 确认项 | 影响 |
|---|---|---|
| D1 | 开发交付时抽样验收 `sales_standard_qty = weight` 与商品基础表单位是否匹配 | 目标画像标准销售量、毛利、售罄率、折扣阶梯 |
| D2 | 开发交付的毛利损耗表是否按数据合同实现，并在营业日期 + 门店编码 + 交易商品编码粒度稳定提供全链路毛利额 | 成本反推 |
| D3 | 开发交付的门店 SKU 可订可售表是否按数据合同实现，并在日期 + 门店编码 + 销售商品编码粒度主键唯一 | 当前在售、正式锚点 |
| D4 | 毛利损耗表中的门店进货数量、门店进货重量、门店订购数量（订购单位）、门店订购数量（重量口径）是否按数据合同稳定交付 | 有效在售 SKU 日、售罄率、订购覆盖 |
| D5 | 退货、取消、冲销、测试交易在 Doris 的过滤状态 | 有效交易口径 |

---

## 34. 不能做的事

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

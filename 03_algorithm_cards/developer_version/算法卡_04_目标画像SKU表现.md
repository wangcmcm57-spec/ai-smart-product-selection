# 算法卡 04：目标画像 SKU 表现算法

版本：V1.0 开发评审版  
生成日期：2026-07-31  
文档状态：待数据开发字段映射、Doris 试跑和业务验收  
业务基准：`01_业务原始与补充文档/业务补充算法文档/算法卡_04_目标画像SKU表现_业务提供最新原始版_20260731.md`  
业务解读版：`04_业务解读版/目标画像SKU表现算法_业务解读版.md`

## 1. 算法目标

本算法用于识别目标消费者画像下的现有高表现 SKU 锚点。

它只回答：

```text
在某个城市算法区域 + 某个品类 + 某个门店品类等级群 + 某个消费者类型下，
哪些现有 SKU 的目标画像贡献、相对偏好、复购、自然动销和毛利表现较好，
可以作为后续购物篮和新品方向生成的锚点。
```

本算法不做：

```text
不重新计算会员画像
不重新计算门店品类等级
不重新计算门店群主力消费者类型
不直接生成新品
不计算新品价格带
不读取外部竞品数据
不使用固定经验权重替代 CRITIC
不按名称相似自动合并 SKU
```

## 2. 正式交付表

V1 正式交付以下表。

### 2.1 SKU 7天19点前复购中间表

表名：

```text
mart_sku_repurchase_7d_pre19
```

用途：

```text
先从 Doris 小票明细计算 SKU 级复购结果。
算法 04 正式结果表读取该表中的复购字段。
```

表性质：

```text
正式中间结果表，可复用、可验收、可追溯。
```

### 2.2 目标画像 SKU 表现明细表

表名：

```text
mart_target_profile_sku_performance
```

用途：

```text
算法 04 的核心正式结果表。
```

### 2.3 目标画像标准商品表现表

表名：

```text
mart_target_profile_product_performance
```

V1 口径：

```text
第一版允许 SKU_ONLY。
如果没有稳定 SPU、换码或替代关系，不强行合并。
```

### 2.4 目标画像锚点汇总表

表名：

```text
mart_target_profile_anchor_summary
```

用途：

```text
给后续购物篮算法、新品候选方向生成和 AI 商品机会推荐读取。
```

### 2.5 参数与解释表

建议表名：

```text
mart_target_profile_sku_performance_param
```

用途：

```text
保存标准化参数、CRITIC 权重、Jenks/BIC 断点、Jeffreys 参数和版本血缘。
```

## 3. 计算周期与版本

正式评估周期：

```text
最近 3 个数据完整自然月
```

例如 2026 年 7 月运行：

```text
performance_start_date = 2026-04-01
performance_end_date   = 2026-06-30
```

更新频率：

```text
每月正式更新一次。
```

同一批结果必须锁定以下版本：

```text
sku_performance_model_version
profile_model_version
category_level_model_version
consumer_contribution_model_version
scope_version
sku_category_version
sku_attribute_version
source_data_version
```

任一上游正式版本变化时，算法 04 必须全量重算对应周期，禁止混用不同版本。

## 4. 计算范围与结果粒度

正式范围：

```text
scope_type = CITY 或 CITY_CLUSTER
scope_id   = 城市编码或城市算法区域编码
```

门店群：

```text
store_group_type = FINAL_LEVEL 或 ALL_RATED
final_level      = A / B / C / D / ALL_RATED
```

品类颗粒度：

```text
category_granularity = LARGE / MIDDLE / SMALL
category_code        = 对应品类编码
```

SKU 表现明细唯一键：

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

说明：

```text
一行表示某个周期、某个范围、某个品类、某个门店群、某个消费者类型下，一个 SKU 的表现。
```

## 5. 输入表清单

| 输入表 | 逻辑表名 | 是否必须 | 用途 |
|---|---|---|---|
| Doris 小票商品明细表 | `data_agent.dws_member_order_item_detail_df_all` | 必须 | 计算目标画像购买、销售、小票、会员、复购、分时段销售 |
| 会员画像结果表 | `dim_customer_profile` | 必须 | 读取会员唯一 `final_profile` |
| 门店品类等级表 | `mart_store_category_level` | 必须 | 读取门店在品类下的 `final_level` |
| 门店群消费者画像贡献表 | `mart_store_group_consumer_contribution` | 必须 | 读取本范围内所有有效画像及主力画像标记 |
| 门店基础表 | `dim_store` | 必须 | 补充城市、门店状态、区域 |
| 城市算法区域映射表 | `dim_city_algorithm_region` | 必须 | 确定城市算法区域 |
| 商品基础表 | `dim_sku` | 必须 | 映射 SKU、品类、单位、SPU、属性 |
| 毛利损耗表 | 待开发确认 | 必须 | 日门店 SKU 销售、毛利、进货、折扣、损耗等经营字段 |
| 门店商品日价格表 | 待开发确认 | 条件必须 | 成本备选口径、价格解释 |
| 门店 SKU 可订可售表 | 待开发确认 | 必须 | 判断当前可订可售 |

## 6. 输入字段清单

### 6.1 Doris 小票商品明细表

来源表：

```text
data_agent.dws_member_order_item_detail_df_all
```

| 中文字段名 | 逻辑字段名 | Doris 字段 | 是否必须 | 中文注释 |
|---|---|---|---|---|
| 订单商品明细ID | `order_item_id` | `order_item_id` | 必须 | 商品行唯一键，用于明细去重 |
| 小票ID | `ticket_id` | `order_id` | 必须 | 已确认全公司唯一，用于小票数 |
| 业务日期 | `business_date` | `business_date` | 必须 | 交易所属营业日期 |
| 交易时间 | `trade_time` | `inc_time` | 必须 | 用于 19:00 复购和 19:30 自然动销 |
| 门店编码 | `store_id` | `store_id` | 必须 | 对齐门店基础表和门店品类等级表 |
| 会员编码 | `customer_id` | `customer_id` | 必须 | 关联会员画像；非会员不进入目标画像计算 |
| 交易商品编码 | `sku_id` | `article_id` | 必须 | 销售条码，算法 04 的 SKU |
| 实付金额 | `paid_sales_amt` | `usual_amt` | 必须 | 商品行实付金额 |
| 优惠金额 | `discount_amt` | `discount_amt` | 建议 | V1 促销代理判断辅助 |
| 是否时段促销 | `hour_promo_flag` | `is_hour_promotion` | 建议 | 时段折扣解释辅助 |
| 时段优惠金额 | `hour_discount_amt` | `hour_discount_amt` | 只作辅助 | 会员当天同小时累计优惠金额，不能直接按商品行求和 |
| 销售重量 | `sales_weight` | `weight` | 建议 | 称重商品销售量 |
| 订单状态 | `order_status` | `order_status` | 必须 | V1 保留正常完成订单 |
| 退款类型 | `refund_type` | `refund_type` | 必须 | V1 剔除退款/退货 |
| 是否退货 | `is_return` | `is_return` | 必须 | V1 剔除退货 |
| 数据更新时间 | `source_update_time` | `update_time` | 建议 | 源数据追溯 |

### 6.2 会员画像结果表

| 中文字段名 | 逻辑字段名 | 是否必须 | 中文注释 |
|---|---|---|---|
| 画像模型版本 | `profile_model_version` | 必须 | 锁定正式画像版本 |
| 画像周期开始日期 | `profile_start_date` | 必须 | 画像计算周期 |
| 画像周期结束日期 | `profile_end_date` | 必须 | 画像计算周期 |
| 会员编码 | `customer_id` | 必须 | 对齐小票会员 |
| 最终画像 | `final_profile` | 必须 | 算法 04 的消费者类型 |
| 结果状态 | `result_status` | 必须 | 只读取正式有效画像 |

### 6.3 门店品类等级表

| 中文字段名 | 逻辑字段名 | 是否必须 | 中文注释 |
|---|---|---|---|
| 门店品类等级模型版本 | `category_level_model_version` | 必须 | 锁定算法 02 正式版本 |
| 城市算法区域编码 | `scope_id` | 必须 | 对齐算法范围 |
| 城市算法区域名称 | `scope_name` | 必须 | 展示和校验 |
| 品类颗粒度 | `category_granularity` | 必须 | 大类/中类/小类 |
| 品类编码 | `category_code` | 必须 | 对齐商品基础表分类 |
| 门店编码 | `store_id` | 必须 | 组建门店群 |
| 最终等级 | `final_level` | 必须 | A/B/C/D |
| 结果状态 | `result_status` | 必须 | 只读取正式成功结果 |

### 6.4 门店群消费者画像贡献表

| 中文字段名 | 逻辑字段名 | 是否必须 | 中文注释 |
|---|---|---|---|
| 贡献模型版本 | `consumer_contribution_model_version` | 必须 | 锁定算法 03 正式版本 |
| 城市算法区域编码 | `scope_id` | 必须 | 与算法 04 范围一致 |
| 品类颗粒度 | `category_granularity` | 必须 | 与算法 04 品类一致 |
| 品类编码 | `category_code` | 必须 | 与算法 04 品类一致 |
| 门店群类型 | `store_group_type` | 必须 | FINAL_LEVEL / ALL_RATED |
| 门店品类等级 | `final_level` | 必须 | A/B/C/D/ALL_RATED |
| 最终画像 | `final_profile` | 必须 | 算法 04 计算的消费者类型 |
| 是否主力画像 | `is_main_profile` | 必须 | 产品默认展示 |
| 是否相对主力候选 | `is_relative_main_candidate` | 建议 | NO_OBVIOUS_MAIN 场景展示 |
| 结果状态 | `result_status` | 必须 | 只读取正式有效贡献结果 |

### 6.5 商品基础表

| 中文字段名 | 逻辑字段名 | 是否必须 | 中文注释 |
|---|---|---|---|
| 交易商品编码 | `sku_id` | 必须 | 对齐小票 `article_id` |
| 商品名称 | `sku_name` | 必须 | 展示和核验 |
| 大类编码 | `large_category_code` | 必须 | 品类筛选 |
| 大类名称 | `large_category_name` | 必须 | 展示 |
| 中类编码 | `middle_category_code` | 必须 | 品类筛选 |
| 中类名称 | `middle_category_name` | 必须 | 展示 |
| 小类编码 | `small_category_code` | 必须 | 品类筛选 |
| 小类名称 | `small_category_name` | 必须 | 展示 |
| SPU编码 | `spu_id` | 建议 | V1 可为空；有值时可做标准商品 |
| SPU名称 | `spu_name` | 建议 | 展示 |
| 规格 | `specification` | 建议 | 商品属性和单位换算 |
| 单位 | `source_unit` | 必须 | V1 识别重量/数量 |
| 单位重量 | `unit_weight` | 建议 | 计件商品折算重量时使用 |
| 品牌 | `brand` | 建议 | 商品属性 |
| 存储温层 | `storage_temperature` | 建议 | 商品属性 |
| 数据更新时间 | `sku_updated_at` | 必须 | 生成 `sku_category_version` |

V1 单位识别规则：

| 单位值示例 | `measurement_type` | `standard_unit` |
|---|---|---|
| 千克 / kg / 公斤 | WEIGHT | kg |
| g / 克 | WEIGHT | kg |
| 件 / 份 / 盒 / 包 / 袋 / 瓶 / 个 | QUANTITY | 件 |
| 无法识别 | UNKNOWN | UNKNOWN |

真实商品基础表交付后，开发需输出单位分布样例。无法识别的单位先标记：

```text
measurement_mapping_status = UNKNOWN
```

### 6.6 毛利损耗表

表粒度：

```text
营业日期 + 门店编码 + 交易商品编码
```

| 中文字段名 | 逻辑字段名 | 是否必须 | 中文注释 |
|---|---|---|---|
| 营业日期 | `business_date` | 必须 | 对齐小票和价格表 |
| 门店编码 | `store_id` | 必须 | 对齐小票 `store_id` |
| 交易商品编码 | `sku_id` | 必须 | 对齐小票 `article_id` |
| 销售额 | `daily_sku_sales_amt` | 必须 | 日门店 SKU 全部消费者销售额 |
| 销售数量 | `daily_sku_sales_qty` | 必须 | 计件商品全日销售量 |
| 销售重量 | `daily_sku_sales_weight` | 条件必须 | 称重商品全日销售量 |
| 19:30前销售额 | `pre1930_sales_amt` | 条件必须 | 自然动销使用；如只有 19点前字段，需由 Doris 小票按 `inc_time < 19:30:00` 补算 |
| 19:30前销售数量 | `pre1930_sales_qty` | 条件必须 | 自然动销使用；计件商品标准销售量 |
| 19:30前销售重量 | `pre1930_sales_weight` | 条件必须 | 自然动销使用；称重商品标准销售量 |
| 19点前销售额 | `pre19_sales_amt` | 建议 | 19:00 前销售解释，不可替代 19:30 自然动销 |
| 19点前销售数量 | `pre19_sales_qty` | 建议 | 19:00 前销售解释，不可替代 19:30 自然动销 |
| 19点前销售重量 | `pre19_sales_weight` | 建议 | 19:00 前销售解释，不可替代 19:30 自然动销 |
| 19点前平均售价 | `pre19_avg_price` | 建议 | 价格解释 |
| 门店进货数量 | `store_purchase_qty` | 必须 | 实际到货/收货数量 |
| 门店进货金额 | `store_purchase_amt` | 建议 | 到货成本备用 |
| 门店订购数量 | `store_order_qty` | 建议 | 订购覆盖 |
| 门店订购额 | `store_order_amt` | 建议 | 订购覆盖 |
| 全链路毛利额 | `full_chain_margin_amt` | 必须 | V1 优先毛利口径 |
| 全链路毛利率 | `full_chain_margin_rate` | 建议 | 毛利解释 |
| 门店毛利额 | `store_margin_amt` | 建议 | 补充解释 |
| 总折扣额 | `total_discount_amt` | 建议 | 促销代理 |
| 促销折扣额 | `promo_discount_amt` | 建议 | 非促销 SKU 日判断 |
| 时段折扣额 | `hour_discount_amt_agg` | 建议 | 19:30 后折扣解释 |
| 门店损耗金额 | `store_loss_amt` | 建议 | 不进入 04 综合分，仅留作对账解释 |
| 数据更新时间 | `source_update_time` | 建议 | 追溯 |

### 6.7 门店商品日价格表

原始粒度：

```text
日期 + 门店编码 + 销售商品编码 + 验收商品编码
```

算法 04 使用前必须先聚合到：

```text
日期 + 门店编码 + 销售商品编码
```

| 中文字段名 | 逻辑字段名 | 是否必须 | 中文注释 |
|---|---|---|---|
| 日期 | `business_date` | 必须 | 优先营业日期 |
| 门店编码 | `store_id` | 必须 | 对齐小票 |
| 销售商品编码 | `sku_id` | 必须 | 对齐小票 `article_id` |
| 验收商品编码 | `receipt_sku_id` | 必须 | 聚合前保留，防止一对多 |
| 出库到店成本含税 | `arrival_cost_amt_tax_included` | 条件必须 | 全链路成本不可推导时的 V1 成本备选 |
| 出库到店金额含税 | `arrival_amount_tax_included` | 建议 | 成本金额校验 |
| 门店进货金额 | `store_purchase_amt` | 建议 | 成本备用 |
| 销售原价 | `list_price` | 建议 | 价格解释 |
| 商品平均售价 | `avg_paid_price` | 建议 | 价格解释 |
| 19点前平均售价 | `pre19_avg_paid_price` | 建议 | 价格解释 |
| 19点后售价 | `post19_price` | 建议 | 折扣解释 |
| 总折扣额 | `total_discount_amt` | 建议 | 促销代理 |
| 数据更新时间 | `source_update_time` | 建议 | 追溯 |

### 6.8 门店 SKU 可订可售表

表粒度：

```text
日期 + 门店编码 + 销售商品编码
```

| 中文字段名 | 逻辑字段名 | 是否必须 | 中文注释 |
|---|---|---|---|
| 日期 | `snapshot_date` | 必须 | 可订可售快照日期 |
| 门店编码 | `store_id` | 必须 | 对齐门店群 |
| 销售商品编码 | `sku_id` | 必须 | 对齐小票 `article_id` |
| 订购商品编码 | `order_sku_id` | 建议 | 订购条码，保留 |
| 是否可售 | `is_sellable` | 必须 | 1 可售，0 不可售 |
| 是否可订 | `is_orderable` | 必须 | 1 可订，0 不可订 |
| 数据更新时间 | `source_update_time` | 建议 | 追溯 |

V1 当前可订可售判断：

```text
orderable_sellable_flag = CASE WHEN is_orderable = 1 AND is_sellable = 1 THEN 1 ELSE 0 END
```

## 7. 前置过滤

### 7.1 有效交易过滤

只保留正常完成的正向销售：

```text
customer_id IS NOT NULL
sku_id IS NOT NULL
paid_sales_amt > 0
销售数量或销售重量 > 0
order_status 为正常完成状态
is_return = 0
refund_type 为空或非退款
剔除测试交易、冲销交易、取消交易
剔除赠品和零金额行
```

V1 具体状态值以 Doris 字段验收结果为准。

### 7.2 小票内同 SKU 合并

同一小票内同一 SKU 多行时，先合并：

```text
ticket_id + sku_id
```

聚合字段：

```text
SUM(paid_sales_amt)
SUM(sales_weight)
COUNT(DISTINCT order_item_id)
```

说明：

```text
order_id 已确认全公司唯一，不需要拼接 store_id。
```

### 7.3 上游唯一性检查

计算前必须检查：

```text
同一 profile_model_version + customer_id 只能有一个 final_profile
同一 category_level_model_version + scope + category + store_id 只能有一个 final_level
同一 consumer_contribution_model_version + scope + category + final_level + final_profile 只能有一条贡献结果
同一 sku_category_version + sku_id 只能命中一个正式品类
```

如果不唯一：

```text
result_status = UPSTREAM_VERSION_ERROR
停止发布正式结果
```

## 8. 标准销售量

### 8.1 计量类型

根据商品基础表 `source_unit` 判断：

```text
千克、kg、公斤、g、克 -> WEIGHT
件、份、盒、包、袋、瓶、个 -> QUANTITY
其他 -> UNKNOWN
```

### 8.2 标准量计算

称重商品：

```text
standard_sales_qty = sales_weight_kg
standard_unit = kg
```

计件商品：

```text
standard_sales_qty = sales_qty
standard_unit = 件
```

如果小票没有销售数量，计件商品可优先用毛利损耗表销售数量做日门店 SKU 层补充，明细层无法拆分时输出降级标记：

```text
measurement_mapping_status = DAILY_SKU_QTY_ALLOCATED
```

无法识别单位：

```text
measurement_mapping_status = UNKNOWN
数量深度和售罄率不进入正式自然动销得分
```

## 9. 前置中间表：SKU 7天19点前复购

### 9.1 计算目的

指标平台当前没有可直接用于算法 04 的 SKU 级复购结果。

因此 V1 必须从 Doris 小票明细自行计算：

```text
mart_sku_repurchase_7d_pre19
```

### 9.2 复购口径

对同一会员、同一 SKU：

```text
首次购买日 T：会员购买该 SKU 的日期，时间不限
复购：T+1 到 T+7 自然日内，再次购买同一 SKU，且第二次购买时间 < 19:00:00
同一天多张小票不算复购
周期结束前不足 7 天观察窗口的首次购买不进入分母
```

V1 观察起点：

```text
同一会员在同一计算周期内多次购买同一 SKU，
取周期内第一次购买该 SKU 的日期作为 T。
```

### 9.3 计算步骤

第一步，生成会员日 SKU 购买事实：

```text
member_sku_buy_day
= DISTINCT performance_period + scope + final_level + final_profile + customer_id + sku_id + business_date
```

第二步，找首次购买日：

```text
first_buy_date = MIN(business_date)
```

第三步，判断完整观察窗口：

```text
first_buy_date <= performance_end_date - 7 days
```

第四步，判断复购：

```text
EXISTS(
  同一 customer_id
  同一 sku_id
  business_date BETWEEN first_buy_date + 1 AND first_buy_date + 7
  trade_time < '19:00:00'
)
```

第五步，聚合到算法 04 粒度。

### 9.4 输出字段

表名：

```text
mart_sku_repurchase_7d_pre19
```

表粒度：

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

| 中文字段名 | 字段名 | 类型建议 | 是否必须 | 中文注释 |
|---|---|---|---|---|
| 复购模型版本 | `repurchase_model_version` | varchar | 必须 | SKU 复购计算版本 |
| 数据周期开始日期 | `performance_start_date` | date | 必须 | 复购观察周期开始 |
| 数据周期结束日期 | `performance_end_date` | date | 必须 | 复购观察周期结束 |
| 范围版本 | `scope_version` | varchar | 必须 | 城市算法区域版本 |
| 范围类型 | `scope_type` | varchar | 必须 | CITY / CITY_CLUSTER |
| 范围编码 | `scope_id` | varchar | 必须 | 城市或城市算法区域编码 |
| 范围名称 | `scope_name` | varchar | 建议 | 展示 |
| 品类颗粒度 | `category_granularity` | varchar | 必须 | LARGE / MIDDLE / SMALL |
| 品类编码 | `category_code` | varchar | 必须 | 当前评分品类 |
| 品类名称 | `category_name` | varchar | 必须 | 展示 |
| 门店群类型 | `store_group_type` | varchar | 必须 | FINAL_LEVEL / ALL_RATED |
| 门店品类等级 | `final_level` | varchar | 必须 | A/B/C/D/ALL_RATED |
| 最终画像 | `final_profile` | varchar | 必须 | 会员画像标签 |
| 销售商品编码 | `sku_id` | varchar | 必须 | 对齐小票 `article_id` |
| 销售商品名称 | `sku_name` | varchar | 建议 | 展示 |
| 7天观察窗口首购会员数 | `eligible_first_buyer_cnt_7d` | bigint | 必须 | 分母 |
| 7天19点前复购会员数 | `repeat_buyer_cnt_7d_pre19` | bigint | 必须 | 分子 |
| 7天19点前复购率原始值 | `repurchase_rate_7d_pre19_raw` | decimal(18,6) | 必须 | 分子 / 分母 |
| 复购率 Jeffreys 平滑值 | `repurchase_rate_7d_pre19_smoothed` | decimal(18,6) | 必须 | `(x+0.5)/(n+1)` |
| 复购率95%下界 | `repurchase_rate_7d_pre19_lower_95` | decimal(18,6) | 必须 | 正式评分使用 |
| 复购率95%上界 | `repurchase_rate_7d_pre19_upper_95` | decimal(18,6) | 必须 | 解释 |
| 结果状态 | `result_status` | varchar | 必须 | SUCCESS / NO_ELIGIBLE_WINDOW / DATA_INCOMPLETE |
| 计算时间 | `calculated_at` | datetime | 必须 | 写入时间 |

## 10. SKU 基础表现指标

在同一比较组、同一 `final_profile` 下计算。

比较组：

```text
performance_period
+ scope
+ category_granularity
+ category_code
+ store_group_type
+ final_level
+ final_profile
```

基础指标：

```text
sku_sales_amt
= SUM(目标画像购买该 SKU 的实付金额)

sku_sales_qty
= SUM(目标画像购买该 SKU 的标准销售量)

sku_ticket_cnt
= COUNT(DISTINCT 目标画像购买该 SKU 的 ticket_id)

sku_buyer_cnt
= COUNT(DISTINCT 目标画像购买该 SKU 的 customer_id)

profile_category_sales_amt
= SUM(目标画像在该品类的实付金额)

profile_category_buyer_cnt
= COUNT(DISTINCT 目标画像在该品类购买会员)

profile_category_ticket_cnt
= COUNT(DISTINCT 目标画像在该品类购买小票)
```

派生指标：

```text
sku_sales_share
= sku_sales_amt / profile_category_sales_amt

sku_buyer_penetration_raw
= sku_buyer_cnt / profile_category_buyer_cnt

sku_ticket_penetration
= sku_ticket_cnt / profile_category_ticket_cnt

sku_avg_paid_price
= sku_sales_amt / sku_sales_qty
```

## 11. 目标画像相对偏好

### 11.1 对照组

目标画像与其他画像比较时，必须在相同可购买门店日内比较。

参考组：

```text
同一周期
+ 同一城市算法区域
+ 同一品类
+ 同一门店等级群
+ 同一 SKU 有效可购买门店日
+ 除目标画像外的全部有效消费者类型
```

### 11.2 原始偏好

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

### 11.3 Jeffreys 平滑和下界

```text
p_t = (x_t + 0.5) / (n_t + 1)
p_o = (x_o + 0.5) / (n_o + 1)

preference_index_smoothed = p_t / p_o
```

下界按业务原文近似：

```text
log_rr = ln(p_t / p_o)

se_log_rr
= sqrt(
    1/(x_t + 0.5) - 1/(n_t + 1)
  + 1/(x_o + 0.5) - 1/(n_o + 1)
  )

preference_index_lower_95 = exp(log_rr - 1.96 * se_log_rr)
preference_index_upper_95 = exp(log_rr + 1.96 * se_log_rr)
```

如果算法 03 只有一个有效画像：

```text
preference_status = NO_REFERENCE_PROFILE
该指标从 CRITIC 中移除
```

## 12. 19:30 前自然动销

### 12.1 非促销 SKU 日

业务原文口径：

```text
门店 + 日期 + SKU
19:30 前没有参加商品活动
并且 19:30 前没有商品促销折扣
```

V1 没有促销活动表时，按以下优先级：

```text
1. 毛利损耗表或日门店SKU汇总中的促销折扣额、时段折扣额
2. 小票 discount_amt > 0 作为代理口径
```

如果使用代理：

```text
promotion_source = PROMOTION_PROXY_V1
```

### 12.2 有效在售 SKU 日

有效在售 SKU 日：

```text
门店当天该 SKU 实际收货标准量 > 0
```

实际收货标准量优先来源：

```text
毛利损耗表：门店进货数量 / 销售重量口径
```

19:30 前销售标准量优先来源：

```text
1. 毛利损耗表或日清经营表中已拆分到 19:30 前的销售数量/销售重量
2. 如果只有 19点前字段，不可直接替代 19:30 前口径
3. 需要由 Doris 小票商品明细按 inc_time < '19:30:00' 补算
```

如果单位不明确：

```text
measurement_mapping_status = UNKNOWN
natural_sales_status = DATA_INCOMPLETE
```

### 12.3 售罄率和销售深度

```text
pre1930_sell_through_rate
= SUM(有效 SKU 日 19:30 前标准销售量)
 / SUM(有效 SKU 日实际收货标准量)

non_promo_pre1930_sell_through_rate
= SUM(非促销有效 SKU 日 19:30 前标准销售量)
 / SUM(非促销有效 SKU 日实际收货标准量)

pre1930_sales_volume_per_available_store_day
= SUM(有效 SKU 日 19:30 前标准销售量)
 / available_store_day_cnt
```

异常：

```text
19:30 前销售标准量 / 实际收货标准量 > 1.10
-> result_status = SELL_THROUGH_DATA_ERROR
-> 不进入自然动销得分
```

禁止把售罄率截断成 100%。

## 13. 商品毛利与目标画像成本

### 13.1 业务理想口径

业务最新原文：

```text
target_profile_sku_sales_amt
= SUM(目标画像购买该 SKU 的实付销售额)

target_profile_sku_cost_amt
= SUM(目标画像购买该 SKU 的成本金额)

target_profile_sku_margin_amt
= target_profile_sku_sales_amt - target_profile_sku_cost_amt
```

如果有交易行级成本：

```text
直接按目标画像购买明细 SUM 成本金额。
```

### 13.2 V1 优先落地口径：全链路毛利推导成本

如果毛利损耗表可以稳定提供：

```text
营业日期 + 门店编码 + 销售商品编码
的销售额和全链路毛利额
```

则计算：

```text
daily_sku_total_sales_amt = 毛利损耗表.销售额

daily_sku_full_chain_margin_amt = 毛利损耗表.全链路毛利额

daily_sku_full_chain_cost_amt
= daily_sku_total_sales_amt - daily_sku_full_chain_margin_amt
```

目标画像成本按销售额占比分摊：

```text
target_profile_daily_sku_sales_share
= target_profile_daily_store_sku_sales_amt
 / daily_sku_total_sales_amt

target_profile_daily_store_sku_cost_amt
= daily_sku_full_chain_cost_amt
 * target_profile_daily_sku_sales_share
```

汇总：

```text
target_profile_sku_cost_amt
= SUM(target_profile_daily_store_sku_cost_amt)

target_profile_sku_margin_amt
= target_profile_sku_sales_amt - target_profile_sku_cost_amt
```

输出：

```text
cost_source = FULL_CHAIN_MARGIN_DERIVED_COST
cost_allocation_method = SALES_AMOUNT_SHARE
cost_allocation_status = COST_ALLOCATED_V1
```

### 13.3 V1 备选落地口径：出库到店成本含税

如果全链路成本无法稳定推导，则使用门店商品日价格表的：

```text
出库到店成本含税
```

使用前必须先聚合：

```text
日期 + 门店编码 + 销售商品编码 + 验收商品编码
-> 日期 + 门店编码 + 销售商品编码
```

聚合公式：

```text
daily_sku_arrival_cost_amt_tax_included
= SUM(出库到店成本含税)
```

再分摊：

```text
target_profile_daily_store_sku_cost_amt
= daily_sku_arrival_cost_amt_tax_included
 * target_profile_daily_store_sku_sales_amt
 / daily_sku_total_sales_amt
```

输出：

```text
cost_source = ARRIVAL_COST_TAX_INCLUDED
cost_allocation_method = SALES_AMOUNT_SHARE
cost_allocation_status = COST_ALLOCATED_V1
```

### 13.4 成本异常处理

如果日门店 SKU 总销售额为 0：

```text
不做分摊
result_status = DATA_INCOMPLETE
```

如果成本金额缺失：

```text
target_profile_sku_cost_amt = NULL
target_profile_sku_margin_amt = NULL
profitability_status = MARGIN_DATA_INCOMPLETE
is_formal_anchor = 0
```

禁止：

```text
用 0 填充缺失成本
用同品类平均成本替代
重复扣减损耗
```

### 13.5 毛利底线

正式锚点必须同时满足：

```text
target_profile_sku_margin_amt > 0
sku_total_margin_amt > 0
```

否则：

```text
profitability_status = NON_POSITIVE_MARGIN
is_formal_anchor = 0
```

## 14. 19:30 后折扣阶梯

业务原文要求输出，但不进入综合得分。

输出字段建议：

```text
discount_ladder_json
```

JSON 内按半小时折扣档保存：

```text
19:30-20:00 销售标准量 / 增量售罄率 / 实际折扣率
20:00-20:30 销售标准量 / 增量售罄率 / 实际折扣率
20:30-21:00 销售标准量 / 增量售罄率 / 实际折扣率
其他实际营业折扣档同理
```

公式：

```text
band_incremental_sell_through_rate
= 该折扣档销售标准量 / 当日实际收货标准量

cumulative_sell_through_rate_at_band_end
= 截至该折扣档结束累计销售标准量 / 当日实际收货标准量
```

## 15. 小样本处理

比例指标必须保存：

```text
raw_rate
smoothed_rate
credible_lower_95
credible_upper_95
numerator_cnt
denominator_cnt
```

单个比例 Jeffreys 区间：

```text
posterior = Beta(x + 0.5, n - x + 0.5)
credible_lower_95 = BetaQuantile(0.025, posterior)
credible_upper_95 = BetaQuantile(0.975, posterior)
```

正式评分使用 95% 下界的指标：

```text
sku_buyer_penetration_lower_95
repurchase_rate_7d_pre19_lower_95
preference_index_lower_95
```

如果开发环境缺少 BetaQuantile 函数，需要使用等价数值实现，并在参数表保存实现版本。

## 16. 综合评分

### 16.1 四个一级维度

目标画像贡献：

```text
sku_sales_share
sku_buyer_penetration_lower_95
target_sales_per_available_store_day
```

目标画像偏好：

```text
preference_index_lower_95
repurchase_rate_7d_pre19_lower_95
```

19:30 前自然动销：

```text
non_promo_pre1930_sell_through_rate
pre1930_sales_volume_per_available_store_day
```

商品毛利：

```text
target_profile_sku_margin_amt
target_profile_sku_margin_rate
sku_total_margin_amt
sku_total_margin_rate
```

不进入综合得分：

```text
订购率
19:30 后折扣阶梯
价格和价格带
损耗
商品属性完整度
当前在售状态
```

### 16.2 指标转换

在同一比较组内处理：

```text
金额、每店日销售额、销售量深度：ln(1 + x)
偏好指数下界：ln(x)
比例和毛利率：保留原值
```

稳健 Z 分数：

```text
z_j = (x'_ij - median_j) / (1.4826 * MAD_j)
indicator_score_ij = 100 * Phi(z_j)
```

MAD 回退：

```text
MAD > 0：使用 MAD
MAD = 0 且 IQR > 0：使用 IQR / 1.349
MAD = 0、IQR = 0、标准差 > 0：使用标准差
全部 SKU 取值相同：移除该指标
```

### 16.3 CRITIC 动态赋权

在每个一级维度内先算二级指标权重，再对四个一级维度算权重。

公式：

```text
C_j = sigma_j * SUM_k(1 - corr_jk)
w_j = C_j / SUM(C_j)

dimension_score_d = SUM(indicator_score_j * w_j)
sku_performance_score = SUM(dimension_score_d * dimension_weight_d)
```

有效 SKU 数回退：

```text
有效 SKU 数 >= 3：正常运行 CRITIC
有效 SKU 数 = 2：不运行 CRITIC，使用四维 Pareto 比较
有效 SKU 数 = 1：result_status = SINGLE_SKU，不生成正式高表现组
```

## 17. Jenks+BIC 动态锚点组

对同一比较组的 `sku_performance_score` 从低到高排序：

```text
K_max = MIN(3, 综合得分去重值数量)
候选 K = 1 ... K_max
```

Jenks：

```text
SSE_K = SUM((score_i - 当前组均值)^2)
```

BIC：

```text
BIC(K) = N * ln(SSE_K / N + 1e-12) + K * ln(N)
```

选择：

```text
BIC 最小的 K
相同时选择更小 K
```

分组结果：

```text
K=3：高表现组 / 中表现组 / 低表现组
K=2：高表现组 / 低表现组
K=1：NO_OBVIOUS_HIGH_SKU
```

最高表现组进入正式锚点准入判断。

## 18. 正式锚点准入

正式锚点必须同时满足：

```text
1. 上游版本、商品编码、销售、到货、成本/毛利数据完整
2. orderable_sellable_flag = 1
3. target_profile_sku_margin_amt > 0
4. sku_total_margin_amt > 0
5. 置信度校正后的综合得分进入 Jenks 最高表现组
6. evidence_status != LOW_EVIDENCE
7. natural_sales_status = VALID
```

满足：

```text
is_formal_anchor = 1
anchor_type = ACTIVE_ANCHOR
```

历史锚点：

```text
贡献周期内有真实销售且表现较好
但当前不可订不可售
-> anchor_type = HISTORICAL_ANCHOR
-> is_formal_anchor = 0
```

非正式当前锚点场景：

```text
不可订不可售
只有 1 个 SKU 或 2 个 SKU 的相对候选
没有非促销自然销售窗口
消费者证据不足
目标画像或 SKU 整体商品毛利不为正
```

## 19. 稳定性验证

### 19.1 门店稳定性

```text
top1_store_sales_share
= 该 SKU 销售额最高门店销售额 / 门店群该 SKU 销售额

store_sales_hhi
= SUM(各门店该 SKU 销售额占比^2)
```

留一门店验证：

```text
删除每家覆盖该 SKU 的门店
重新计算指标、CRITIC 权重、综合分和 Jenks 分组

leave_one_store_anchor_rate
= 删除不同门店后仍进入锚点组的有效次数 / 有效验证次数
```

### 19.2 时间稳定性

保持会员画像版本和门店群不变：

```text
删除第 1 月，使用第 2 月 + 第 3 月重算
删除第 2 月，使用第 1 月 + 第 3 月重算
删除第 3 月，使用第 1 月 + 第 2 月重算
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

## 20. 输出字段：目标画像 SKU 表现明细表

表名：

```text
mart_target_profile_sku_performance
```

### 20.1 范围与版本字段

| 中文字段名 | 字段名 | 类型建议 | 是否必须 | 中文注释 |
|---|---|---|---|---|
| SKU表现模型版本 | `sku_performance_model_version` | varchar | 必须 | 算法 04 版本 |
| 数据周期开始日期 | `performance_start_date` | date | 必须 | 正式评估周期开始 |
| 数据周期结束日期 | `performance_end_date` | date | 必须 | 正式评估周期结束 |
| 范围版本 | `scope_version` | varchar | 必须 | 城市算法区域版本 |
| 范围类型 | `scope_type` | varchar | 必须 | CITY / CITY_CLUSTER |
| 范围编码 | `scope_id` | varchar | 必须 | 城市或城市算法区域编码 |
| 范围名称 | `scope_name` | varchar | 必须 | 展示 |
| 品类颗粒度 | `category_granularity` | varchar | 必须 | LARGE / MIDDLE / SMALL |
| 大类编码 | `large_category_code` | varchar | 建议 | 大类 |
| 大类名称 | `large_category_name` | varchar | 建议 | 大类 |
| 中类编码 | `middle_category_code` | varchar | 建议 | 中类 |
| 中类名称 | `middle_category_name` | varchar | 建议 | 中类 |
| 小类编码 | `small_category_code` | varchar | 建议 | 小类 |
| 小类名称 | `small_category_name` | varchar | 建议 | 小类 |
| 门店群类型 | `store_group_type` | varchar | 必须 | FINAL_LEVEL / ALL_RATED |
| 门店品类等级 | `final_level` | varchar | 必须 | A/B/C/D/ALL_RATED |
| 门店数 | `store_cnt` | bigint | 必须 | 门店群内有效门店数 |
| 最终画像 | `final_profile` | varchar | 必须 | 消费者类型 |
| 是否主力画像 | `is_main_profile` | tinyint | 必须 | 来自算法 03 |
| 是否相对主力候选 | `is_relative_main_candidate` | tinyint | 建议 | 来自算法 03 |
| 会员画像版本 | `profile_model_version` | varchar | 必须 | 上游版本 |
| 门店品类等级版本 | `category_level_model_version` | varchar | 必须 | 上游版本 |
| 画像贡献版本 | `consumer_contribution_model_version` | varchar | 必须 | 上游版本 |
| 商品分类版本 | `sku_category_version` | varchar | 必须 | 商品基础表分类口径 |
| 商品属性版本 | `sku_attribute_version` | varchar | 建议 | 属性来源版本 |

### 20.2 商品与在售字段

| 中文字段名 | 字段名 | 类型建议 | 是否必须 | 中文注释 |
|---|---|---|---|---|
| 销售商品编码 | `sku_id` | varchar | 必须 | 对齐小票 `article_id` |
| 商品编码 | `product_code` | varchar | 建议 | 商品主数据编码 |
| 商品名称 | `sku_name` | varchar | 必须 | 商品展示名 |
| SPU编码 | `spu_id` | varchar | 建议 | V1 可为空 |
| 替代/换码组编码 | `replacement_group_id` | varchar | 建议 | V1 可为空 |
| 标准商品口径 | `standard_product_mode` | varchar | 必须 | V1 默认 SKU_ONLY |
| 是否可订可售 | `orderable_sellable_flag` | tinyint | 必须 | 1 可订可售 |
| 上架状态 | `listing_status` | varchar | 必须 | ACTIVE / INACTIVE |
| 计量类型 | `measurement_type` | varchar | 必须 | WEIGHT / QUANTITY / UNKNOWN |
| 来源单位 | `source_unit` | varchar | 必须 | 商品基础表单位 |
| 标准单位 | `standard_unit` | varchar | 必须 | kg / 件 / UNKNOWN |
| 单位换算系数 | `conversion_factor` | decimal(18,6) | 建议 | 单位换算 |
| 单位映射状态 | `measurement_mapping_status` | varchar | 必须 | SUCCESS / UNKNOWN / DAILY_SKU_QTY_ALLOCATED |
| 订购门店数 | `ordered_store_cnt` | bigint | 建议 | 周期内实际订购过该 SKU 的门店数 |
| 门店订购率 | `store_order_rate` | decimal(18,6) | 建议 | ordered_store_cnt / 可订门店数 |
| 订购门店日率 | `ordered_store_day_rate` | decimal(18,6) | 建议 | 实际收货门店日 / 可订门店营业日 |

### 20.3 原始行为和偏好字段

| 中文字段名 | 字段名 | 类型建议 | 是否必须 | 中文注释 |
|---|---|---|---|---|
| SKU销售额 | `sku_sales_amt` | decimal(18,2) | 必须 | 目标画像购买该 SKU 实付销售额 |
| SKU标准销售量 | `sku_sales_qty` | decimal(18,6) | 必须 | 目标画像购买该 SKU 标准量 |
| SKU小票数 | `sku_ticket_cnt` | bigint | 必须 | 目标画像购买该 SKU 去重小票数 |
| SKU购买会员数 | `sku_buyer_cnt` | bigint | 必须 | 目标画像购买该 SKU 去重会员数 |
| SKU销售占比 | `sku_sales_share` | decimal(18,6) | 必须 | SKU销售额 / 目标画像品类销售额 |
| SKU小票渗透率 | `sku_ticket_penetration` | decimal(18,6) | 必须 | SKU小票数 / 目标画像品类小票数 |
| SKU会员渗透率原始值 | `sku_buyer_penetration_raw` | decimal(18,6) | 必须 | SKU购买会员 / 目标画像品类购买会员 |
| SKU会员渗透率95%下界 | `sku_buyer_penetration_lower_95` | decimal(18,6) | 必须 | 正式评分使用 |
| 目标画像渗透率 | `target_penetration` | decimal(18,6) | 必须 | 目标画像对该 SKU 的渗透 |
| 参考画像渗透率 | `reference_penetration` | decimal(18,6) | 条件必须 | 其他画像渗透 |
| 偏好指数原始值 | `preference_index_raw` | decimal(18,6) | 条件必须 | target / reference |
| 偏好指数平滑值 | `preference_index_smoothed` | decimal(18,6) | 条件必须 | Jeffreys 平滑 |
| 偏好指数95%下界 | `preference_index_lower_95` | decimal(18,6) | 条件必须 | 正式评分使用 |
| 偏好指数95%上界 | `preference_index_upper_95` | decimal(18,6) | 条件必须 | 解释 |
| 偏好状态 | `preference_status` | varchar | 必须 | VALID / NO_REFERENCE_PROFILE |

### 20.4 复购字段

| 中文字段名 | 字段名 | 类型建议 | 是否必须 | 中文注释 |
|---|---|---|---|---|
| 7天19点前复购会员数 | `repeat_buyer_cnt_7d_pre19` | bigint | 必须 | 来自 `mart_sku_repurchase_7d_pre19` |
| 7天观察窗口首购会员数 | `eligible_first_buyer_cnt_7d` | bigint | 必须 | 来自复购表 |
| 7天19点前复购率原始值 | `repurchase_rate_7d_pre19_raw` | decimal(18,6) | 必须 | 分子 / 分母 |
| 7天19点前复购率95%下界 | `repurchase_rate_7d_pre19_lower_95` | decimal(18,6) | 必须 | 正式评分使用 |
| 7天19点前复购率95%上界 | `repurchase_rate_7d_pre19_upper_95` | decimal(18,6) | 必须 | 解释 |

### 20.5 经营、成本和价格字段

| 中文字段名 | 字段名 | 类型建议 | 是否必须 | 中文注释 |
|---|---|---|---|---|
| 有效在售门店日数 | `available_store_day_cnt` | bigint | 必须 | 实际收货标准量 > 0 的门店日 |
| 每有效在售门店日销售额 | `sales_per_available_store_day` | decimal(18,6) | 必须 | 销售深度 |
| 19:30前售罄率 | `pre1930_sell_through_rate` | decimal(18,6) | 必须 | 全部有效 SKU 日 |
| 非促销19:30前售罄率 | `non_promo_pre1930_sell_through_rate` | decimal(18,6) | 必须 | 自然动销评分 |
| 19:30前每店日标准销售量 | `pre1930_sales_volume_per_available_store_day` | decimal(18,6) | 必须 | 自然动销评分 |
| 目标画像19:30前吸收率 | `target_profile_pre1930_absorption_rate` | decimal(18,6) | 建议 | 解释字段 |
| 折扣阶梯JSON | `discount_ladder_json` | json/string | 建议 | 只解释，不进综合分 |
| 目标画像SKU销售额 | `target_profile_sku_sales_amt` | decimal(18,2) | 必须 | 目标画像购买该 SKU 实付金额 |
| 目标画像SKU成本金额 | `target_profile_sku_cost_amt` | decimal(18,2) | 必须 | V1 按销售额占比分摊 |
| 目标画像SKU毛利额 | `target_profile_sku_margin_amt` | decimal(18,2) | 必须 | 销售额 - 成本金额 |
| 目标画像SKU毛利率 | `target_profile_sku_margin_rate` | decimal(18,6) | 必须 | 毛利额 / 销售额 |
| SKU整体销售额 | `sku_total_sales_amt` | decimal(18,2) | 必须 | 全部消费者购买该 SKU 销售额 |
| SKU整体成本金额 | `sku_total_cost_amt` | decimal(18,2) | 必须 | V1 成本口径 |
| SKU整体毛利额 | `sku_total_margin_amt` | decimal(18,2) | 必须 | 整体销售额 - 整体成本 |
| SKU整体毛利率 | `sku_total_margin_rate` | decimal(18,6) | 必须 | 整体毛利额 / 整体销售额 |
| 成本来源 | `cost_source` | varchar | 必须 | FULL_CHAIN_MARGIN_DERIVED_COST / ARRIVAL_COST_TAX_INCLUDED |
| 成本分摊方法 | `cost_allocation_method` | varchar | 必须 | SALES_AMOUNT_SHARE |
| 成本分摊状态 | `cost_allocation_status` | varchar | 必须 | COST_ALLOCATED_V1 / DIRECT_LINE_COST / DATA_INCOMPLETE |
| 平均实付价 | `sku_avg_paid_price` | decimal(18,6) | 建议 | 价格解释 |
| 标准化实付价 | `standardized_paid_price` | decimal(18,6) | 建议 | 每 kg / 每件等 |

### 20.6 得分、锚点和状态字段

| 中文字段名 | 字段名 | 类型建议 | 是否必须 | 中文注释 |
|---|---|---|---|---|
| 目标画像贡献维度分 | `contribution_dimension_score` | decimal(18,6) | 必须 | 一级维度分 |
| 目标画像偏好维度分 | `preference_dimension_score` | decimal(18,6) | 必须 | 一级维度分 |
| 自然动销维度分 | `natural_sales_dimension_score` | decimal(18,6) | 必须 | 一级维度分 |
| 商品毛利维度分 | `margin_dimension_score` | decimal(18,6) | 必须 | 一级维度分 |
| 维度权重JSON | `dimension_weights_json` | json/string | 必须 | 四个一级维度权重 |
| 点估计证据分 | `point_evidence_score` | decimal(18,6) | 必须 | 用平滑点估计计算 |
| SKU综合表现分 | `sku_performance_score` | decimal(18,6) | 必须 | 正式评分，使用下界 |
| 选择分组数 | `selected_cluster_count` | int | 必须 | Jenks+BIC K |
| Jenks断点JSON | `jenks_breaks_json` | json/string | 必须 | 分组断点 |
| BIC结果JSON | `bic_by_k_json` | json/string | 必须 | BIC 追溯 |
| 表现分组 | `performance_group` | varchar | 必须 | HIGH / MEDIUM / LOW / NO_OBVIOUS_HIGH_SKU |
| 是否正式锚点 | `is_formal_anchor` | tinyint | 必须 | 1 是，0 否 |
| 锚点类型 | `anchor_type` | varchar | 必须 | ACTIVE_ANCHOR / HISTORICAL_ANCHOR / NONE |
| 结果状态 | `result_status` | varchar | 必须 | SUCCESS 等 |
| 毛利状态 | `profitability_status` | varchar | 必须 | POSITIVE_MARGIN / NON_POSITIVE_MARGIN / MARGIN_DATA_INCOMPLETE |
| 证据状态 | `evidence_status` | varchar | 必须 | SUFFICIENT / LOW_EVIDENCE |
| 自然动销状态 | `natural_sales_status` | varchar | 必须 | VALID / NO_NATURAL_SALES_WINDOW / DATA_INCOMPLETE |
| 订购覆盖状态 | `order_coverage_status` | varchar | 建议 | HIGH / LOW / NO_OBVIOUS_SPLIT |
| 属性状态 | `attribute_status` | varchar | 必须 | COMPLETE / ATTRIBUTE_INCOMPLETE |
| 门店稳定状态 | `store_stability_status` | varchar | 建议 | STABLE / STORE_CONCENTRATED / INSUFFICIENT_STORE_SAMPLE |
| 时间稳定状态 | `time_stability_status` | varchar | 建议 | STABLE / TIME_SENSITIVE / INSUFFICIENT_TIME_SAMPLE |
| 计算时间 | `calculated_at` | datetime | 必须 | 写入时间 |

## 21. 输出字段：标准商品表现表

表名：

```text
mart_target_profile_product_performance
```

V1 粒度：

```text
与 SKU 表现明细相同，但 product_id 可等于 sku_id，standard_product_mode = SKU_ONLY。
```

必须字段：

| 中文字段名 | 字段名 | 类型建议 | 是否必须 | 中文注释 |
|---|---|---|---|---|
| 标准商品表现模型版本 | `product_performance_model_version` | varchar | 必须 | 标准商品层版本 |
| SKU表现模型版本 | `sku_performance_model_version` | varchar | 必须 | 来源明细版本 |
| 标准商品编码 | `standard_product_id` | varchar | 必须 | V1 SKU_ONLY 时等于 sku_id |
| 标准商品名称 | `standard_product_name` | varchar | 必须 | V1 等于商品名称 |
| 标准商品口径 | `standard_product_mode` | varchar | 必须 | SKU_ONLY / SPU / REPLACEMENT_GROUP |
| 成员SKU列表 | `member_sku_json` | json/string | 必须 | V1 单个 SKU |
| 是否正式锚点 | `is_formal_anchor` | tinyint | 必须 | 来源 SKU 结果或合并后结果 |
| 综合表现分 | `product_performance_score` | decimal(18,6) | 必须 | V1 等于 SKU 分 |
| 计算时间 | `calculated_at` | datetime | 必须 | 写入时间 |

## 22. 输出字段：锚点汇总表

表名：

```text
mart_target_profile_anchor_summary
```

表粒度：

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

| 中文字段名 | 字段名 | 类型建议 | 是否必须 | 中文注释 |
|---|---|---|---|---|
| SKU表现模型版本 | `sku_performance_model_version` | varchar | 必须 | 算法 04 版本 |
| 数据周期开始日期 | `performance_start_date` | date | 必须 | 周期开始 |
| 数据周期结束日期 | `performance_end_date` | date | 必须 | 周期结束 |
| 范围编码 | `scope_id` | varchar | 必须 | 城市/城市算法区域 |
| 品类编码 | `category_code` | varchar | 必须 | 当前品类 |
| 门店群类型 | `store_group_type` | varchar | 必须 | FINAL_LEVEL / ALL_RATED |
| 门店品类等级 | `final_level` | varchar | 必须 | A/B/C/D/ALL_RATED |
| 最终画像 | `final_profile` | varchar | 必须 | 消费者类型 |
| 当前正式锚点SKU | `active_anchor_skus_json` | json/string | 必须 | 当前可订可售正式锚点 |
| 历史锚点SKU | `historical_anchor_skus_json` | json/string | 建议 | 历史表现好但当前不可订不可售 |
| 低铺货高表现SKU | `low_order_high_performance_skus_json` | json/string | 建议 | 扩店机会 |
| 时间敏感锚点SKU | `time_sensitive_anchor_skus_json` | json/string | 建议 | 分月验证后标记 |
| 门店集中锚点SKU | `store_concentrated_anchor_skus_json` | json/string | 建议 | 分店验证后标记 |
| 相对锚点候选 | `relative_anchor_candidates_json` | json/string | 建议 | 两个 SKU Pareto 场景 |
| 结果状态 | `result_status` | varchar | 必须 | SUCCESS / NO_OBVIOUS_HIGH_SKU 等 |
| 质量指标 | `quality_metrics_json` | json/string | 建议 | 数据完整率、异常数等 |
| 计算时间 | `calculated_at` | datetime | 必须 | 写入时间 |

## 23. 参数表

表名：

```text
mart_target_profile_sku_performance_param
```

表粒度：

```text
sku_performance_model_version
+ performance_start_date
+ performance_end_date
+ scope
+ category
+ store_group
+ final_profile
+ param_type
```

字段：

| 中文字段名 | 字段名 | 类型建议 | 是否必须 | 中文注释 |
|---|---|---|---|---|
| 参数模型版本 | `sku_performance_model_version` | varchar | 必须 | 算法 04 版本 |
| 参数类型 | `param_type` | varchar | 必须 | STANDARDIZATION / CRITIC / JENKS_BIC / JEFFREYS / MEASUREMENT |
| 参数名称 | `param_name` | varchar | 必须 | 参数名称 |
| 参数值JSON | `param_value_json` | json/string | 必须 | 参数内容 |
| 适用范围JSON | `scope_key_json` | json/string | 必须 | 适用比较组 |
| 计算时间 | `calculated_at` | datetime | 必须 | 写入时间 |

## 24. 结果状态枚举

计算状态：

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

业务状态：

```text
listing_status: ACTIVE / INACTIVE
anchor_type: ACTIVE_ANCHOR / HISTORICAL_ANCHOR / NONE
profitability_status: POSITIVE_MARGIN / NON_POSITIVE_MARGIN / MARGIN_DATA_INCOMPLETE
evidence_status: SUFFICIENT / LOW_EVIDENCE
time_stability_status: STABLE / TIME_SENSITIVE / INSUFFICIENT_TIME_SAMPLE
store_stability_status: STABLE / STORE_CONCENTRATED / INSUFFICIENT_STORE_SAMPLE
natural_sales_status: VALID / NO_NATURAL_SALES_WINDOW / DATA_INCOMPLETE
order_coverage_status: HIGH / LOW / NO_OBVIOUS_SPLIT
attribute_status: COMPLETE / ATTRIBUTE_INCOMPLETE
measurement_mapping_status: SUCCESS / UNKNOWN / DAILY_SKU_QTY_ALLOCATED
promotion_source: FORMAL_PROMOTION / PROMOTION_PROXY_V1 / NOT_AVAILABLE
cost_source: FULL_CHAIN_MARGIN_DERIVED_COST / ARRIVAL_COST_TAX_INCLUDED / DIRECT_LINE_COST
```

## 25. 调度顺序

每月正式运行顺序：

```text
1. 确认算法 01、02、03 正式版本完成
2. 校验基础数据周期完整
3. 生成有效交易明细
4. 生成会员日 SKU 购买事实
5. 计算 mart_sku_repurchase_7d_pre19
6. 计算目标画像 SKU 基础行为指标
7. 计算目标画像相对偏好
8. 计算自然动销和折扣阶梯解释
9. 计算目标画像成本和毛利
10. 计算 Jeffreys 区间
11. 计算稳健标准化、CRITIC 权重和综合分
12. 计算 Jenks+BIC 分组
13. 判断正式锚点、历史锚点和状态
14. 写入 SKU 表现明细、标准商品表、锚点汇总表、参数表
15. 输出对账和验收报告
```

## 26. 验收规则

### 26.1 上游对账

同一范围、品类、门店群、消费者类型下：

```text
算法 04 各 SKU 目标画像销售额合计
= 算法 03 对应消费者类型销售额
```

允许因无效交易过滤产生小额差异，但必须输出差异率。

### 26.2 复购验收

抽样 20 个 SKU：

```text
检查首次购买日
检查 T+1 到 T+7 是否跨天
检查第二次购买是否 19:00 前
检查周期末不足 7 天是否未进分母
检查同一天多张小票是否未被算作复购
```

### 26.3 毛利验收

抽样 20 个日门店 SKU：

```text
复算目标画像销售额占比
复算成本分摊金额
复算目标画像毛利额
检查成本来源 cost_source 是否正确
```

### 26.4 自然动销验收

抽样检查：

```text
非促销 SKU 日判断
19:30 前销售标准量
实际收货标准量
售罄率是否未被截断
折扣阶梯是否只解释、不进综合分
```

### 26.5 锚点验收

业务抽样看：

```text
正式锚点是否当前可订可售
低证据 SKU 是否没有成为正式锚点
毛利不为正 SKU 是否被拦截
历史表现好但当前不可订不可售是否进入 HISTORICAL_ANCHOR
商品属性缺失是否只是 ATTRIBUTE_INCOMPLETE，没有阻断经营表现分
```

## 27. 当前仍需开发确认

| 确认项 | 影响 |
|---|---|
| 毛利损耗表是否稳定提供日门店 SKU 销售额和全链路毛利额 | 决定是否使用全链路毛利推导成本 |
| 门店商品日价格表出库到店成本含税是否稳定可取 | 全链路成本不可用时的备选 |
| 非促销 SKU 日是否能用正式促销字段判断 | 如果不能，V1 使用折扣代理并打标 |
| 商品基础表单位真实值分布 | 完善单位映射 |
| SPU、换码、替代关系何时可用 | 决定标准商品表是否从 SKU_ONLY 升级 |
| 交易状态字段枚举 | 精准过滤退货、取消、冲销、测试交易 |

以上确认项不阻断 V1 开发，但必须在上海试跑前完成字段验收。

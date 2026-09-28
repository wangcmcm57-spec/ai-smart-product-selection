# 毛利损耗表

目标表建议名：`mart_sku_margin_loss`

表用途：提供门店商品经营结果指标，用于门店品类等级、SKU 表现、毛利健康、折扣风险和损耗风险计算。

一行代表：一个营业日期 + 一个门店 + 一个交易商品。

主键：`business_date + store_id + sku_id`。

关联要求：门店编码对齐小票表 `store_id`，交易商品编码对齐小票表 `article_id`。

## 1. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 营业日期 | `business_date` | date | 必须 | `data_db.dwd_date_shop_sku.dt` | 门店经营日期 |
| 门店编码 | `store_id` | varchar(64) | 必须 | `data_db.dwd_date_shop_sku.shop_id` 或门店维表 | 必须和小票表 `store_id` 对齐 |
| 门店名称 | `store_name` | varchar(128) | 建议 | `data_db.dwd_date_shop_sku.shop_name` 或 `dim_store.store_name` | 展示和校验 |
| 城市 | `city_name` | varchar(64) | 必须 | `dim_store.city_name` | 区域筛选和算法区域映射 |
| 区域 | `area_name` | varchar(128) | 建议 | `dim_store.area_name` | 业务区域 |
| 管理区域 | `manage_area_name` | varchar(128) | 建议 | `dim_store.manage_area_name` | 管理口径 |
| 大区 | `region_name` | varchar(128) | 建议 | `dim_store.region_name` | 上级区域 |
| 交易商品编码 | `sku_id` | varchar(64) | 必须 | `data_db.dwd_date_shop_sku.sku_id` | 必须和小票表 `article_id` 对齐 |
| 商品编码 | `product_id` | varchar(64) | 建议 | `dim_sku.product_id` 或 `sku_id` | 商品主数据编码 |
| 商品名称 | `sku_name` | varchar(256) | 必须 | `data_db.dwd_date_shop_sku.sku_name` 或 `dim_sku.sku_name` | 商品名称 |
| 大类名称 | `category_level1_name` | varchar(128) | 必须 | `data_db.dwd_date_shop_sku.category_level1_name` 或 `dim_sku.category_level1_name` | 商品大类 |
| 中类名称 | `category_level2_name` | varchar(128) | 必须 | `data_db.dwd_date_shop_sku.category_level2_name` 或 `dim_sku.category_level2_name` | 商品中类 |
| 小类名称 | `category_level3_name` | varchar(128) | 必须 | `data_db.dwd_date_shop_sku.category_level3_name` 或 `dim_sku.category_level3_name` | 商品小类 |
| 结算单位 | `settlement_unit` | varchar(32) | 必须 | `dim_sku.sale_unit` 或经营指标来源 | 判断数量字段是计件口径还是重量口径 |
| 销售额 | `sales_amt` | decimal(18,6) | 必须 | `data_db.dwd_date_shop_sku.sale_amt` | 门店品类等级核心指标 |
| 销售数量 | `sales_qty` | decimal(18,6) | 必须 | `data_db.dwd_date_shop_sku.sale_qty` | 计件商品销售数量 |
| 销售重量 | `sales_weight_kg` | decimal(18,6) | 条件必须 | 开发补充门店+SKU+日粒度字段 | 称重商品销售重量，建议单位 kg |
| 原价销售额 | `original_sales_amt` | decimal(18,6) | 条件必须 | 开发补充门店+SKU+日粒度字段 | 判断自然动销和折扣依赖 |
| 19 点前销售额 | `pre19_sales_amt` | decimal(18,6) | 必须 | `data_db.dwd_date_shop_sku.bf19_sale_amt` | 19 点前时段销售额 |
| 19 点前销售数量 | `pre19_sales_qty` | decimal(18,6) | 必须 | `data_db.dwd_date_shop_sku.bf19_sale_qty` | 19 点前计件销售数量 |
| 19 点前销售重量 | `pre19_sales_weight_kg` | decimal(18,6) | 条件必须 | `data_db.dwd_date_shop_sku.bf19_sale_weight` 或开发补充 | 19 点前称重商品销售重量，建议单位 kg |
| 19 点前客数 | `pre19_customer_count` | bigint | 建议 | `data_db.dwd_date_shop_sku.bf19_cust_num` | 19 点前商品购买客数 |
| 总客数 | `customer_count` | bigint | 建议 | `data_db.dwd_date_shop_sku.cust_num` | 商品购买客数 |
| 会员来客数 | `member_customer_count` | bigint | 条件必须 | 开发补充门店+SKU+日粒度字段 | 会员贡献分析使用 |
| 19 点前会员来客数 | `pre19_member_customer_count` | bigint | 条件必须 | 开发补充门店+SKU+日粒度字段 | 会员时段贡献分析使用 |
| 门店进货金额 | `receipt_amt` | decimal(18,6) | 必须 | `data_db.dwd_date_shop_sku.receive_amt` | 实际验收金额 |
| 门店进货数量 | `receipt_qty` | decimal(18,6) | 必须 | `data_db.dwd_date_shop_sku.receive_qty` | 实际验收数量，计件商品售罄率分母优先使用 |
| 门店进货重量 | `receipt_weight_kg` | decimal(18,6) | 条件必须 | 开发补充门店+SKU+日粒度字段 | 实际验收重量，称重商品售罄率分母优先使用 |
| 门店订购额 | `order_amt` | decimal(18,6) | 建议 | `data_db.dwd_date_shop_sku.store_order_amt` | 订购金额 |
| 门店订购数量（订购单位） | `order_qty` | decimal(18,6) | 建议 | `data_db.dwd_date_shop_sku.store_order_qty` | 原订购单位数量，用于对账和订购满足率 |
| 门店订购数量（重量口径） | `order_weight_kg` | decimal(18,6) | 条件必须 | 开发补充门店+SKU+日粒度字段 | 订购数量换算重量，称重商品分析使用 |
| 供应链毛利额 | `supply_chain_margin_amt` | decimal(18,6) | 必须 | `data_db.dwd_date_shop_sku.scm_store_profit_amt` | 供应链毛利额，含税/不含税口径需在交付反馈中固定 |
| 门店毛利额 | `store_margin_amt` | decimal(18,6) | 必须 | `data_db.dwd_date_shop_sku.profit_amt` | 门店毛利额 |
| 全链路毛利额 | `full_link_margin_amt` | decimal(18,6) | 必须 | `data_db.dwd_date_shop_sku.full_link_store_profit_amt` | 全链路毛利额，机会评分核心字段 |
| 全链路毛利率 | `full_link_margin_rate` | decimal(18,8) | 必须 | `data_db.dwd_date_shop_sku.full_link_store_profit_rate` | 全链路毛利率，0 到 1 小数 |
| 门店毛利率 | `store_margin_rate` | decimal(18,8) | 必须 | `data_db.dwd_date_shop_sku.profit_rate` | 门店毛利率，0 到 1 小数 |
| 总折扣额 | `discount_amt` | decimal(18,6) | 必须 | `data_db.dwd_date_shop_sku.discount_amt` | 促销、会员、时段等折扣合计 |
| 折扣率 | `discount_rate` | decimal(18,8) | 必须 | `data_db.dwd_date_shop_sku.discount_rate` | 总折扣率，0 到 1 小数 |
| 促销折扣额 | `promotion_discount_amt` | decimal(18,6) | 建议 | `data_db.dwd_date_shop_sku.promotion_discount_amt` | 促销依赖分析使用 |
| 促销折扣率 | `promotion_discount_rate` | decimal(18,8) | 建议 | `data_db.dwd_date_shop_sku.promotion_discount_rate` | 促销折扣率，0 到 1 小数 |
| 会员折扣额 | `member_discount_amt` | decimal(18,6) | 条件必须 | 开发补充门店+SKU+日粒度字段 | 会员权益影响分析使用 |
| 会员折扣率 | `member_discount_rate` | decimal(18,8) | 条件必须 | 开发补充门店+SKU+日粒度字段 | 会员折扣率，0 到 1 小数 |
| 时段折扣额 | `time_period_discount_amt` | decimal(18,6) | 条件必须 | `data_db.dwd_date_shop_sku.hour_discount_amt` | 算法 02 促销健康适用时必须；是总折扣额中满足时段促销的部分，缺失时促销维度降级 |
| 时段折扣率 | `time_period_discount_rate` | decimal(18,8) | 建议 | `data_db.dwd_date_shop_sku.hour_discount_rate` | 时段折扣率，0 到 1 小数 |
| 门店损耗金额 | `loss_amt` | decimal(18,6) | 条件必须 | `data_db.dwd_date_shop_sku.lost_amt` | 损耗健康和风险线适用时必须；成本口径，缺失时损耗维度降级 |
| 损耗率 | `loss_rate` | decimal(18,8) | 建议 | `data_db.dwd_date_shop_sku.lost_rate` | 损耗率，0 到 1 小数 |
| 平均售价 | `avg_sale_price` | decimal(18,6) | 建议 | `sales_amt / sales_qty` 或源表成交均价 | 价格带分析使用 |
| 19 点前平均售价 | `pre19_avg_sale_price` | decimal(18,6) | 建议 | `pre19_sales_amt / pre19_sales_qty` 或源表时段均价 | 19 点前价格接受度 |
| 数据更新时间 | `data_update_time` | datetime | 必须 | 开发补充 `update_time`、`load_time`、`etl_time` 或分区日期 | 数据同步或更新时间 |

## 2. 数量字段使用规则

```text
计件商品：
优先使用 销售数量、19点前销售数量、门店进货数量、门店订购数量（订购单位）

称重商品：
优先使用 销售重量、19点前销售重量、门店进货重量、门店订购数量（重量口径）
```

注意：

```text
1. 订购数量两个口径都需要保留，不能只保留一个。
2. 原单位数量用于对账、订购覆盖和计件商品分析。
3. 重量口径数量用于称重商品分析。
4. 公斤和件数不能直接相加，也不能混在同一个售罄率分母里。
5. 门店品类等级的订购健康主要使用实际进货/实际验收口径计算售罄率，不使用订购数量直接替代实际进货量。
```

## 3. 缺失和降级写法

```text
1. 主键字段 `business_date`、`store_id`、`sku_id` 不能为空。
2. 金额、数量和比例字段缺失时保留空值，不写 0；0 只表示真实业务值为 0。
3. 称重商品必须优先使用重量字段；重量字段缺失时，不得用件数直接替代重量。
4. 计件商品必须优先使用数量字段；数量字段缺失时，不得用重量直接替代件数。
5. 当前 Doris 只覆盖当日动销 SKU 时，如算法需要覆盖零销售但可售/可订 SKU，必须结合 `mart_store_sku_daily_sale_order_status` 补齐。
```

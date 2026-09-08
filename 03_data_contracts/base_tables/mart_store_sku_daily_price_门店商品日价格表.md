# 门店商品日价格表

目标表建议名：`mart_store_sku_daily_price`

表用途：提供门店商品每日价格、采购、出库、到店、售价和成交价信息，用于价格带、毛利健康和商品机会评分。

一行代表：一个营业日期 + 一个门店 + 一个销售商品 + 一个验收商品。

主键：`business_date + store_id + sku_id + receipt_sku_id`。

关联要求：门店编码对齐小票表 `store_id`，销售商品编码对齐小票表 `article_id`。

口径要求：

1. 出库到店成本必须取含税口径，字段名统一为“出库到店成本含税”。
2. 出库到店金额必须取含税口径，字段名统一为“出库到店金额含税”。
3. 不要取“出库到店成本（不含税）”和“出库到店金额（不含税）”。
4. 销售商品编码必须能和小票商品明细表里的 `article_id` 对齐。
5. 门店编码必须能和小票商品明细表里的 `store_id` 对齐。
6. 验收商品编码和销售商品编码都要保留，不能只留一个。
7. 日期优先使用营业日期。

## 1. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 日期 | `business_date` | date | 必须 | 价格系统、验收系统或经营日表 | 门店经营日期，优先取营业日期 |
| 门店编码 | `store_id` | varchar(64) | 必须 | 价格系统、验收系统或 `dim_store.store_id` | 必须和小票表 `store_id` 对齐 |
| 门店名称 | `store_name` | varchar(128) | 建议 | `dim_store.store_name` 或价格系统 | 门店名称 |
| 仓编码 | `warehouse_id` | varchar(64) | 必须 | 价格系统、仓配系统或验收系统 | 门店对应供货仓编码 |
| 仓名称 | `warehouse_name` | varchar(128) | 建议 | 价格系统、仓配系统或验收系统 | 门店对应供货仓名称 |
| 销售商品编码 | `sku_id` | varchar(64) | 必须 | 价格系统或经营日表 | 门店实际销售商品编码，必须和小票表 `article_id` 对齐 |
| 销售商品名称 | `sku_name` | varchar(256) | 建议 | `dim_sku.sku_name` 或价格系统 | 门店实际销售商品名称 |
| 验收商品编码 | `receipt_sku_id` | varchar(64) | 必须 | 验收、进货或仓配系统 | 门店验收/进货商品编码 |
| 验收商品名称 | `receipt_sku_name` | varchar(256) | 建议 | 验收、进货或仓配系统 | 门店验收/进货商品名称 |
| 销售单位 | `sale_unit` | varchar(32) | 必须 | `dim_sku.sale_unit` 或价格系统 | 销售商品单位 |
| 验收单位 | `receipt_unit` | varchar(32) | 必须 | 验收、进货或仓配系统 | 验收商品单位 |
| 价格策略名称 | `price_strategy_name` | varchar(256) | 建议 | 价格系统 | 当前使用的价格策略 |
| 价格等级 | `price_level` | varchar(64) | 建议 | 价格系统 | 门店价格等级，例如 A 价、B 价、C 价、D 价 |
| 价格带 | `price_band` | varchar(64) | 建议 | 价格系统或本表加工 | 商品或门店对应价格带 |
| 当天采购价（出库价计算使用） | `daily_purchase_price` | decimal(18,6) | 必须 | 采购价或出库价计算来源 | 用来计算当天出库价的采购成本价 |
| 采购结算价 | `purchase_settlement_price` | decimal(18,6) | 建议 | 采购结算系统 | 与供应商结算使用的采购价 |
| 当天出库价 | `daily_outbound_price` | decimal(18,6) | 必须 | 出库价格系统 | 当天仓到门店的出库单价 |
| 出库价格 | `outbound_price` | decimal(18,6) | 必须 | 出库价格系统 | 全链路经营口径的出库价格 |
| 到店价 | `arrival_price` | decimal(18,6) | 必须 | 出库、验收或价格系统 | 商品到门店后的价格口径 |
| 销售原价 | `original_sale_price` | decimal(18,6) | 必须 | 价格系统 | 门店销售原价/标价，不得用成交均价替代 |
| 销售条码销售价 | `barcode_sale_price` | decimal(18,6) | 建议 | 价格系统 | 销售商品编码对应的销售价 |
| 商品平均售价 | `avg_sale_price` | decimal(18,6) | 建议 | 经营日表或 `sales_amt / sales_qty` | 实际成交均价 |
| 19 点前平均售价 | `pre19_avg_sale_price` | decimal(18,6) | 建议 | 经营日表或时段加工 | 19 点前销售均价 |
| 19 点后售价 | `post19_sale_price` | decimal(18,6) | 建议 | 价格系统、经营日表或时段加工 | 19 点后销售价或晚间折扣后售价 |
| 出库到店成本含税 | `outbound_arrival_cost_tax_included` | decimal(18,6) | 必须 | 出库、验收或成本系统 | 含税口径的出库到店成本 |
| 出库到店金额含税 | `outbound_arrival_amt_tax_included` | decimal(18,6) | 必须 | 出库、验收或成本系统 | 含税口径的出库到店金额 |
| 门店进货金额 | `receipt_amt` | decimal(18,6) | 建议 | 验收、进货或经营日表 | 门店验收/进货金额 |
| 销售金额 | `sales_amt` | decimal(18,6) | 建议 | 经营日表 | 实际销售金额 |
| 原价销售金额 | `original_sales_amt` | decimal(18,6) | 建议 | 价格系统或经营日表 | 按销售原价计算的销售金额 |
| 总折扣额 | `discount_amt` | decimal(18,6) | 建议 | 经营日表 | 促销、会员、时段等折扣合计 |
| 数据更新时间 | `data_update_time` | datetime | 必须 | 价格系统、验收系统、`update_time`、`load_time` 或 `etl_time` | 数据同步或更新日期时间 |

## 2. 缺失和降级写法

```text
1. 主键字段 `business_date`、`store_id`、`sku_id`、`receipt_sku_id` 不能为空。
2. 价格、成本、金额字段缺失时保留空值，不写 0；0 只表示真实业务价格或金额为 0。
3. `original_sale_price` 是标价/原价，不能用 `avg_sale_price` 或 `sales_amt / sales_qty` 直接替代。
4. `outbound_arrival_cost_tax_included` 和 `outbound_arrival_amt_tax_included` 必须使用含税口径；不含税字段不得落入这两个字段。
5. 验收商品编码和销售商品编码都要保留；如存在一对多或多对一映射，开发需在交付反馈中说明映射规则。
```

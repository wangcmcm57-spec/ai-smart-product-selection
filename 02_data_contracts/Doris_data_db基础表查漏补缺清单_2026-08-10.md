# Doris `data_db` 基础表查漏补缺清单

生成日期：2026-08-10

当前定位：这是给数据开发补齐基础数据字段用的当前工作清单，不是历史归档，也不是替代表合同的字段合同。

本文给数据开发使用，目标是说明：本地数据合同目录中 6 张基础表需要哪些字段，当前 Doris `data_db` 现有表能提供什么，还缺什么。

使用方式：

```text
1. 字段定义、表粒度、主键以 base_tables/ 下的正式数据合同为准。
2. 本清单用于开发判断现有 Doris `data_db` 能覆盖哪些字段、哪些字段还需要补源表或补映射。
3. 开发完成补数后，应回填实际来源表、字段名、主键唯一性、调度周期和缺失原因。
```

## 1. 检查范围

本次只检查以下本地合同文件：

```text
/Users/saihanhabuer/Documents/ai-selection-agent/02_data_contracts/base_tables/dim_store_门店基础表.md
/Users/saihanhabuer/Documents/ai-selection-agent/02_data_contracts/base_tables/dim_sku_商品基础表.md
/Users/saihanhabuer/Documents/ai-selection-agent/02_data_contracts/base_tables/mart_sku_margin_loss_毛利损耗表.md
/Users/saihanhabuer/Documents/ai-selection-agent/02_data_contracts/base_tables/mart_store_sku_daily_price_门店商品日价格表.md
/Users/saihanhabuer/Documents/ai-selection-agent/02_data_contracts/base_tables/mart_store_sku_daily_sale_order_status_门店商品每日可订可售表.md
/Users/saihanhabuer/Documents/ai-selection-agent/02_data_contracts/base_tables/dim_product_status_商品状态表.md
```

不包含：

```text
dim_city_algorithm_region_城市算法区域映射表.md
external_data/ 外部竞品数据合同
```

本次核对 Doris 库：

```text
Host: 10.111.105.243
Port: 9030
Database: data_db
```

## 2. Doris 当前表和注释情况

`data_db` 当前共有 11 张表 / 视图，936 个字段。

| Doris 表 | 表类型 | 表注释 | 字段注释情况 |
|---|---|---|---|
| `dim_shop` | BASE TABLE | 门店信息维度表 | 110/110 有字段注释 |
| `dim_shop_cbd` | BASE TABLE | 门店商圈宽表 | 94/94 有字段注释 |
| `dim_sku` | BASE TABLE | 商品基本信息表 | 106/106 有字段注释 |
| `dwd_date_shop` | BASE TABLE | 门店日粒度指标宽表 | 235/235 有字段注释 |
| `dwd_date_shop_sku` | BASE TABLE | 门店商品日粒度指标宽表（当日动销 SKU） | 72/72 有字段注释 |
| `dwd_date_shop_sku_monthly_backup_20260728` | BASE TABLE | 门店商品日粒度指标宽表（当日动销 SKU） | 42/42 有字段注释 |
| `dwd_date_shop_sku_p20260630_backup_20260728` | BASE TABLE | 门店商品日粒度指标宽表（当日动销 SKU） | 42/42 有字段注释 |
| `dwd_date_shop_sku_pre_full_switch_20260729` | BASE TABLE | 门店商品日粒度指标宽表（当日动销 SKU） | 42/42 有字段注释 |
| `dwd_date_shop_sku_qdm_brand` | BASE TABLE | QDM品牌指定SKU门店商品日指标表 | 54/54 有字段注释 |
| `dwd_date_shop_sku_qdm_brand_static_backup_20260805234833` | BASE TABLE | QDM品牌指定SKU门店商品日指标表（2026年6月） | 53/53 有字段注释 |
| `dwd_date_shop_sku_qdm_brand_view` | VIEW | 空 | 0/86 有字段注释 |

说明：

```text
合同表名是项目侧目标表名，Doris 表名不同是正常情况。
本清单判断是否满足，按字段、粒度和业务口径判断，不按表名是否一致判断。
```

## 3. 总体结论

| 合同目标表 | 当前覆盖结论 | 可用 Doris 来源 | 开发需要补充的核心内容 |
|---|---|---|---|
| `dim_store` 门店基础表 | 基本可满足 | `dim_shop` | 补充或确认 `sp_store_status` 状态码含义；`数据更新时间` V1 可用 `dt` 快照日期 |
| `dim_sku` 商品基础表 | 基本可满足 | `dim_sku` | 缺直接的“是否标品”“是否自加工商品”，需提供字段或映射规则 |
| `mart_sku_margin_loss` 毛利损耗表 | 部分满足 | `dwd_date_shop_sku` / `dwd_date_shop_sku_qdm_brand_view` / 必要时 join 维表 | 缺门店+SKU+日粒度的销售重量、进货重量、订购重量、原价销售额、会员来客、会员折扣、更新时间 |
| `mart_store_sku_daily_price` 门店商品日价格表 | 不满足 | 当前无完整来源 | 缺验收商品编码、仓、采购价、出库价、到店价、销售原价、价格等级、价格带等价格主字段 |
| `mart_store_sku_daily_sale_order_status` 门店商品每日可订可售表 | 不满足 | 当前无完整来源 | 缺订购商品编码、是否可售、是否可订、更新时间 |
| `dim_product_status` 商品状态表 | 不满足 | SAP POP 平台待接入 Doris | 缺 SAP POP 平台中区域 + 商品编码 + 商品名称 + 商品状态 A/O/S/D/B 的稳定接入 |

开发优先级建议：

| 优先级 | 需要处理的表 | 原因 |
|---|---|---|
| P0 | `mart_store_sku_daily_sale_order_status` | 没有可售 / 可订状态，算法无法判断“没销量”是消费者不买还是商品不可售不可订 |
| P0 | `mart_store_sku_daily_price` | 价格带、毛利健康、机会评分依赖采购 / 出库 / 到店 / 售价 / 验收 SKU |
| P0 | `dim_product_status` | 没有商品状态，算法无法区分全年品、试卖品、季节品、淘汰品和备选品 |
| P1 | `mart_sku_margin_loss` 缺口字段 | 现有经营指标能覆盖一部分，但重量、会员、原价、更新时间字段不完整 |
| P2 | `dim_sku` 标品 / 自加工映射 | 可先用候选字段派生，但需要数据字典确认 |
| P2 | `dim_store` 状态码映射 | `sp_store_status` 可用，但需要明确状态码中文含义和是否营业规则 |

## 4. `dim_store` 门店基础表

合同粒度：

```text
一行一个门店
主键：门店编码
```

当前建议来源：

```text
data_db.dim_shop
```

### 4.1 可用字段映射

| 合同字段 | Doris 字段 | 说明 |
|---|---|---|
| 门店编码 | `dim_shop.sp_store_id` | 中台门店编码，需作为和小票 `store_id` 对齐的门店编码 |
| 门店名称 | `dim_shop.sp_store_name` | 门店名称 |
| 城市 | `dim_shop.city_description` | 城市名称 |
| 区域 | `dim_shop.sap_area_name` 或 `dim_shop.area_description` | 建议数据开发选定一个正式业务区域口径 |
| 管理区域 | `dim_shop.manage_area_name` | 管理区域名称 |
| 大区 | `dim_shop.sap_area2_name` 或 `dim_shop.area2_name` | 建议数据开发选定一个正式大区口径 |
| 门店类型 | `dim_shop.store_type_name` / `dim_shop.sp_type` | `store_type_name` 是名称，`sp_type` 是编码，注释为 20加盟 / 10直营 |
| 开业日期 | `dim_shop.sp_origin_start_date` | 当前字段类型为 varchar，落目标表时建议转 date |
| 督导 | `dim_shop.group_manager` | 督导姓名 |
| 主管 | `dim_shop.zone_manager` | 运营主管 |
| 门店状态 | `dim_shop.sp_store_status` | 用户已确认可用该字段表示门店状态 |
| 是否营业 | 由 `dim_shop.sp_store_status` 派生 | 需要数据开发提供状态码到是否营业 1/0 的映射 |
| 数据更新时间 | `dim_shop.dt` | V1 可作为快照日期使用 |

### 4.2 需要开发补充 / 反馈

#### 4.2.1 `sp_store_status` 状态码含义和是否营业映射

当前 `dim_shop.sp_store_status` 枚举值：

| `sp_store_status` | 当前行数 |
|---:|---:|
| 10 | 3016 |
| 20 | 36 |
| 30 | 20 |
| 50 | 262 |
| 60 | 202 |
| 99 | 2376 |

开发需要补充：

| 需要补充项 | 说明 |
|---|---|
| `sp_store_status` 每个编码的中文含义 | 例如营业中、停业、闭店、待开业等，按数据源真实字典填写 |
| 是否营业派生规则 | 哪些状态写 `is_open = 1`，哪些状态写 `is_open = 0` |

目标表建议保留：

| 中文字段 | 英文字段建议 | 口径 |
|---|---|---|
| 门店状态编码 | `store_status_code` | 来源 `dim_shop.sp_store_status` |
| 是否营业 | `is_open` | 由 `store_status_code` 派生，1 营业，0 非营业 |

#### 4.2.2 `dt` 和记录更新时间的区别

当前 `dim_shop.dt`：

```text
min(dt) = 2026-07-20
max(dt) = 2026-07-20
```

处理建议：

| 场景 | `dt` 是否够用 | 说明 |
|---|---|---|
| 只需要知道门店维表是哪天快照 | 够用 | 可把 `dt` 写入合同里的数据更新时间或快照日期 |
| 需要追查某条门店记录具体几点更新 / 哪次同步更新 | 不够 | 需要补充 `update_time` / `load_time` / `etl_time` 这类记录级更新时间 |

V1 建议：

```text
`dim_store.data_update_time` 可先使用 `dim_shop.dt`，字段注释写成“门店维表快照日期”。
如开发侧可以提供记录级更新时间，再补充 `update_time`。
```

## 5. `dim_sku` 商品基础表

合同粒度：

```text
一行一个商品 / 销售条码
主键：交易商品编码
```

当前建议来源：

```text
data_db.dim_sku
```

### 5.1 可用字段映射

| 合同字段 | Doris 字段 | 说明 |
|---|---|---|
| 交易商品编码 | `dim_sku.article_id` | 对齐小票 `article_id` |
| 商品编码 | `dim_sku.article_id` | 合同允许和交易商品编码一致时重复保留 |
| 商品名称 | `dim_sku.article_name` | 商品名称 |
| 大类编码 | `dim_sku.category_level1_id` | 大类编码 |
| 大类名称 | `dim_sku.category_level1_description` | 大类名称 |
| 中类编码 | `dim_sku.category_level2_id` | 中类编码 |
| 中类名称 | `dim_sku.category_level2_description` | 中类名称 |
| 小类编码 | `dim_sku.category_level3_id` | 小类编码 |
| 小类名称 | `dim_sku.category_level3_description` | 小类名称 |
| SPU编码 | `dim_sku.spu_id` | SPU 编码 |
| SPU名称 | `dim_sku.spu_name` | SPU 名称 |
| 规格 | `dim_sku.norms` | 规格 |
| 单位 | `dim_sku.sale_unit` | 销售单位 |
| 单位重量 | `dim_sku.unit_weight` | 单位重量 |
| 品牌 | `dim_sku.brand` | 品牌 |
| 产地 | `dim_sku.product_address` | 产地 |
| 存储条件 | `dim_sku.sp_info_name` / `dim_sku.sp_info` | 存储条件文本 / 编码 |
| 温层 | `dim_sku.temperature_layer_name` | 温层名称 |
| 保质天数 | `dim_sku.abi_quality_days` | 保质天数 |
| 数据更新时间 | `dim_sku.update_time` | 当前最大值为 `2026-08-06 00:52:00` |

### 5.2 需要开发补充 / 反馈

#### 5.2.1 是否标品

当前 Doris 全库没有直接命中以下字段或注释：

```text
是否标品
标品
standard_product
```

候选字段：

| 候选字段 | Doris 注释 | 是否可直接等同“是否标品” |
|---|---|---|
| `dim_sku.weight_flag` | 称重标识 | 不能直接等同，只能辅助判断称重 / 计件 |
| `dim_sku.package_attribute` / `package_attribute_name` | 包装属性 | 可能辅助判断，但需数据字典 |
| `dim_sku.type` / `type_name` | 商品属性 / 商品区分名称 | 可能辅助判断，但需数据字典 |

开发需要补充二选一：

```text
方案 A：直接提供 `is_standard_product` 字段，1 是标品，0 非标品。
方案 B：提供由现有字段派生“是否标品”的规则表或映射口径。
```

#### 5.2.2 是否自加工商品

当前 Doris 全库没有直接命中：

```text
是否自加工商品
自加工
```

候选字段：

| 候选字段 | Doris 注释 | 需要确认点 |
|---|---|---|
| `dim_sku.commodity_attribute` | 商品属性：01 正常商品，02 W商品，03 大妈工坊商品 | “大妈工坊商品”是否等同自加工商品 |
| `dim_sku.commodity_attribute_name` | 商品属性名称 | 需要看字段实际枚举 |
| `dim_sku.logistics_process_tag` | 是否物流加工 | 物流加工是否等同自加工，通常不能直接等同 |

开发需要补充：

```text
1. 如果系统有正式“是否自加工商品”字段，请补入目标 `dim_sku`。
2. 如果没有，请提供“商品属性 / 大妈工坊 / 物流加工”到是否自加工的映射规则。
```

## 6. `mart_sku_margin_loss` 毛利损耗表

合同粒度：

```text
一行一个营业日期 + 门店 + 商品
主键：营业日期 + 门店编码 + 交易商品编码
```

当前主要可用来源：

```text
data_db.dwd_date_shop_sku
data_db.dwd_date_shop_sku_qdm_brand_view
data_db.dim_shop
data_db.dim_sku
```

注意：

```text
`dwd_date_shop_sku` 表注释为“门店商品日粒度指标宽表（当日动销 SKU）”。
如果目标表需要覆盖“无销量但可售 / 可订”的门店 SKU，不能只依赖该表，还必须结合可售可订状态表。
```

### 6.1 已能覆盖的主要字段

| 合同字段 | Doris 字段 | 说明 |
|---|---|---|
| 营业日期 | `dwd_date_shop_sku.dt` | 可用 |
| 门店编码 | `dwd_date_shop_sku.shop_id` | 可用 |
| 门店名称 | `dwd_date_shop_sku.shop_name` | 可用 |
| 城市 | `dwd_date_shop_sku_qdm_brand_view.city_name` 或 join `dim_shop.city_description` | 可用 |
| 区域 | `dwd_date_shop_sku_qdm_brand_view.sap_area_name` 或 join `dim_shop` | 可用 |
| 管理区域 | `dwd_date_shop_sku_qdm_brand_view.manage_area_name` 或 join `dim_shop` | 可用 |
| 大区 | `dwd_date_shop_sku_qdm_brand_view.sap_area2_name` 或 join `dim_shop` | 可用 |
| 交易商品编码 | `dwd_date_shop_sku.sku_id` | 可用 |
| 商品编码 | `dwd_date_shop_sku.sku_id` | 可用 |
| 商品名称 | `dwd_date_shop_sku.sku_name` | 可用 |
| 大类名称 | `dwd_date_shop_sku.category_level1_name` | 可用 |
| 中类名称 | `dwd_date_shop_sku.category_level2_name` | 可用 |
| 小类名称 | `dwd_date_shop_sku.category_level3_name` | 可用 |
| 结算单位 | join `dim_sku.sale_unit` / `dim_sku.order_unit` | 可补充 |
| 销售额 | `dwd_date_shop_sku.sale_amt` | 可用 |
| 销售数量 | `dwd_date_shop_sku.sale_qty` | 可用 |
| 19点前销售额 | `dwd_date_shop_sku.bf19_sale_amt` | 可用 |
| 19点前销售数量 | `dwd_date_shop_sku.bf19_sale_qty` | 可用 |
| 19点前销售重量 | `dwd_date_shop_sku.bf19_sale_weight` | 可用 |
| 19点前客数 | `dwd_date_shop_sku.bf19_cust_num` | 可用 |
| 总客数 | `dwd_date_shop_sku.cust_num` | 可用 |
| 门店进货金额 | `dwd_date_shop_sku.receive_amt` | 可用 |
| 门店进货数量 | `dwd_date_shop_sku.receive_qty` | 可用 |
| 门店订购额 | `dwd_date_shop_sku.store_order_amt` | 可用 |
| 门店订购数量（订购单位） | `dwd_date_shop_sku.store_order_qty` | 可用 |
| 供应链毛利额 | `dwd_date_shop_sku.scm_store_profit_amt` / `scm_store_profit_amt_notax` | 有含税 / 不含税两种，目标表需选定口径 |
| 门店毛利额 | `dwd_date_shop_sku.profit_amt` | 可用 |
| 全链路毛利额 | `dwd_date_shop_sku.full_link_store_profit_amt` | 可用 |
| 全链路毛利率 | `dwd_date_shop_sku.full_link_store_profit_rate` | 可用 |
| 门店毛利率 | `dwd_date_shop_sku.profit_rate` | 可用 |
| 总折扣额 | `dwd_date_shop_sku.discount_amt` | 可用 |
| 折扣率 | `dwd_date_shop_sku.discount_rate` | 可用 |
| 促销折扣额 | `dwd_date_shop_sku.promotion_discount_amt` | 可用 |
| 促销折扣率 | `dwd_date_shop_sku.promotion_discount_rate` | 可用 |
| 时段折扣额 | `dwd_date_shop_sku.hour_discount_amt` | 可用 |
| 时段折扣率 | `dwd_date_shop_sku.hour_discount_rate` | 可用 |
| 门店损耗金额 | `dwd_date_shop_sku.lost_amt` | 可用 |
| 损耗率 | `dwd_date_shop_sku.lost_rate` | 可用 |
| 平均售价 | `sale_amt / sale_qty` | 可派生 |
| 19点前平均售价 | `bf19_sale_amt / bf19_sale_qty` | 可派生 |

### 6.2 缺口字段清单

以下字段在 `data_db` 当前门店+SKU+日粒度表中未看到，或只在门店日粒度表 `dwd_date_shop` 中存在，不能直接满足合同粒度。

| 合同字段 | 当前 Doris 情况 | 为什么不能直接满足 | 开发需要补充 |
|---|---|---|---|
| 销售重量 | `dwd_date_shop` 有 `sale_weight`，但 `dwd_date_shop_sku` 没有 | `dwd_date_shop` 是门店+日粒度，不到 SKU | 补门店+SKU+日粒度 `sale_weight` |
| 原价销售额 | `dwd_date_shop` 有 `original_price_sale_amt`，但 `dwd_date_shop_sku` 没有 | 粒度不到 SKU | 补门店+SKU+日粒度 `original_price_sale_amt` |
| 会员来客数 | `dwd_date_shop` 有 `member_cust_num`，但 `dwd_date_shop_sku` 没有 | 粒度不到 SKU | 补门店+SKU+日粒度 `member_cust_num` |
| 19点前会员来客数 | `dwd_date_shop` 有 `bf19_member_cust_num`，但 `dwd_date_shop_sku` 没有 | 粒度不到 SKU | 补门店+SKU+日粒度 `bf19_member_cust_num` |
| 门店进货重量 | `dwd_date_shop` 有 `receive_weight`，但 `dwd_date_shop_sku` 没有 | 粒度不到 SKU | 补门店+SKU+日粒度 `receive_weight` |
| 门店订购数量（重量口径） | `dwd_date_shop` 有 `store_order_weight`，但 `dwd_date_shop_sku` 没有 | 粒度不到 SKU | 补门店+SKU+日粒度 `store_order_weight` |
| 会员折扣额 | `dwd_date_shop` 有 `member_discount_amt`，但 `dwd_date_shop_sku` 没有 | 粒度不到 SKU | 补门店+SKU+日粒度 `member_discount_amt` |
| 会员折扣率 | `dwd_date_shop` 有 `member_discount_rate`，但 `dwd_date_shop_sku` 没有 | 粒度不到 SKU | 补门店+SKU+日粒度 `member_discount_rate` |
| 数据更新时间 | 经营指标表未看到 `update_time` / `load_time` / `dt` 以外的同步时间 | 无法追溯指标生成时间 | 补 `update_time` / `load_time` / `etl_time`；如只能提供分区日期，也需明确字段口径 |

### 6.3 开发补数要求

请开发补充或反馈：

```text
1. 是否能在门店+SKU+日粒度补齐销售重量、进货重量、订购重量。
2. 是否能在门店+SKU+日粒度补齐原价销售额。
3. 是否能在门店+SKU+日粒度补齐会员来客数、19点前会员来客数、会员折扣额、会员折扣率。
4. 经营指标表是否能增加记录级更新时间。
5. `dwd_date_shop_sku` 当前是“当日动销 SKU”，如目标表要覆盖零销售门店 SKU，需要和可售可订状态表结合产出。
```

## 7. `mart_store_sku_daily_price` 门店商品日价格表

合同粒度：

```text
营业日期 + 门店编码 + 销售商品编码 + 验收商品编码
```

合同关键要求：

```text
1. 销售商品编码必须对齐小票 `article_id`。
2. 验收商品编码和销售商品编码都要保留，不能只留一个。
3. 出库到店成本、出库到店金额必须取含税口径。
4. 日期优先使用营业日期。
```

### 7.1 当前能勉强提供的字段

| 合同字段 | 当前 Doris 候选 | 说明 |
|---|---|---|
| 日期 | `dwd_date_shop_sku.dt` | 有营业日期 |
| 门店编码 | `dwd_date_shop_sku.shop_id` | 有门店编码 |
| 门店名称 | `dwd_date_shop_sku.shop_name` | 有门店名称 |
| 销售商品编码 | `dwd_date_shop_sku.sku_id` | 有销售商品编码 |
| 销售商品名称 | `dwd_date_shop_sku.sku_name` | 有销售商品名称 |
| 销售单位 | join `dim_sku.sale_unit` | 可从商品基础表补 |
| 验收单位 | join `dim_sku.order_unit` | 可作为候选，但需确认是否等同验收单位 |
| 商品平均售价 | `sale_amt / sale_qty` | 可派生成交均价，不是价格主数据 |
| 19点前平均售价 | `bf19_sale_amt / bf19_sale_qty` | 可派生 |
| 19点后售价 | `af19_sale_amt / af19_sale_qty` | 可派生 19点后成交均价，不是标价 |
| 门店进货金额 | `dwd_date_shop_sku.receive_amt` | 有金额指标，但缺验收商品编码 |
| 销售金额 | `dwd_date_shop_sku.sale_amt` | 有销售金额 |
| 总折扣额 | `dwd_date_shop_sku.discount_amt` | 有折扣额 |

### 7.2 缺口字段清单

以下是价格表的核心缺口。当前 `data_db` 没有看到能满足合同粒度的字段。

| 合同字段 | 当前 Doris 情况 | 需要开发补充 |
|---|---|---|
| 仓编码 | 未看到仓编码 / 仓库编码字段 | 补门店对应供货仓编码 |
| 仓名称 | 未看到仓名称 / 仓库名称字段 | 补门店对应供货仓名称 |
| 验收商品编码 | 全库未看到“验收”相关字段 | 补验收 / 进货商品编码 |
| 验收商品名称 | 全库未看到“验收”相关字段 | 补验收 / 进货商品名称 |
| 价格策略名称 | 未看到价格策略字段 | 补价格策略名称 |
| 价格等级 | 未看到价格等级字段 | 补价格等级，例如 A价 / B价 / C价 / D价 |
| 价格带 | 未看到价格带字段 | 补价格带 |
| 当天采购价（出库价计算使用） | 未看到 SKU 日粒度采购价 | 补采购价字段 |
| 采购结算价 | 未看到采购结算价 | 补采购结算价 |
| 当天出库价 | 未看到门店+SKU+验收SKU粒度出库单价 | 补当天出库价 |
| 出库价格 | 未看到门店+SKU+验收SKU粒度出库价格 | 补出库价格 |
| 到店价 | 未看到到店价字段 | 补到店价 |
| 销售原价 | `dwd_date_shop` 有门店日粒度平均销售原价 / 原价销售额，但不是 SKU 日粒度 | 补销售 SKU 日粒度销售原价 |
| 销售条码销售价 | 未看到销售条码销售价 | 补销售条码销售价 |
| 出库到店成本含税 | `dwd_date_shop` 有门店日粒度 `out_stock_cost`，粒度不满足 | 补门店+销售SKU+验收SKU+日粒度含税成本 |
| 出库到店金额含税 | `dwd_date_shop` 有门店日粒度 `out_stock_pay_amt`，粒度不满足 | 补门店+销售SKU+验收SKU+日粒度含税金额 |
| 原价销售金额 | `dwd_date_shop` 有门店日粒度 `original_price_sale_amt`，粒度不满足 | 补门店+销售SKU+日粒度原价销售金额 |
| 数据更新时间 | 未看到价格表记录级更新时间 | 补 `update_time` / `load_time` / `etl_time` |

### 7.3 不能用现有字段直接替代的点

| 现有字段 | 不能替代什么 | 原因 |
|---|---|---|
| `dwd_date_shop.avg_out_stock_price` | 不能替代价格表出库价 | 只有门店+日粒度，不到 SKU / 验收 SKU |
| `dwd_date_shop.out_stock_cost` | 不能替代出库到店成本含税 | 只有门店+日粒度 |
| `dwd_date_shop.out_stock_pay_amt` | 不能替代出库到店金额含税 | 只有门店+日粒度 |
| `dwd_date_shop.avg_original_sale_price` | 不能替代销售商品日原价 | 只有门店+日粒度 |
| `dwd_date_shop_sku.sale_amt / sale_qty` | 不能替代销售原价 / 标价 | 这是成交均价派生值，不是标价或价格主数据 |

## 8. `mart_store_sku_daily_sale_order_status` 门店商品每日可订可售表

合同粒度：

```text
日期 + 门店编码 + 销售商品编码
```

合同字段：

```text
日期
门店编码
销售商品编码
订购商品编码
是否可售
是否可订
数据更新时间
```

### 8.1 当前能提供的字段

| 合同字段 | 当前 Doris 候选 | 说明 |
|---|---|---|
| 日期 | `dwd_date_shop_sku.dt` | 有营业日期 |
| 门店编码 | `dwd_date_shop_sku.shop_id` | 有门店编码 |
| 销售商品编码 | `dwd_date_shop_sku.sku_id` | 有销售商品编码 |

### 8.2 缺口字段清单

| 合同字段 | 当前 Doris 情况 | 为什么不能满足 | 开发需要补充 |
|---|---|---|---|
| 订购商品编码 | 未看到订购商品编码字段 | 无法对齐订购 / 进货 / 验收口径 | 补门店+销售SKU+日对应的订购商品编码 |
| 是否可售 | 全库未看到“可售”字段 | 无法判断商品当天在该门店是否可售 | 补 `is_saleable`，1 可售，0 不可售 |
| 是否可订 | 只有 `store_can_orders` / `store_can_order_num` 这类可订门店数指标 | 这是汇总指标，不是门店 SKU 日级 0/1 状态 | 补 `is_orderable`，1 可订，0 不可订 |
| 数据更新时间 | 未看到状态表记录级更新时间 | 无法追溯状态数据更新 | 补 `update_time` / `load_time` / `etl_time` |

### 8.3 不能用现有字段直接替代的点

| 现有字段 | Doris 注释 | 不能替代原因 |
|---|---|---|
| `dwd_date_shop_sku.store_can_orders` | 可订门店数（CMR原值） | 是指标 / 数量，不是某门店某 SKU 当天是否可订的 0/1 状态 |
| `dwd_date_shop.store_can_order_num` | 可订门店次数 | 是门店日汇总，不是 SKU 日状态 |
| `dwd_date_shop_sku.order_store_rate` | 门店订购渗透率 | 是聚合率，不是可订状态 |

开发需要提供一张真正的状态表：

```text
一行 = 日期 + 门店编码 + 销售商品编码
字段至少包含：
日期、门店编码、销售商品编码、订购商品编码、是否可售、是否可订、数据更新时间
```

## 9. `dim_product_status` 商品状态表

合同粒度：

```text
一行一个数据版本 + 区域 + 商品的当前商品状态
主键建议：product_status_version + region_code + sku_id
```

当前建议来源：

```text
业务已补充来源为 SAP POP 平台。当前 data_db 未看到已落入 Doris 且可直接满足 A/O/S/D/B 商品状态枚举的完整来源。
需要数据开发从 SAP POP 平台抽取或同步商品状态数据，并落到 Doris 可稳定读取的数据源。
```

### 9.1 必须提供字段

| 合同字段 | 英文字段 | 最低要求 |
|---|---|---|
| 区域编码 | `region_code` | 必须能和门店区域或算法区域口径建立映射 |
| 区域名称 | `region_name` | 业务可读的区域名称 |
| 商品编码 | `sku_id` | 必须对齐小票表 `article_id` 和商品基础表 `dim_sku.sku_id` |
| 商品名称 | `sku_name` | 必须和商品基础表商品名称可核对 |
| 商品状态编码 | `product_status_code` | 只能取 `A`、`O`、`S`、`D`、`B` |
| 状态快照日期 | `status_snapshot_date` | 必须提供，用于标识本批 SAP POP 商品状态快照 |
| 来源系统 | `source_system` | 固定写 `SAP_POP` |
| 数据更新时间 | `data_update_time` | 必须提供，支持数据追溯 |

### 9.2 商品状态枚举

| 状态编码 | 英文含义 | 中文含义 | 算法使用提示 |
|---|---|---|---|
| `A` | `annual` | 全年品 | 可作为常规在售商品基线 |
| `O` | `one_time_buy` | 试卖品 | 历史销量和停订不能直接等同常规失败 |
| `S` | `seasonal` | 季节品 | `S` 本身已代表季节品身份，本表不判断销售季内/外 |
| `D` | `discontinued` | 淘汰品 | 不应作为常规新品候选，特殊策略需单独标记 |
| `B` | `backup` | 备选品 | 作为备选货盘或替代关系判断，不等同常规主推 |

### 9.3 需要开发补充 / 反馈

| 需要补充项 | 说明 |
|---|---|
| SAP POP 商品状态接入 | 当前 Doris `data_db` 未看到可直接提供 A/O/S/D/B 的字段，需要开发说明 SAP POP 的来源表、接口或同步任务 |
| 区域口径 | 需要明确区域是大区、管理区域、城市群还是其他业务区域，并说明如何和门店基础表对齐 |
| 状态快照周期 | 需要说明 SAP POP 商品状态同步频率、快照日期口径和更新时间字段 |

## 10. 给开发的补数任务清单

### 10.1 必须补表 / 补字段

| 目标合同表 | 必补内容 | 最低要求 |
|---|---|---|
| `mart_store_sku_daily_sale_order_status` | 每日可售可订状态表 | 日期 + 门店编码 + 销售商品编码 + 订购商品编码 + 是否可售 + 是否可订 + 更新时间 |
| `mart_store_sku_daily_price` | 门店商品日价格表 | 日期 + 门店编码 + 销售商品编码 + 验收商品编码 + 仓 + 采购价 + 出库价 + 到店价 + 销售原价 + 成交价 + 价格等级 / 价格带 + 更新时间 |
| `dim_product_status` | 商品状态表 | 区域 + 商品编码 + 商品名称 + 商品状态 A/O/S/D/B + 状态快照日期 + 更新时间 |
| `mart_sku_margin_loss` | SKU 日粒度缺口经营字段 | 销售重量、进货重量、订购重量、原价销售额、会员来客、19点前会员来客、会员折扣额、会员折扣率、更新时间 |

### 10.2 需要提供字段字典 / 派生规则

| 目标表 | 规则 | 当前候选字段 |
|---|---|---|
| `dim_store` | `sp_store_status` 状态码中文含义、是否营业 1/0 派生规则 | `dim_shop.sp_store_status` |
| `dim_sku` | 是否标品派生规则，或直接补字段 | `weight_flag`、`package_attribute_name`、`type_name` |
| `dim_sku` | 是否自加工商品派生规则，或直接补字段 | `commodity_attribute`、`commodity_attribute_name`、`logistics_process_tag` |
| `dim_product_status` | SAP POP 平台中商品状态 A/O/S/D/B 的来源字段、枚举字典和区域适用口径 | 当前 Doris `data_db` 未看到可直接映射字段 |

### 10.3 可先用现有 Doris 产出的字段

| 目标表 | 可先产出内容 |
|---|---|
| `dim_store` | 门店编码、门店名称、城市、区域、管理区域、大区、门店类型、开业日期、督导、主管、门店状态、快照日期 |
| `dim_sku` | 商品编码、商品名称、类目、SPU、规格、单位、单位重量、品牌、产地、存储条件、温层、保质天数、更新时间 |
| `mart_sku_margin_loss` | 门店 SKU 日销售额、销售数量、19点前销售、客数、进货额/量、订购额/量、毛利、折扣、损耗等主要金额指标 |

## 11. 建议开发自查 SQL

### 11.1 查看门店状态码枚举

```sql
SELECT
  sp_store_status,
  COUNT(*) AS cnt
FROM data_db.dim_shop
GROUP BY sp_store_status
ORDER BY sp_store_status;
```

### 11.2 查看字段注释

```sql
SELECT
  TABLE_NAME,
  ORDINAL_POSITION,
  COLUMN_NAME,
  COLUMN_TYPE,
  COLUMN_COMMENT
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'data_db'
  AND TABLE_NAME IN (
    'dim_shop',
    'dim_sku',
    'dwd_date_shop',
    'dwd_date_shop_sku',
    'dwd_date_shop_sku_qdm_brand',
    'dwd_date_shop_sku_qdm_brand_view'
  )
ORDER BY TABLE_NAME, ORDINAL_POSITION;
```

### 11.3 检查价格表关键字段是否已补齐

```sql
SELECT
  TABLE_NAME,
  COLUMN_NAME,
  COLUMN_COMMENT
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'data_db'
  AND (
    COLUMN_NAME LIKE '%price%'
    OR COLUMN_COMMENT LIKE '%价格%'
    OR COLUMN_COMMENT LIKE '%采购价%'
    OR COLUMN_COMMENT LIKE '%出库价%'
    OR COLUMN_COMMENT LIKE '%到店价%'
    OR COLUMN_COMMENT LIKE '%价格等级%'
    OR COLUMN_COMMENT LIKE '%价格带%'
    OR COLUMN_COMMENT LIKE '%验收%'
    OR COLUMN_COMMENT LIKE '%仓%'
  )
ORDER BY TABLE_NAME, ORDINAL_POSITION;
```

### 11.4 检查可售可订状态字段是否已补齐

```sql
SELECT
  TABLE_NAME,
  COLUMN_NAME,
  COLUMN_COMMENT
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'data_db'
  AND (
    COLUMN_NAME LIKE '%saleable%'
    OR COLUMN_NAME LIKE '%orderable%'
    OR COLUMN_COMMENT LIKE '%可售%'
    OR COLUMN_COMMENT LIKE '%可订%'
  )
ORDER BY TABLE_NAME, ORDINAL_POSITION;
```

### 11.5 检查商品状态字段是否已补齐

```sql
SELECT
  TABLE_NAME,
  COLUMN_NAME,
  COLUMN_COMMENT
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'data_db'
  AND (
    COLUMN_NAME LIKE '%status%'
    OR COLUMN_NAME LIKE '%life%'
    OR COLUMN_NAME LIKE '%season%'
    OR COLUMN_NAME LIKE '%annual%'
    OR COLUMN_NAME LIKE '%discontinued%'
    OR COLUMN_COMMENT LIKE '%商品状态%'
    OR COLUMN_COMMENT LIKE '%生命周期%'
    OR COLUMN_COMMENT LIKE '%全年%'
    OR COLUMN_COMMENT LIKE '%试卖%'
    OR COLUMN_COMMENT LIKE '%季节%'
    OR COLUMN_COMMENT LIKE '%淘汰%'
    OR COLUMN_COMMENT LIKE '%备选%'
  )
ORDER BY TABLE_NAME, ORDINAL_POSITION;
```

## 12. 最终交付判断

当前 Doris `data_db` 已经具备：

```text
1. 门店维度大部分字段。
2. 商品维度大部分字段。
3. 门店 SKU 日经营指标的一部分金额、数量、毛利、折扣、损耗字段。
```

当前 Doris `data_db` 仍不具备完整合同交付能力：

```text
1. 价格表缺核心价格和验收 SKU 字段。
2. 可售可订表缺核心 0/1 状态字段。
3. 毛利损耗表缺一批门店+SKU+日粒度字段，尤其是重量、会员和原价销售额。
4. 商品状态表缺 SAP POP 平台中区域 + 商品编码 + 商品名称 + 商品状态 A/O/S/D/B 的稳定 Doris 接入。
5. 商品维表缺“是否标品”“是否自加工商品”的直接字段或明确映射。
6. 门店维表需要 `sp_store_status` 状态码含义和是否营业派生规则。
```

因此，数据开发需要先补齐以上缺口，再按合同产出项目侧目标基础表。

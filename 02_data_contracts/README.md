# 数据合同

这里存放给数据开发使用的字段合同。

当前阶段的目标是：让数据开发可以并行准备 V1 AI 新品推荐所需的数据表。每张表都需要进入 Doris，或至少形成可被 Doris 加工任务稳定读取的数据源。

## V1 必做数据表

### 已有源表

| 表 | 状态 | 说明 |
| --- | --- | --- |
| Doris 小票商品明细表 | 已有 | 作为会员画像、门店品类等级、SKU 表现等算法的核心交易事实表 |

### 需要开发准备的内部基础表

| 表合同 | 目标表建议名 | 是否 V1 必做 | 说明 |
| --- | --- | --- | --- |
| [门店基础表](base_tables/dim_store_门店基础表.md) | `dim_store` | 必做 | 提供门店名称、城市、区域、管理区域、营业状态等 |
| [商品基础表](base_tables/dim_sku_商品基础表.md) | `dim_sku` | 必做 | 提供商品名称、品类、SPU、规格、温层、保质期等 |
| [毛利损耗表](base_tables/mart_sku_margin_loss_毛利损耗表.md) | `mart_sku_margin_loss` | 必做 | 提供门店商品销售、客数、毛利、折扣、损耗等经营指标 |
| [门店商品日价格表](base_tables/mart_store_sku_daily_price_门店商品日价格表.md) | `mart_store_sku_daily_price` | 必做 | 提供采购价、出库价、到店价、销售原价、成交均价、19点前后价格等 |
| [城市算法区域映射表](base_tables/dim_city_algorithm_region_城市算法区域映射表.md) | `dim_city_algorithm_region` | 必做 | 提供城市到算法区域的映射，用于会员画像和区域参数计算 |
| [门店商品每日可订可售表](base_tables/mart_store_sku_daily_sale_order_status_门店商品每日可订可售表.md) | `mart_store_sku_daily_sale_order_status` | 必做 | 判断商品在门店是否可售、是否可订，避免算法误判“没销量”的原因 |

### 需要开发准备的外部竞品表

| 表合同 | 目标表建议名 | 是否 V1 必做 | 说明 |
| --- | --- | --- | --- |
| [久谦接口原始表](external_data/ods_jiuqian_api_raw_久谦接口原始表.md) | `ods_jiuqian_api_raw` | 必做 | 保存每次 API 返回原文，方便追溯、排错、重跑 |
| [竞品 SKU 基础表](external_data/dim_competitor_sku_竞品SKU基础表.md) | `dim_competitor_sku` | 必做 | 保存竞品商品稳定属性 |
| [竞品每日快照表](external_data/fact_competitor_sku_daily_snapshot_竞品每日快照表.md) | `fact_competitor_sku_daily_snapshot` | 必做 | 保存竞品每天变化的价格、销量、促销、评价、售罄等数据 |

## V1 暂不纳入

以下表先不作为当前开发交付范围：

- 供应商基础表
- 库存损耗明细表
- 促销优惠券明细表

## 开发交付要求

每张表请至少反馈：

1. 字段是否能提供。
2. 字段来源系统或来源表。
3. 是否能按合同粒度产出。
4. 主键是否唯一。
5. 和小票表的关联字段是否能对齐。
6. 数据更新频率。
7. 历史数据可回溯周期。
8. 当前缺失字段和替代字段。

真实数据样例不放入 Git。如需样例，请放入 `07_examples/synthetic_data/`，并确保是脱敏或人造数据。

# 外部数据合同

这里存放 V1 需要接入 Doris 的外部竞品数据合同。

当前外部数据来自久谦 API，第一版拆成 3 张表：

| 表合同 | 目标表建议名 | 用途 |
| --- | --- | --- |
| [久谦接口原始表](ods_jiuqian_api_raw_久谦接口原始表.md) | `ods_jiuqian_api_raw` | 保存每次接口返回原文，方便追溯、排错、重跑 |
| [竞品 SKU 基础表](dim_competitor_sku_竞品SKU基础表.md) | `dim_competitor_sku` | 保存竞品商品稳定属性 |
| [竞品每日快照表](fact_competitor_sku_daily_snapshot_竞品每日快照表.md) | `fact_competitor_sku_daily_snapshot` | 保存价格、销量、促销、评价、覆盖门店数等每日变化指标 |

开发需要并行确认久谦 API 是否能提供以下字段：

- 评论数
- 好评率
- 总销量
- 日销量
- 是否售罄
- 商品详情链接
- 标准规格重量

如果 API 第一版不能提供，可以字段保留为空，但需要在开发反馈中明确缺失原因。

# 竞品 SKU 基础表

目标表建议名：`dim_competitor_sku`

表用途：保存竞品商品相对稳定的基础属性，对应架构图里的外部竞品表主体。

一行代表：一个数据提供方 + 一个竞品平台 + 一个城市 + 一个竞品 SKU。

主键建议：`data_provider + competitor_platform + city_name + competitor_sku_id`。

关联要求：

| 关联对象 | 关联字段 | 要求 |
| --- | --- | --- |
| 久谦接口原始表 | 数据采集批次号 | 可追溯来源批次 |
| 竞品每日快照表 | 数据提供方 + 竞品平台 + 城市 + 竞品 SKU 编码 | 关联每日价格、销量、促销 |
| 后续内部竞品匹配表 | 竞品平台 + 城市 + 竞品 SKU 编码 | 后续用于匹配内部商品，不直接对齐小票表 |

## 1. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 数据提供方 | `data_provider` | varchar(64) | 必须 | `ods_jiuqian_api_raw.data_provider` 或采集任务配置 | 数据供应方，V1 固定为久谦 |
| 竞品平台 | `competitor_platform` | varchar(64) | 必须 | 久谦 API 返回 | 竞品所属平台，例如叮咚买菜、盒马 |
| 城市 | `city_name` | varchar(64) | 必须 | 久谦 API 返回或请求城市 | 竞品数据城市 |
| 竞品 SKU 编码 | `competitor_sku_id` | varchar(128) | 必须 | 久谦 API 返回 | 外部平台商品唯一编码 |
| 竞品商品名称 | `competitor_sku_name` | varchar(512) | 必须 | 久谦 API 返回 | 竞品商品名称 |
| 商品描述 | `product_description` | varchar(2048) | 建议 | 久谦 API 返回 | 商品描述，接口没有可为空 |
| 外部一级类目 | `competitor_category_level1_name` | varchar(128) | 建议 | 久谦 API 返回 | 外部平台一级类目 |
| 外部二级类目 | `competitor_category_level2_name` | varchar(128) | 建议 | 久谦 API 返回 | 外部平台二级类目 |
| 外部三级类目 | `competitor_category_level3_name` | varchar(128) | 建议 | 久谦 API 返回 | 外部平台三级类目，没有可为空 |
| 品牌 | `brand_name` | varchar(128) | 建议 | 久谦 API 返回 | 竞品品牌，没有可为空 |
| 规格 | `specification` | varchar(128) | 建议 | 久谦 API 返回 | 原始规格 |
| 标准规格重量 | `standard_weight_g` | decimal(18,6) | 建议 | 久谦 API 返回或规格解析 | 统一换算成克，无法解析可为空 |
| 存储方式 | `storage_condition` | varchar(64) | 建议 | 久谦 API 返回 | 冷藏、冷冻、常温等存储方式 |
| 商品渠道 | `sales_channel` | varchar(64) | 建议 | 久谦 API 返回 | 前置仓、门店、电商等渠道 |
| 自定义标签 | `custom_tags` | varchar(2048) | 建议 | 久谦 API 返回 | 外部标签，多个标签可用 JSON 数组或分隔字符串 |
| 商品图片链接 | `product_image_url` | varchar(2048) | 建议 | 久谦 API 返回 | 竞品图片链接 |
| 商品详情链接 | `product_detail_url` | varchar(2048) | 建议 | 久谦 API 返回 | 竞品商品详情页链接；API 不提供时可为空 |
| 首次采集日期 | `first_collection_date` | date | 必须 | 采集任务加工 | 第一次采集到该 SKU 的日期 |
| 最近采集日期 | `latest_collection_date` | date | 必须 | 采集任务加工 | 最近一次采集到该 SKU 的日期 |
| 数据采集批次号 | `collection_batch_id` | varchar(128) | 必须 | `ods_jiuqian_api_raw.collection_batch_id` | 来源批次 |
| 数据更新时间 | `data_update_time` | datetime | 必须 | 入库任务生成 | 入库更新时间 |

## 2. 缺失和降级写法

```text
1. 主键字段 `data_provider`、`competitor_platform`、`city_name`、`competitor_sku_id` 不能为空。
2. `competitor_sku_name` 不能为空；接口缺失商品名时，该条不能进入竞品基础表正式可用数据。
3. 类目、品牌、规格、图片、详情链接等接口未提供时可为空，但必须保留原始批次号方便追溯。
4. `standard_weight_g` 只能来自 API 字段或可解释的规格解析规则，无法解析时为空，不能按商品名猜重量。
```

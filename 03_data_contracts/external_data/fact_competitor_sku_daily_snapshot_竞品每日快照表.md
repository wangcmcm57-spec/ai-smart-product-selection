# 竞品每日快照表

目标表建议名：`fact_competitor_sku_daily_snapshot`

表用途：保存竞品每天变化的数据，比如价格、会员价、销量、促销、覆盖门店数。后续竞品趋势、价格带、销量趋势都依赖这张表。

一行代表：一个采集日期 + 一个数据提供方 + 一个竞品平台 + 一个城市 + 一个竞品 SKU。

主键建议：`collection_date + data_provider + competitor_platform + city_name + competitor_sku_id`。

关联要求：

| 关联对象 | 关联字段 | 要求 |
| --- | --- | --- |
| 竞品 SKU 基础表 | 数据提供方 + 竞品平台 + 城市 + 竞品 SKU 编码 | 补商品名称、类目、规格、图片 |
| 后续竞品趋势汇总表 | 采集日期 + 城市 + 类目 / 方向 | 作为趋势算法输入 |

## 1. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 采集日期 | `collection_date` | date | 必须 | 久谦 API 返回或采集任务日期 | 竞品数据日期 |
| 数据提供方 | `data_provider` | varchar(64) | 必须 | 久谦数据供给/导入任务的提供方登记 | 数据供应方，V1 固定为久谦 |
| 竞品平台 | `competitor_platform` | varchar(64) | 必须 | 久谦 API 返回 | 竞品平台 |
| 城市 | `city_name` | varchar(64) | 必须 | 久谦 API 返回或请求城市 | 竞品数据城市 |
| 竞品 SKU 编码 | `competitor_sku_id` | varchar(128) | 必须 | 久谦 API 返回 | 外部商品编码 |
| 竞品商品名称 | `competitor_sku_name` | varchar(512) | 必须 | 久谦 API 返回或 `dim_competitor_sku.competitor_sku_name` | 冗余保留，方便查询 |
| 当前售价 | `current_sale_price` | decimal(18,6) | 必须 | 久谦 API 返回 | 当前售卖价格 |
| 划线价 | `list_price` | decimal(18,6) | 建议 | 久谦 API 返回 | 原价 / 市场价 |
| 会员价 | `member_price` | decimal(18,6) | 建议 | 久谦 API 返回 | 会员价，没有可为空 |
| 规格 | `specification` | varchar(128) | 建议 | 久谦 API 返回 | 当天采集到的规格 |
| 标准规格重量 | `standard_weight_g` | decimal(18,6) | 建议 | 久谦 API 返回或规格解析 | 克重，方便做 500g 价格换算 |
| 折扣标签 | `discount_tags` | varchar(2048) | 建议 | 久谦 API 返回 | 促销 / 折扣标签，多个标签可用 JSON 数组或分隔字符串 |
| 限时特卖信息 | `flash_sale_info` | varchar(2048) | 建议 | 久谦 API 返回 | 限时特卖信息 |
| 月销量 | `monthly_sales_qty` | decimal(18,6) | 建议 | 久谦 API 返回 | 月销量，接口没有可为空 |
| 总销量 | `total_sales_qty` | decimal(18,6) | 建议 | 久谦 API 返回 | 总销量，接口没有可为空 |
| 日销量 | `daily_sales_qty` | decimal(18,6) | 建议 | 久谦 API 返回或快照差分 | 日销量，接口没有可为空 |
| 评论数 | `review_count` | bigint | 建议 | 久谦 API 返回 | 评论数，接口没有可为空 |
| 好评率 | `positive_review_rate` | decimal(18,8) | 建议 | 久谦 API 返回 | 好评率，统一落 0 到 1 小数 |
| 是否售罄 | `is_sold_out` | tinyint | 建议 | 久谦 API 返回 | `1` 售罄，`0` 未售罄，接口没有可为空 |
| 覆盖门店数 | `coverage_store_count` | bigint | 建议 | 久谦 API 返回 | 覆盖门店 / 点位数量 |
| 原始记录数 | `raw_record_count` | bigint | 必须 | 采集任务聚合统计 | 原始采集记录数，用于聚合校验 |
| 商品详情链接 | `product_detail_url` | varchar(2048) | 建议 | 久谦 API 返回 | 竞品商品详情页链接，接口没有可为空 |
| 数据采集批次号 | `collection_batch_id` | varchar(128) | 必须 | 久谦数据供给/导入任务保留的实际批次标识 | 供给/导入批次，不是已留存API原文的证明 |
| 数据更新时间 | `data_update_time` | datetime | 必须 | 入库任务生成 | 入库更新时间 |

## 2. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `is_sold_out` | 是否售罄 | `1` | 售罄 | 久谦 API 明确返回商品售罄 |
| `is_sold_out` | 是否售罄 | `0` | 未售罄 | 久谦 API 明确返回商品未售罄 |
| `is_sold_out` | 是否售罄 | 空 | 暂无状态 | 久谦 API 未提供售罄字段或字段不可稳定解析 |

久谦 API 需要确认能否提供以下字段：

- 评论数
- 好评率
- 总销量
- 日销量
- 是否售罄
- 商品详情链接
- 标准规格重量

如果 API 提供，就第一版一起接；如果不提供，可以先为空，但开发需要反馈缺失原因。

## 3. 缺失和降级写法

```text
1. 主键字段 `collection_date`、`data_provider`、`competitor_platform`、`city_name`、`competitor_sku_id` 不能为空。
2. `current_sale_price` 不能为空；没有价格的竞品记录不能进入正式价格快照。
3. 月销量、总销量、日销量、评论数、好评率、是否售罄、商品详情链接和标准规格重量，API 不提供时可以为空，但开发需要反馈缺失原因。
4. `positive_review_rate` 必须落为 0 到 1 小数，例如 96% 写 `0.96`。
5. `standard_weight_g` 无法解析时为空；算法做规格价格换算时必须识别缺失状态。
```

## 久谦两表供给与输入追溯

一期直接读取`dim_competitor_sku`和`fact_competitor_sku_daily_snapshot`。不依赖久谦API原始响应表，不要求补建原始响应表。字段来源中的“久谦API返回”表示供给方字段口径，不表示本仓库已保存API响应或能还原供应商最初采集过程。

`data_provider`和`collection_batch_id`来自实际数据供给/导入任务；字段仍按本合同验收，缺失时不能伪造接口请求或采集批次。两表按`data_provider + competitor_platform + city_name + competitor_sku_id`关联，日快照另以`collection_date`区分；禁止只用批次号关联或省略提供方。两表批次号各自留存，不以批次相等替代实体关联。截止日有效性须有日期/供给规则依据，不能用后续更新的属性回填历史输入。

算法07在`external_trend_run.input_assets_snapshot_json`登记实际读取列、完整业务键、读取范围、不可变`snapshot_reference`、内容`content_hash`和记录数，并保存可定位到冻结行的证据索引。`source_audit_json`保存实际供给批次、更新时间及可取得的供给依据；未知的上游API细节保持缺失，不猜补。输入行可定位且可冻结时，缺少供应商最初API原文不单独阻断07；行键冲突、无法定位或无法冻结时，只阻断依赖该输入的输出。

同批次重跑读取父运行冻结行，不读取当前可变维表重建历史。已有历史不可变输入包继续保留；原包不可取得时明确阻断该历史重跑，不以当前两表内容冒充原输入。公开外部源的原始响应快照合同独立保留。

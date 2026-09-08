# 商品状态表

目标表建议名：`dim_product_status`

表用途：按区域和商品沉淀 SAP POP 平台中的当前商品经营状态，供算法识别全年品、试卖品、季节品、淘汰品和备选品，避免把不同状态商品的销量、停订、候选机会和历史失败混在一起判断。

口径调整：历史草稿中的 `dim_product_season_window` 不再作为独立规则配置表维护。当前 P0 商品状态改为基础数据表，由数据开发从 SAP POP 平台按区域、商品名称、商品编码和商品状态提供。`product_status_code = S` 已代表该商品是季节品；本表同步维护该商品的计划上架开始日期和计划上架结束日期，作为后续算法识别季节窗口的基础，但不维护销售季名称或是否每年重复。

来源：SAP POP 平台。由数据开发从 SAP POP 平台抽取或同步到 Doris 可稳定读取的数据源，再落到目标基础表。

一行代表：一个数据版本 + 一个区域 + 一个商品的当前商品状态。

主键建议：`product_status_version + region_code + sku_id`。

关联要求：商品编码 `sku_id` 必须能和 Doris 小票商品明细表里的 `article_id` 对齐，也必须能和商品基础表 `dim_sku.sku_id` 对齐。区域字段需能和门店基础表或城市算法区域口径建立稳定映射。

## 1. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 商品状态数据版本 | `product_status_version` | varchar(64) | 必须 | 数据开发生成 | 例如 `PRODUCT_STATUS_2026_V1`，用于追溯本批状态数据 |
| 区域编码 | `region_code` | varchar(64) | 必须 | SAP POP 平台或门店区域映射 | 商品状态适用区域编码 |
| 区域名称 | `region_name` | varchar(128) | 必须 | SAP POP 平台或门店区域映射 | 商品状态适用区域名称 |
| 商品编码 | `sku_id` | varchar(64) | 必须 | SAP POP 平台或 `dim_sku.sku_id` | 商品销售编码，必须对齐小票表 `article_id` |
| 商品名称 | `sku_name` | varchar(256) | 必须 | SAP POP 平台或 `dim_sku.sku_name` | 商品名称，用于业务核对 |
| 商品状态编码 | `product_status_code` | varchar(8) | 必须 | SAP POP 平台 | `A`、`O`、`S`、`D`、`B` |
| 商品状态英文名 | `product_status_en_name` | varchar(64) | 必须 | 状态枚举映射 | `annual`、`one_time_buy`、`seasonal`、`discontinued`、`backup` |
| 商品状态中文名 | `product_status_name` | varchar(64) | 必须 | 状态枚举映射 | 全年品、试卖品、季节品、淘汰品、备选品 |
| 计划上架开始日期 | `season_start_date` | date | 条件必须 | SAP POP 平台 | 仅 `product_status_code = S` 的商品填写，表示计划上架开始日期 |
| 计划上架结束日期 | `season_end_date` | date | 条件必须 | SAP POP 平台 | 仅 `product_status_code = S` 的商品填写，表示计划上架结束日期 |
| 状态快照日期 | `status_snapshot_date` | date | 必须 | SAP POP 平台同步快照或入库任务生成 | 本批商品状态对应的快照日期 |
| 来源系统 | `source_system` | varchar(128) | 必须 | 数据开发补充 | 固定填写 `SAP_POP` |
| 来源表 | `source_table` | varchar(128) | 建议 | 数据开发补充 | SAP POP 平台对应来源表、接口或同步任务名称 |
| 数据更新时间 | `data_update_time` | datetime | 必须 | 入库任务生成 | 数据同步或更新时间 |
| 备注 | `remark` | varchar(1024) | 建议 | SAP POP 平台或项目维护 | 特殊状态、区域例外或人工说明 |

## 2. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `product_status_code` | 商品状态编码 | `A` | 全年品 | 商品在该区域常年经营，不属于试卖、季节、淘汰或备选 |
| `product_status_code` | 商品状态编码 | `O` | 试卖品 | `one_time_buy`，商品在该区域为一次性/试卖性质 |
| `product_status_code` | 商品状态编码 | `S` | 季节品 | `seasonal`，商品在该区域属于季节品 |
| `product_status_code` | 商品状态编码 | `D` | 淘汰品 | `discontinued`，商品在该区域已淘汰或停止经营 |
| `product_status_code` | 商品状态编码 | `B` | 备选品 | `backup`，商品在该区域作为备选或后备商品 |
| `source_system` | 来源系统 | `SAP_POP` | SAP POP 平台 | 商品状态从 SAP POP 平台抽取或同步 |
| `season_start_date` | 计划上架开始日期 | 必填 | 仅 `S` 商品 | 季节品计划上架开始时间 |
| `season_end_date` | 计划上架结束日期 | 必填 | 仅 `S` 商品 | 季节品计划上架结束时间 |

## 3. 算法使用

| 算法 | 使用方式 |
|---|---|
| 算法 04 | 判断历史 SKU 表现时区分全年品、季节品、试卖品、淘汰品和备选品 |
| 算法 06 | 购物篮关联计算时，按 `S` 状态和计划上架开始/结束日期识别季节窗口；本表提供季节品基础窗口 |
| 算法 08 | 候选标准化时透传商品状态和季节窗口，避免把淘汰品、试卖品和备选品误当常规候选 |
| 算法 09 | 历史失败和风险门禁时，区分正常季节结束、淘汰、试卖结束和真实经营失败 |

## 4. 缺失和降级写法

```text
1. `region_code`、`region_name`、`sku_id`、`sku_name`、`product_status_code`、`status_snapshot_date`、`source_system`、`data_update_time` 不能为空。
2. `product_status_code` 只能取 `A`、`O`、`S`、`D`、`B`，不得写中文、英文全称或其他临时枚举。
3. `source_system` 固定写 `SAP_POP`；如果开发落地时使用中间同步表，需在 `source_table` 说明真实同步表、接口或任务名称。
4. 同一数据版本、同一区域、同一商品只能有一条当前状态记录。
5. `product_status_code = S` 的商品必须填写 `season_start_date` 和 `season_end_date`；非 `S` 商品可为空。
6. 算法不得把商品状态表里的计划上架时间解释为每年重复的销售季规则；如后续业务需要“每年重复”或更细季节窗口口径，应另行新增规则资产。
7. `product_status_code = D` 的商品不得作为常规新品开发候选；如作为替代、复活或特殊策略候选，必须由后续算法单独标记原因。
8. 商品状态缺失时，算法不得自行按商品名称或销量季节性猜状态，应写状态缺失或未知。
```

# 门店基础表

目标表建议名：`dim_store`

表用途：提供门店维度基础信息，用于城市、区域、门店状态筛选，以及所有门店粒度算法结果的关联。

一行代表：一个门店。

主键：`store_id`。

关联要求：门店编码必须能和 Doris 小票商品明细表里的 `store_id` 对齐。

## 1. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 门店编码 | `store_id` | varchar(64) | 必须 | `data_db.dim_shop.sp_store_id` | 门店唯一编码，必须和小票表 `store_id` 对齐 |
| 门店名称 | `store_name` | varchar(128) | 必须 | `data_db.dim_shop.sp_store_name` | 门店名称，用于展示和验收 |
| 城市 | `city_name` | varchar(64) | 必须 | `data_db.dim_shop.city_description` | 门店所在城市，需能对齐城市算法区域映射表 |
| 区域 | `area_name` | varchar(128) | 建议 | `data_db.dim_shop.sap_area_name` 或 `data_db.dim_shop.area_description` | 业务区域口径，开发需选定一个稳定来源 |
| 管理区域 | `manage_area_name` | varchar(128) | 建议 | `data_db.dim_shop.manage_area_name` | 业务管理区域 |
| 大区 | `region_name` | varchar(128) | 建议 | `data_db.dim_shop.sap_area2_name` 或 `data_db.dim_shop.area2_name` | 上级大区，开发需选定一个稳定来源 |
| 门店类型 | `store_type` | varchar(64) | 建议 | `data_db.dim_shop.store_type_name` 或 `data_db.dim_shop.sp_type` | 门店经营类型，例如直营、加盟 |
| 开业日期 | `open_date` | date | 建议 | `data_db.dim_shop.sp_origin_start_date` | 门店开业日期；源字段为字符串时落表需转为日期 |
| 督导 | `supervisor_name` | varchar(128) | 建议 | `data_db.dim_shop.group_manager` | 门店督导 |
| 主管 | `manager_name` | varchar(128) | 建议 | `data_db.dim_shop.zone_manager` | 门店主管 |
| 门店状态编码 | `store_status_code` | varchar(32) | 必须 | `data_db.dim_shop.sp_store_status` | 源系统门店状态编码，中文含义需由开发补充字段字典 |
| 门店状态名称 | `store_status_name` | varchar(64) | 建议 | 状态码字典或开发补充映射 | 门店状态中文名称，例如营业中、闭店、停业等 |
| 是否营业 | `is_open` | tinyint | 必须 | 由 `store_status_code` 派生 | `1` 表示营业，`0` 表示非营业 |
| 数据更新时间 | `data_update_time` | datetime | 必须 | `data_db.dim_shop.update_time`、`load_time`、`etl_time` 或 `dt` | 数据同步或快照更新时间；V1 如果只有 `dt`，需说明是快照日期 |

## 2. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `is_open` | 是否营业 | `1` | 营业 | `store_status_code` 属于业务确认的营业状态 |
| `is_open` | 是否营业 | `0` | 非营业 | `store_status_code` 属于闭店、停业、待开业或其他非营业状态 |
| `store_status_code` | 门店状态编码 | 源系统枚举 | 源系统门店状态 | 开发需补充 `sp_store_status` 每个编码的中文含义和是否营业派生规则 |

## 3. 缺失和降级写法

```text
1. `store_id`、`store_name`、`city_name`、`store_status_code`、`is_open` 不能为空。
2. `area_name`、`manage_area_name`、`region_name` 来源存在多套口径时，开发必须在交付反馈中写清最终采用来源。
3. `store_status_code` 无法映射到是否营业时，`is_open` 不得自行猜测；该状态码进入开发补数清单。
4. 只有分区日期 `dt` 时，`data_update_time` 可先写对应日期的 `00:00:00`，字段注释保留“快照日期”口径。
```

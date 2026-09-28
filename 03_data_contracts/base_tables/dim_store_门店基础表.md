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

## 4. 历史营业状态读取（复用已有历史数据，不新增实体表）

当前门店基础信息仍是一店一行；历史营业判断读取现有 `data_db.dim_shop` 留存日分区中的 `sp_store_id`、`sp_store_status`、`dt`。字段字典已定义状态和日分区，业务已确认本次有三个月历史营业状态；这不是待建设的数据源。不能用当前 `dim_store.is_open` 回填整个历史周期，也不能把“没有小票”推断为停业。

算法 02 使用运行过程数据集 `store_operating_daily`，可以是 CTE，不新增正式表：

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 营业日期 | `business_date` | date | 必须 | `data_db.dim_shop.dt` 经已核实的日期映射 | 按源 ETL 的快照归属日期转换，不把分区加载日期自动当营业日期 |
| 门店编码 | `store_id` | varchar(64) | 必须 | `data_db.dim_shop.sp_store_id` | 与交易、可售表关联 |
| 门店状态编码 | `store_status_code` | varchar(32) | 必须 | `data_db.dim_shop.sp_store_status` | 当日历史状态，沿用第 2 节同一状态码映射 |
| 当日是否营业 | `is_open` | tinyint | 条件必须 | 当日 `store_status_code` 派生 | 已知营业为 1、已知非营业为 0；缺失/无法映射为 NULL，写质量问题，不能默认 0 |

过程唯一键为 `business_date + store_id`。同键完全一致行可去重；状态冲突不得任取一行。交易、货盘按日期和门店同时关联；当前门店名称、城市关联仍按 `dim_store.store_id` 唯一，不把多天历史表只按门店关联。

`dt -> business_date` 的日期转换和营业状态字典属于本数据合同及源 ETL 的固定口径，不在算法 02 另存配置快照或绑定 JSON。若源明确日分区就是当日营业快照，才使用 `business_date = dt`；否则必须在源 ETL 合同中写清转换。每次运行使用的源分区由 `source_data_version（源数据版本）`和 `run_id（运行ID）`在现有调度记录中追溯。

交付验收检查实际日期归属、唯一性、状态映射及本次使用月份覆盖，包括算法实际采用的参数训练/回退日期；不重复询问数据是否存在。缺失门店日或冲突状态不能近似成营业或停业：算法 02 将受影响评分组结果写为 `NOT_CALCULABLE（不可计算）`并记录原因。当前三个月历史已知可用，不据此推断其他参考月份缺失或齐备。

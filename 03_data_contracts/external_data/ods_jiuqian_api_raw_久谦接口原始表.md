# 久谦接口原始表

目标表建议名：`ods_jiuqian_api_raw`

表用途：保存久谦 API 每次返回的原始数据，方便追溯、排错、重跑。

一行代表：一次久谦接口请求 / 一个采集批次。

主键建议：`collection_batch_id + api_name + request_city + request_category + request_time`。

关联要求：

| 关联对象 | 关联字段 | 要求 |
| --- | --- | --- |
| 竞品 SKU 基础表 | 数据采集批次号 | 用于追溯竞品基础数据来自哪次接口 |
| 竞品每日快照表 | 数据采集批次号 | 用于追溯价格、销量、促销快照来自哪次接口 |

## 1. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 数据采集批次号 | `collection_batch_id` | varchar(128) | 必须 | 采集任务生成 | 每次接口采集生成唯一批次号 |
| 数据提供方 | `data_provider` | varchar(64) | 必须 | 采集任务配置 | 外部数据供应方，V1 固定为久谦 |
| 接口名称 | `api_name` | varchar(128) | 必须 | 采集任务配置 | 久谦具体接口名称 |
| 请求城市 | `request_city` | varchar(64) | 必须 | 采集任务参数 | 本次请求城市 |
| 请求类目 | `request_category` | varchar(128) | 必须 | 采集任务参数 | 本次请求类目或关键词 |
| 请求参数 | `request_params` | json 或 string | 必须 | 采集任务参数 | 保存完整接口请求条件 |
| 请求时间 | `request_time` | datetime | 必须 | 采集任务生成 | 接口请求时间 |
| 返回状态 | `response_status` | varchar(32) | 必须 | 接口返回或采集任务生成 | 接口请求结果状态 |
| 返回记录数 | `response_record_count` | bigint | 必须 | 接口返回或采集任务统计 | 本次接口返回商品数量 |
| 原始返回内容 | `raw_response_json` | json 或 string | 必须 | 久谦 API 原始返回 | 原始接口返回内容，保留完整 JSON 原文 |
| 错误信息 | `error_message` | varchar(2048) | 建议 | 接口返回或采集任务生成 | 失败时记录原因，成功时可为空 |
| 数据更新时间 | `data_update_time` | datetime | 必须 | 入库任务生成 | 入库更新时间 |

## 2. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `response_status` | 返回状态 | `SUCCESS` | 成功 | 接口正常返回且原始内容已入库 |
| `response_status` | 返回状态 | `FAILED` | 失败 | 接口请求失败、超时、鉴权失败或返回异常 |
| `response_status` | 返回状态 | `PARTIAL_SUCCESS` | 部分成功 | 批次内部分请求成功，部分请求失败 |

## 3. 缺失和降级写法

```text
1. 主键字段 `collection_batch_id`、`api_name`、`request_city`、`request_category`、`request_time` 不能为空。
2. 请求失败时仍需落一行记录，`response_status` 写 `FAILED`，`raw_response_json` 可为空，`error_message` 必填。
3. `raw_response_json` 必须保留接口原文，不做业务字段裁剪。
4. 从原始表加工到竞品基础表和竞品每日快照表时，必须保留 `collection_batch_id` 追溯来源。
```

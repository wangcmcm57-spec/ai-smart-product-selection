# 算法范围快照表

目标表名：`dim_algorithm_scope_snapshot`

用途：保存算法 01、算法 02 及后续区域算法在一次正式运行中锁定的城市到算法区域映射。它是跨算法共享的不可变快照，不是每个算法自行创建的临时表。

一行代表：一个 `scope_version` 下的一个城市映射。

主键：`scope_version + city`

业务唯一约束：同一 `scope_version + city` 只能有一条记录；同一 `scope_version + scope_id` 下的城市集合和 `scope_type` 必须唯一。

## 1. 来源和生成规则

首次新批次按 `level_end_date` 从 `dim_city_algorithm_region` 命中：

```text
effective_start_date <= level_end_date
AND (effective_end_date IS NULL OR level_end_date < effective_end_date)
AND is_active = 1
```

如果是明确登记的历史补算，仍按同一生效区间命中历史行，`is_active` 只做一致性校验，不把历史 `is_active = 0` 行误当成不存在；补算必须在运行审计中标记 `backfill_flag = 1`。同版本重跑永远直接读取已有快照。

同一城市命中 0 条或多条记录时，阻断该城市所属范围，不跨区域回退。

将命中的语义字段按 `city、algorithm_region_code、algorithm_region_name、effective_start_date、effective_end_date` 去首尾空格并排序，拼接后计算：

```text
scope_version = 'SCOPE_' + SHA256(canonical_scope_rows)[0:16]
```

`data_update_time`、`confirmed_by`、`confirmed_date` 和 `is_active` 的非语义变化不生成新 `scope_version`。区域归属、编码、名称或生效区间变化必须生成新版本；旧快照不得更新或物理删除。

## 2. 字段合同

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 范围版本 | `scope_version` | varchar(64) | 必须 | 规范化映射行 SHA-256 | 本批次不可变的范围版本 |
| 范围版本生成依据 | `scope_version_source` | varchar(32) | 必须 | 快照发布流程 | 固定为 `MAPPING_CANONICAL_SHA256`，用于证明范围版本由规范化映射行生成 |
| 范围类型 | `scope_type` | varchar(32) | 必须 | 按 `scope_version + scope_id` 的城市数判定 | 一个城市为 `CITY`，两个及以上城市为 `CITY_CLUSTER` |
| 范围编码 | `scope_id` | varchar(64) | 必须 | `dim_city_algorithm_region.algorithm_region_code` | 正式算法区域编码，不取城市名 |
| 范围名称 | `scope_name` | varchar(128) | 必须 | `dim_city_algorithm_region.algorithm_region_name` | 正式算法区域名称 |
| 城市 | `city` | varchar(64) | 必须 | `dim_city_algorithm_region.city` | 与 `dim_store.city_name` 对齐 |
| 映射生效开始日期 | `mapping_effective_start_date` | date | 必须 | `dim_city_algorithm_region.effective_start_date` | 被快照锁定的生效起点 |
| 映射生效结束日期 | `mapping_effective_end_date` | date | 条件必须 | `dim_city_algorithm_region.effective_end_date` | 当前映射可为空，历史映射保留结束日期 |
| 源映射更新时间 | `source_mapping_updated_at` | datetime | 必须 | `dim_city_algorithm_region.data_update_time` | 建立快照时的源数据更新时间，仅用于追溯 |
| 快照状态 | `snapshot_status` | varchar(16) | 必须 | 快照发布流程 | `PUBLISHED` / `RETIRED` |
| 快照创建时间 | `snapshot_created_at` | datetime | 必须 | 系统生成 | 快照创建时间 |

## 3. 状态和质量约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `scope_type` | 范围类型 | `CITY` | 单城市范围 | 同一 `scope_version + scope_id` 只包含一个不同城市 |
| `scope_type` | 范围类型 | `CITY_CLUSTER` | 城市群范围 | 同一 `scope_version + scope_id` 包含两个或以上不同城市 |
| `scope_version_source` | 范围版本生成依据 | `MAPPING_CANONICAL_SHA256` | 规范化映射行哈希 | 不允许手工填写或改成运行时间 |
| `snapshot_status` | 快照状态 | `PUBLISHED` | 可供算法读取 | 语义字段完整、唯一性通过且原子发布成功 |
| `snapshot_status` | 快照状态 | `RETIRED` | 已退役但保留历史 | 新范围版本替代，历史结果仍可重跑读取 |

同一 `scope_version + scope_id` 出现城市数与 `scope_type` 不一致时，阻断快照发布并写入数据质量审计。新批次只能读取 `snapshot_status = 'PUBLISHED'` 的快照；历史重跑按明确传入的 `scope_version` 读取原快照，即使其状态已为 `RETIRED`，不得按源表 `is_active = 1` 重新推导范围。

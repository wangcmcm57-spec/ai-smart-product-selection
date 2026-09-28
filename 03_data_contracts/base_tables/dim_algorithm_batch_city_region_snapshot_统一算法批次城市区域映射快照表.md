# 统一算法批次城市区域映射快照表

## 1. 目标表

```text
dim_algorithm_batch_city_region_snapshot
```

该表在新统一算法批次初始化时，将 `dim_city_algorithm_region（城市算法区域映射表）`当时有效的城市映射固化下来，供算法 01～10 在同一批次内共同读取。它保存的是会改变业务比较范围的历史事实，不是每个算法各自维护的配置快照。

## 2. 一行代表什么

```text
一个 algorithm_batch_version（统一算法批次版本）
+ 一个 city（城市）
+ 该城市在本批次锁定的算法区域
```

## 3. 主键或唯一键

```text
algorithm_batch_version + city
```

同一批次、同一城市必须且只能有一条记录。同一城市不能同时属于两个算法区域。

## 4. 生成和重跑规则

新批次初始化时，读取 `dim_city_algorithm_region（城市算法区域映射表）`中在本批 `calculation_end_date（计算结束日期）`当天唯一有效的记录：

```text
effective_start_date <= calculation_end_date
AND (
  effective_end_date IS NULL
  OR effective_end_date >= calculation_end_date
)
```

`is_active（是否当前有效）`只表示现在的状态，不用于回算历史批次；历史归属仅由生效开始/结束日期判定。

规则：

1. 城市未命中或命中多条时阻断批次初始化，不允许算法自行猜测。
2. 同一 `algorithm_batch_version（统一算法批次版本）`的首次运行和重跑始终读取原快照。
3. 原始映射后续新增、失效或回填结束日期，只影响下一完整月批次，不改写历史快照。
4. 同一批次同一算法区域只有一个城市时，`scope_type（范围类型）=CITY（单城市）`；有两个及以上城市时为 `CITY_CLUSTER（城市群）`。
5. 本表不生成 `scope_version（范围版本）`、哈希摘要或第二套版本号。

## 5. 完整字段合同

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 统一算法批次版本 | `algorithm_batch_version` | varchar(32) | 必须 | 全链路调度 | 固定格式 `BATCH_YYYYMM`；进入主键 |
| 计算结束日期 | `calculation_end_date` | date | 必须 | 全链路调度 | 批次统一数据截止月月末；月份必须与统一批次一致 |
| 城市 | `city` | varchar(64) | 必须 | `dim_city_algorithm_region.city` | 对齐 `dim_store.city_name`；进入主键 |
| 算法区域编码 | `algorithm_region_code` | varchar(64) | 必须 | `dim_city_algorithm_region.algorithm_region_code` | 下游统一作为 `scope_id（算法区域编码）` |
| 算法区域名称 | `algorithm_region_name` | varchar(128) | 必须 | `dim_city_algorithm_region.algorithm_region_name` | 下游统一作为 `scope_name（算法区域名称）` |
| 范围类型 | `scope_type` | varchar(32) | 必须 | 本表第 4 节 | `CITY（单城市）` / `CITY_CLUSTER（城市群）` |
| 映射记录生效开始日期 | `mapping_effective_start_date` | date | 必须 | `dim_city_algorithm_region.effective_start_date` | 仅作源映射血缘，不构成第二套版本 |
| 映射记录生效结束日期 | `mapping_effective_end_date` | date | 条件必须 | `dim_city_algorithm_region.effective_end_date` | 原始记录无结束日期时为空；后续回填不得改写本快照 |
| 快照生成时间 | `snapshot_created_at` | datetime | 必须 | 系统生成 | 本批快照首次成功生成时间；同批重跑不更新 |

## 6. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `scope_type` | 范围类型 | `CITY` | 单城市 | 同批次同一算法区域只有一个城市 |
| `scope_type` | 范围类型 | `CITY_CLUSTER` | 城市群 | 同批次同一算法区域有两个及以上城市 |

## 7. 缺失、异常和降级

| 场景 | 处理规则 |
|---|---|
| 城市未命中有效映射 | 阻断新批次初始化，记录缺失城市，不生成不完整快照 |
| 城市同时命中多条有效映射 | 阻断新批次初始化，记录冲突记录，不选择任意一条 |
| 同一批次重复初始化 | 校验已有快照后直接复用，不覆盖、不重新读取当前映射 |
| 映射结束日期为空 | 合法，`mapping_effective_end_date（映射记录生效结束日期）`写 `NULL` |
| 历史批次重跑 | 读取历史批次原快照；禁止读取当前 `is_active=1（当前有效）`记录重建 |

该表没有降级为“实时读取当前映射”的路径。无法取得完整、唯一快照时，相关统一算法批次不得正式发布。

## 8. 验收规则

```text
1. algorithm_batch_version 格式必须为 BATCH_YYYYMM。
2. calculation_end_date 必须为该 YYYYMM 的自然月月末。
3. algorithm_batch_version + city 重复数必须为 0。
4. 所有参与计算门店的城市必须 100% 命中快照。
5. 同批次同一 algorithm_region_code 的 scope_type 必须一致。
6. 同批次同一 algorithm_region_code 只能对应一个 algorithm_region_name。
7. 同批次重跑前后快照行数和业务字段必须完全一致。
8. 新批次映射变化不得改写历史批次。
```

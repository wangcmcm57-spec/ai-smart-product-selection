# 会员筛选规则版本表

目标表名：`dim_member_filter_rule_version`

用途：注册算法 01、算法 02 等会员指标共用的筛选规则版本，保证同一版本使用同一套 SQL/程序实现。该表不是 `dim_customer_profile`，也不保存会员画像结果。

一行代表：一个不可变的会员筛选规则版本。

主键：`member_filter_rule_version`

## 1. 版本和实现规则

规则版本只能新增，不能原地修改。代码或 SQL 仓库中必须存在同名实现，并将实现文件内容的 SHA-256 写入 `rule_sql_digest`。运行任务读取的版本不存在、已退役、或摘要不一致时，会员指标任务失败并进入数据质量告警，不得静默回退到另一版本。

V1 固定规则：

```text
customer_id IS NOT NULL
AND is_customer = 1
AND customer_id NOT LIKE '6%'
有效交易按 order_status = 'os.completed'、is_return = 0、usual_amt > 0、weight > 0 过滤；`refund_type` V1 只作质量审计字段，不单独增加与算法 01 不一致的过滤条件
按 customer_id + business_date 统计 COUNT(DISTINCT order_id)
单日小票数 > 5 时剔除该会员当天全部有效交易
```

`MEMBER_FILTER_V2` 只能新增新记录和新实现；V1 历史结果不得被覆盖。算法 02 不读取 `dim_customer_profile` 或 `profile_model_version`。

## 2. 字段合同

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 会员筛选规则版本 | `member_filter_rule_version` | varchar(64) | 必须 | 系统规则注册 | 例如 `MEMBER_FILTER_V1`，主键 |
| 规则名称 | `rule_name` | varchar(128) | 必须 | 规则注册 | 规则中文名称 |
| 规则 SQL 摘要 | `rule_sql_digest` | varchar(64) | 必须 | 代码/SQL 仓库 SHA-256 | 绑定不可变实现 |
| 规则说明 | `rule_description` | varchar(2048) | 必须 | 规则注册 | 筛选条件和异常会员日阈值 |
| 生效开始日期 | `effective_start_date` | date | 必须 | 规则发布流程 | 版本开始可被运行参数引用的日期 |
| 生效结束日期 | `effective_end_date` | date | 条件必须 | 规则发布流程 | 当前版本可为空；历史版本退役时回填 |
| 规则状态 | `status` | varchar(16) | 必须 | 规则发布流程 | `PUBLISHED` / `RETIRED` |
| 是否当前有效 | `is_active` | tinyint | 必须 | 规则发布流程 | `1` 表示可用于新模型，`0` 表示仅供历史重跑 |
| 注册时间 | `registered_at` | datetime | 必须 | 系统生成 | 规则注册时间 |
| 注册人 | `registered_by` | varchar(128) | 必须 | 系统生成 | 规则发布责任主体；自动发布时为 `SYSTEM_AUTO` |

## 3. 状态约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `status` | 规则状态 | `PUBLISHED` | 可被模型运行参数引用 | 实现摘要校验通过且版本已注册 |
| `status` | 规则状态 | `RETIRED` | 不再用于新模型但保留历史 | 新规则版本替代；历史模型仍可按原版本重跑 |
| `is_active` | 是否当前有效 | `1` | 可用于新模型 | 规则状态为 `PUBLISHED` 且实现摘要校验通过 |
| `is_active` | 是否当前有效 | `0` | 仅供历史重跑 | 规则状态为 `RETIRED` |

算法 01 和算法 02 的运行参数必须记录同一 `member_filter_rule_version`。规则版本变化必须生成新的 `category_level_model_version`；同一数据周期的 V1、V2 结果允许并存。

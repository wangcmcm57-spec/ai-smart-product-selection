# 法规依据表

目标表建议名：`dim_regulation_reference`

表用途：沉淀合规词规则引用的法规、标准、内部制度或官方来源链接。算法不实时访问官网链接，而是通过法源代码引用本表，用于解释、审计和人工复核。

来源文件：`生鲜与食品商品命名合规词库_2026-08-18.xlsx`

核心来源 sheet：`法规依据`

## 1. 表规则

表粒度：

```text
一行 = 一个法规依据版本 + 一个法源代码 + 一个法规或标准依据
```

主键建议：

```text
regulation_version + law_reference_code
```

算法使用：

| 算法 | 使用方式 |
|---|---|
| 算法 07 | 外部趋势或竞品命中风险词时，记录风险词关联的法源代码 |
| 算法 08 | 标准候选命名合规校验时，透传法源代码和依据摘要 |
| 算法 09 | 风险门禁解释候选为什么通过、条件通过、退回或拒绝 |

## 2. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 法规依据版本 | `regulation_version` | varchar(64) | 必须 | 导入批次生成 | 例如 `REGULATION_REF_2026_0818` |
| 法源代码 | `law_reference_code` | varchar(64) | 必须 | Excel 法源代码 | 例如合规词库中维护的 `R01`、`R09` |
| 法规或标准名称 | `regulation_name` | varchar(256) | 必须 | Excel 法规名称 | 法律、法规、标准或内部制度名称 |
| 法规状态 | `regulation_status` | varchar(64) | 建议 | Excel 状态 | `ACTIVE`、`UPDATED`、`REPEALED`、`INTERNAL_RULE` |
| 原始状态和生效时间 | `status_effective_time_raw` | varchar(256) | 建议 | Excel 状态/生效时间 | 保留 Excel 原始文字，便于审计 |
| 生效日期 | `effective_date` | date | 建议 | Excel 或官方资料 | 法规或标准生效日期 |
| 关键条款摘要 | `key_clause` | varchar(2048) | 建议 | Excel 摘要 | 与商品命名、标签、食品安全相关的条款摘要 |
| 命名审核关系 | `naming_audit_relation` | varchar(1024) | 建议 | Excel 或质量维护 | 说明该依据与商品命名审核的关系 |
| 官方来源链接 | `official_source_url` | varchar(1024) | 建议 | Excel 法规链接 | 官方链接或可信来源链接，用于审计追溯 |
| 最近核验时间 | `last_verified_at` | datetime | 建议 | 质量或法务维护 | 最近一次人工或系统核验链接和内容的时间 |
| 核验人 | `verified_by` | varchar(128) | 建议 | 质量或法务维护 | 法务、质量或业务核验人 |
| 是否当前有效 | `is_active` | tinyint | 必须 | 导入规则 | 1 表示当前有效 |
| 来源文件 | `source_file` | varchar(256) | 必须 | 导入元数据 | 来源 Excel 文件名 |
| 来源 sheet | `source_sheet` | varchar(128) | 必须 | 导入元数据 | 来源 sheet 名 |
| 数据更新时间 | `updated_at` | datetime | 必须 | 入库时间 | 数据导入或更新时间 |

## 3. 算法使用例子

```text
候选名称：Omega-3 鲜鸡蛋 12 枚
命中合规词：Omega-3
命名合规词规则表返回：REVIEW_REQUIRED，需要营养成分或检测证明，法源代码 R01
法规依据表返回：R01 对应的法规或标准名称、关键条款摘要、官方来源链接
算法 09 输出：该候选需要补充证明材料后才能通过风险门禁
```

算法运行时不实时访问 `official_source_url`。如果法规更新，由质量、法务或数据维护流程更新本表版本，再触发算法重跑。

## 4. 示例数据

| `regulation_version` | `law_reference_code` | `regulation_name` | `regulation_status` | `official_source_url` | `is_active` |
|---|---|---|---|---|---:|
| `REGULATION_REF_2026_0818` | `R01` | 食品安全相关法规或标准 | `ACTIVE` | 官方来源链接 | 1 |
| `REGULATION_REF_2026_0818` | `R09` | 广告和宣传相关法规或标准 | `ACTIVE` | 官方来源链接 | 1 |

## 5. 数据质量要求

```text
1. law_reference_code 必须和命名合规词规则表中的法源代码保持一致。
2. 官方来源链接用于审计，不作为算法实时判断输入。
3. 法规依据更新时必须生成新版本或更新生效状态，不能静默覆盖历史。
4. 对于内部质量规则，可将 regulation_status 写为 INTERNAL_RULE。
```

## 6. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `regulation_status` | 法规状态 | `ACTIVE` | 现行有效 | 法规、标准或内部制度当前有效 |
| `regulation_status` | 法规状态 | `UPDATED` | 已更新 | 该依据存在新版本，需要通过版本或链接追溯 |
| `regulation_status` | 法规状态 | `REPEALED` | 已废止 | 该依据已废止，只保留历史审计 |
| `regulation_status` | 法规状态 | `INTERNAL_RULE` | 内部规则 | 依据来自内部质量、法务或管理制度 |
| `is_active` | 是否当前有效 | `1` | 当前有效 | 当前算法周期可引用 |
| `is_active` | 是否当前有效 | `0` | 历史无效 | 被新版本或新生效周期替代 |

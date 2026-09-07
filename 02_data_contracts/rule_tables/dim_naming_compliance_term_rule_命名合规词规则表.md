# 命名合规词规则表

目标表建议名：`dim_naming_compliance_term_rule`

表用途：沉淀商品名称、外部趋势词和候选属性中的禁用词、需审核词、风险等级、审核材料和放行条件，供算法 07 识别风险线索，供算法 08 做候选命名合规校验，供算法 09 做正式风险门禁。

来源文件：`生鲜与食品商品命名合规词库_2026-08-18.xlsx`

核心来源 sheet：`词汇明细`

辅助来源 sheet：`分类命名规则`

## 1. 表规则

表粒度：

```text
一行 = 一个合规规则版本 + 一个词组或词根 + 一个适用品类或适用场景
```

主键建议：

```text
compliance_rule_version + term_group_id + applicable_category_name + effective_start_date
```

算法使用：

| 算法 | 使用方式 |
|---|---|
| 算法 07 | 识别外部趋势、外部商品标题、卖点中的法规、标签或食品安全风险线索 |
| 算法 08 | 标准化候选名称时执行命名合规校验，输出风险线索 |
| 算法 09 | 做正式风险门禁，决定候选是否通过、条件通过、退回重构或拒绝 |

## 2. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 合规规则版本 | `compliance_rule_version` | varchar(64) | 必须 | 导入批次生成 | 例如 `COMPLIANCE_2026_0818` |
| 原始序号 | `source_term_no` | varchar(64) | 建议 | Excel 序号 | 合规词库中的原始编号 |
| 词组 ID | `term_group_id` | varchar(64) | 必须 | 导入生成 | 同一类表达的唯一编码 |
| 适用品类 | `applicable_category_name` | varchar(128) | 建议 | Excel 品类字段 | 为空表示全品类适用 |
| 管控结论 | `control_conclusion` | varchar(64) | 必须 | Excel 管控结论 | `BANNED` 禁用、`REVIEW_REQUIRED` 需审核、`ALLOW_WITH_CONDITION` 有条件放行 |
| 风险等级 | `risk_level` | varchar(32) | 必须 | Excel 风险等级 | `HIGH`、`MEDIUM`、`LOW` |
| 二级场景 | `secondary_scene` | varchar(256) | 建议 | Excel 二级场景 | 例如疾病治疗、功能声称、产地声称、认证声称 |
| 风险场景 | `risk_scene` | varchar(256) | 建议 | Excel 或导入规则 | 归一后的风险场景 |
| 词根或表达 | `term_root` | varchar(256) | 必须 | Excel 词根/表达 | 风险词根或标准表达 |
| 常见变形或示例 | `common_variants` | varchar(1024) | 建议 | Excel 常见变形或示例 | 同义、变体、外文或营销表达 |
| 规则属性 | `rule_attribute` | varchar(256) | 建议 | Excel 规则属性 | 说明该词属于禁用、需证明、需限定等哪类规则 |
| 风险原因 | `risk_reason` | varchar(1024) | 建议 | Excel 风险说明 | 为什么该词有风险 |
| 应审核材料 | `required_evidence` | varchar(1024) | 条件必须 | Excel 应审核材料 | 需审核或有条件放行时必须说明需要什么材料 |
| 放行条件 | `release_condition` | varchar(1024) | 条件必须 | Excel 放行条件/判定 | 满足什么条件可以放行 |
| 建议规范表达 | `recommended_expression` | varchar(512) | 建议 | Excel 建议规范表达 | 可替换或更稳妥的商品命名表达 |
| 适用形式 | `applicable_form` | varchar(256) | 建议 | Excel 适用形式 | 适用商品名、卖点、标签、详情页等 |
| 法源代码 | `law_reference_code` | varchar(64) | 建议 | Excel 法源代码 | 关联 `dim_regulation_reference.law_reference_code` |
| 生效口径 | `effective_scope` | varchar(512) | 建议 | Excel 生效口径 | 说明该规则适用的时间、分类或执行口径 |
| 生效依据 | `effective_basis` | varchar(512) | 建议 | Excel 或人工维护 | 法规、内部质量标准或业务规则依据 |
| 规则状态 | `rule_status` | varchar(32) | 必须 | 导入规则 | `ACTIVE`、`REVIEW_REQUIRED`、`DISABLED` |
| 生效开始日期 | `effective_start_date` | date | 必须 | 导入规则 | 规则开始生效日期 |
| 生效结束日期 | `effective_end_date` | date | 建议 | 导入规则 | 当前有效规则可为空 |
| 是否当前有效 | `is_active` | tinyint | 必须 | 导入规则 | 1 表示当前有效 |
| 来源文件 | `source_file` | varchar(256) | 必须 | 导入元数据 | 来源 Excel 文件名 |
| 来源 sheet | `source_sheet` | varchar(128) | 必须 | 导入元数据 | 来源 sheet 名 |
| 数据更新时间 | `updated_at` | datetime | 必须 | 入库时间 | 数据导入或更新时间 |

## 3. 示例数据

| `compliance_rule_version` | `term_root` | `control_conclusion` | `risk_level` | `required_evidence` | `law_reference_code` |
|---|---|---|---|---|---|
| `COMPLIANCE_2026_0818` | 治疗 | `BANNED` | `HIGH` |  | `R09` |
| `COMPLIANCE_2026_0818` | Omega-3 | `REVIEW_REQUIRED` | `MEDIUM` | 营养成分或检测证明 | `R01` |

## 4. 数据质量要求

```text
1. BANNED 词命中后，候选不得进入正式推荐。
2. REVIEW_REQUIRED 或 ALLOW_WITH_CONDITION 命中后，必须记录 required_evidence 和 release_condition。
3. law_reference_code 如果有值，必须能关联到法规依据表。
4. 该表只识别和解释合规风险，正式是否通过门禁由算法 09 判断。
```

## 5. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `control_conclusion` | 管控结论 | `BANNED` | 禁用 | 词根或表达命中后，候选不得进入正式推荐 |
| `control_conclusion` | 管控结论 | `REVIEW_REQUIRED` | 需审核 | 词根或表达命中后，必须补充审核材料或人工判断 |
| `control_conclusion` | 管控结论 | `ALLOW_WITH_CONDITION` | 有条件放行 | 满足放行条件并留存材料后才可通过 |
| `risk_level` | 风险等级 | `HIGH` | 高风险 | 命中后优先进入风险门禁或人工审核 |
| `risk_level` | 风险等级 | `MEDIUM` | 中风险 | 命中后需要记录证据和审核条件 |
| `risk_level` | 风险等级 | `LOW` | 低风险 | 命中后保留提示或低优先级复核 |
| `rule_status` | 规则状态 | `ACTIVE` | 生效 | 规则已确认，算法可正式读取 |
| `rule_status` | 规则状态 | `REVIEW_REQUIRED` | 需复核 | 规则口径仍需质量、法务或商品侧确认 |
| `rule_status` | 规则状态 | `DISABLED` | 停用 | 规则历史保留，不参与当前算法 |
| `is_active` | 是否当前有效 | `1` | 当前有效 | 当前算法周期可读取 |
| `is_active` | 是否当前有效 | `0` | 历史无效 | 被新版本或新生效周期替代 |

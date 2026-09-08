# 分类命名合规规则表

目标表建议名：`dim_category_naming_compliance_rule`

表用途：沉淀不同商品分类和适用形态下的命名结构、必须核对项、高风险示例、推荐示例和证照提示，供算法 07 识别外部商品命名风险，供算法 08/09 做候选名称合规校验。

来源文件：`生鲜与食品商品命名合规词库_2026-08-18.xlsx`

核心来源 sheet：`分类命名规则`

## 1. 表规则

表粒度：

```text
一行 = 一个分类命名合规规则版本 + 一个商品分类 + 一个适用形态 + 一个生效周期
```

主键建议：

```text
category_compliance_rule_version + category_name + applicable_form + effective_start_date
```

算法使用：

| 算法 | 使用方式 |
|---|---|
| 算法 07 | 解析外部商品名时识别是否存在分类命名风险或证照风险 |
| 算法 08 | 生成标准候选名称时校验分类命名结构和显著标示要求 |
| 算法 09 | 风险门禁时判断候选是否需要证照、标签或材料审核 |

## 2. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 分类合规规则版本 | `category_compliance_rule_version` | varchar(64) | 必须 | 导入批次生成 | 例如 `CATEGORY_COMPLIANCE_2026_0818` |
| 商品分类 | `category_name` | varchar(128) | 必须 | Excel 分类 | 合规词库中的商品分类，例如蔬菜、水果 |
| 内部分类编码 | `internal_category_code` | varchar(64) | 建议 | `dim_sku` 映射 | 能映射内部分类时填写 |
| 内部分类层级 | `internal_category_level` | varchar(32) | 建议 | `dim_sku` 映射 | `CATEGORY_LEVEL1`、`CATEGORY_LEVEL2`、`CATEGORY_LEVEL3` |
| 适用形态 | `applicable_form` | varchar(256) | 必须 | Excel 适用形态 | 例如散装、包装鲜蔬菜、加工形态 |
| 推荐命名结构 | `recommended_name_structure` | varchar(1024) | 必须 | Excel 推荐命名结构 | 该分类下更稳妥的命名结构 |
| 必须核对或显著标示 | `mandatory_check_items` | varchar(1024) | 必须 | Excel 必须核对/显著标示 | 进入正式候选前必须核对或标示的事项 |
| 高风险或错误示例 | `high_risk_examples` | varchar(2048) | 建议 | Excel 高风险或错误示例 | 用于风险识别和验收，不作为正式商品样例 |
| 推荐示例 | `recommended_examples` | varchar(2048) | 建议 | Excel 推荐示例 | 用于说明规范表达方式 |
| SC 或证照提示 | `license_audit_requirement` | varchar(1024) | 建议 | Excel SC/证照提示 | 是否需要生产许可、证照或供应链材料核验 |
| 规则状态 | `rule_status` | varchar(32) | 必须 | 导入规则 | `ACTIVE`、`REVIEW_REQUIRED`、`DISABLED` |
| 生效开始日期 | `effective_start_date` | date | 必须 | 导入规则 | 规则开始生效日期 |
| 生效结束日期 | `effective_end_date` | date | 建议 | 导入规则 | 当前有效规则可为空 |
| 是否当前有效 | `is_active` | tinyint | 必须 | 导入规则 | 1 表示当前有效 |
| 来源文件 | `source_file` | varchar(256) | 必须 | 导入元数据 | 来源 Excel 文件名 |
| 来源 sheet | `source_sheet` | varchar(128) | 必须 | 导入元数据 | 来源 sheet 名 |
| 数据更新时间 | `updated_at` | datetime | 必须 | 入库时间 | 数据导入或更新时间 |

## 3. 示例数据

| `category_compliance_rule_version` | `category_name` | `applicable_form` | `recommended_name_structure` | `mandatory_check_items` | `rule_status` |
|---|---|---|---|---|---|
| `CATEGORY_COMPLIANCE_2026_0818` | 蔬菜 | 散装/包装鲜蔬菜 | 产地 + 品种/通用名 + 规格 | 真实品种、真实产地、加工状态 | `ACTIVE` |
| `CATEGORY_COMPLIANCE_2026_0818` | 水果 | 散装/包装鲜水果 | 产地/原产国 + 品种/通用名 + 规格 | 进口、地理标志、甜度、采收日期需有证据 | `ACTIVE` |

## 4. 数据质量要求

```text
1. 同一规则版本、同一商品分类、同一适用形态只能有一条当前有效规则。
2. 推荐命名结构和必须核对项不能为空。
3. 证照提示不直接判定候选失败，但会传给算法 09 做风险门禁。
4. 如果分类无法映射内部分类编码，规则仍可导入，但 rule_status 写 REVIEW_REQUIRED。
```

## 5. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `internal_category_level` | 内部分类层级 | `CATEGORY_LEVEL1` | 一级分类 | 规则映射到内部一级分类 |
| `internal_category_level` | 内部分类层级 | `CATEGORY_LEVEL2` | 二级分类 | 规则映射到内部二级分类 |
| `internal_category_level` | 内部分类层级 | `CATEGORY_LEVEL3` | 三级分类 | 规则映射到内部三级分类 |
| `rule_status` | 规则状态 | `ACTIVE` | 生效 | 规则已确认，算法可正式读取 |
| `rule_status` | 规则状态 | `REVIEW_REQUIRED` | 需复核 | 分类映射或合规口径仍需人工确认 |
| `rule_status` | 规则状态 | `DISABLED` | 停用 | 规则历史保留，不参与当前算法 |
| `is_active` | 是否当前有效 | `1` | 当前有效 | 当前算法周期可读取 |
| `is_active` | 是否当前有效 | `0` | 历史无效 | 被新版本或新生效周期替代 |

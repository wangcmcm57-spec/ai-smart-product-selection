# 候选属性字典表

目标表建议名：`dim_candidate_attribute_dictionary`

表用途：沉淀候选新品会用到的标准属性、同义词、外文词、别名和适用品类，供算法 07 做外部商品解析，供算法 08 做候选标准化、命名和合并。

来源：`B3-按竞对商品名称梳理的命名规则.xlsx`、商品基础表、外部竞品数据、合规词库，以及系统自动生成的高频词候选。

## 1. 表规则

表粒度：

```text
一行 = 一个属性字典版本 + 一个标准属性 + 一个别名或词根 + 一个适用品类
```

主键建议：

```text
attribute_dict_version + canonical_attribute_code + term_alias + applicable_category_code
```

算法使用：

| 算法 | 使用方式 |
|---|---|
| 算法 07 | 把外部商品名、外文词、趋势词解析成标准属性维度 |
| 算法 08 | 判断候选是否同义、是否可合并、是否能生成标准候选名称 |

## 2. 属性维度枚举

| 属性维度 | 中文含义 | 说明 |
|---|---|---|
| `MAIN_PRODUCT` | 主体商品 | 商品名称里真正要卖的主体，例如鲜鸡蛋、牛柳、鸡胸肉 |
| `MAIN_MATERIAL` | 主材料 | 加工品或配方商品的主要原料，例如鸡胸肉、牛肉 |
| `FLAVOR` | 口味 | 黑椒、藤椒、蒜香等 |
| `PROCESS` | 工艺/加工方式 | HPP、低温慢煮、即烹、即食等 |
| `FUNCTION_CLAIM` | 功能卖点 | Omega-3、高蛋白、低钠等，需要合规校验 |
| `SPEC` | 规格 | 200g、12枚、400g/袋等 |
| `PACKAGING` | 包装 | 袋装、盒装、杯装、家庭装等 |
| `SALES_UNIT` | 销售单位 | 份、个、盒、袋、kg 等 |
| `ORIGIN` | 产地 | 云南、泰国、进口等真实产地或原产国 |
| `GRADE` | 等级 | 特级、一级、精品、大果等等级描述 |
| `CULTIVATION_METHOD` | 种植或养殖方式 | 有机、绿色、散养等 |
| `CERTIFICATION` | 认证 | GAP、绿色食品、有机认证等 |
| `PRODUCT_FORM` | 商品形态 | 鲜切、净菜、整只、切片、袋装配菜等 |
| `TEMPERATURE_STATE` | 温层或状态 | 冷藏、冷冻、常温、鲜活等 |
| `STORAGE_CONDITION` | 存储条件 | 0-4 度冷藏、冷冻保存等 |
| `BRAND` | 品牌 | 外部竞品或内部商品品牌 |
| `MODEL` | 型号 | 非食品属性或标品型号，生鲜 V1 谨慎使用 |
| `SCENE` | 场景 | 早餐、火锅、露营等；默认不直接进入商品主体 |
| `RISK_CLAIM` | 风险声称 | 可能触发合规或质量审核的词 |

## 3. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 属性字典版本 | `attribute_dict_version` | varchar(64) | 必须 | 系统生成或导入批次 | 例如 `ATTR_DICT_2026_V1` |
| 标准属性编码 | `canonical_attribute_code` | varchar(64) | 必须 | 系统生成或人工确认 | 标准属性唯一编码 |
| 标准属性名称 | `canonical_attribute_name` | varchar(128) | 必须 | 系统生成或人工确认 | 例如 Omega-3、黑椒、HPP |
| 属性维度 | `attribute_dimension` | varchar(64) | 必须 | 规则判断 | 取值见属性维度枚举 |
| 词语语言 | `term_language` | varchar(32) | 必须 | 系统识别 | `zh`、`en`、`ja`、`mixed` |
| 词语别名 | `term_alias` | varchar(256) | 必须 | B3、外部数据或系统生成 | 外部词、同义词或别名，例如欧米伽3、Omega3 |
| 适用品类编码 | `applicable_category_code` | varchar(64) | 建议 | `dim_sku` 映射 | 属性适用的内部品类编码 |
| 适用品类名称 | `applicable_category_name` | varchar(128) | 建议 | `dim_sku` 映射 | 属性适用的内部品类名称 |
| 规则来源 | `rule_source` | varchar(64) | 必须 | 导入或生成规则 | `B3_RULE`、`COMPLIANCE_TERM`、`SYSTEM_GENERATED`、`MANUAL_REVIEW` |
| 识别置信度 | `confidence` | decimal(8,6) | 建议 | 系统计算 | 0 到 1；人工确认可写 1 |
| 复核状态 | `review_status` | varchar(32) | 必须 | 系统或人工维护 | `AUTO_APPROVED`、`REVIEW_REQUIRED`、`APPROVED`、`REJECTED` |
| 是否允许入名 | `allow_in_candidate_name` | tinyint | 必须 | 规则判断 | 1 表示可进入正式候选名称 |
| 是否风险词 | `is_risk_term` | tinyint | 必须 | 合规词库映射 | 1 表示需要传给合规门禁 |
| 生效开始日期 | `effective_start_date` | date | 必须 | 导入规则 | 规则开始生效日期 |
| 生效结束日期 | `effective_end_date` | date | 建议 | 导入规则 | 当前有效规则可为空 |
| 是否当前有效 | `is_active` | tinyint | 必须 | 导入规则 | 1 表示当前有效 |
| 来源文件 | `source_file` | varchar(256) | 建议 | 导入元数据 | 系统生成可写 `SYSTEM_GENERATED` |
| 来源 sheet | `source_sheet` | varchar(128) | 建议 | 导入元数据 | 来源 sheet 名 |
| 数据更新时间 | `updated_at` | datetime | 必须 | 入库时间 | 数据导入或更新时间 |

## 4. V1 自动生成规则

```text
1. 从商品基础表、竞品商品名、算法 06/07 候选词中抽取高频词。
2. 按 B3 命名规则、商品基础表分类、规格格式和合规词库识别属性维度。
3. 能稳定判断的词写 AUTO_APPROVED。
4. 高频词、会进入新品名称的词、风险词写 REVIEW_REQUIRED，交业务/商品/质量复核。
5. 复核通过后写 APPROVED，复核拒绝后写 REJECTED。
```

业务不需要一次性提供完整字典，但需要复核高频词、入名词、风险词和重点小分类模板。

## 5. 示例数据

| `attribute_dict_version` | `canonical_attribute_name` | `attribute_dimension` | `term_language` | `term_alias` | `applicable_category_name` | `review_status` |
|---|---|---|---|---|---|---|
| `ATTR_DICT_2026_V1` | Omega-3 | `FUNCTION_CLAIM` | `mixed` | 欧米伽3 | 鲜鸡蛋 | `REVIEW_REQUIRED` |
| `ATTR_DICT_2026_V1` | 黑椒 | `FLAVOR` | `zh` | 黑胡椒 | 牛肉类 | `AUTO_APPROVED` |
| `ATTR_DICT_2026_V1` | HPP | `PROCESS` | `en` | 高压冷杀菌 | 鸡肉类 | `REVIEW_REQUIRED` |

## 6. 数据质量要求

```text
1. 同一个别名在同一适用品类下只能映射到一个当前有效标准属性。
2. REVIEW_REQUIRED 或 REJECTED 的词不能直接进入正式候选名称。
3. FUNCTION_CLAIM 和 RISK_CLAIM 必须联动合规词规则表。
4. 该表是属性标准化入口，不替代商品基础表。
```

## 7. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `rule_source` | 规则来源 | `B3_RULE` | B3 命名规则来源 | 词语来自 B3 命名、分类或属性规则整理 |
| `rule_source` | 规则来源 | `COMPLIANCE_TERM` | 合规词来源 | 词语来自命名合规词库 |
| `rule_source` | 规则来源 | `SYSTEM_GENERATED` | 系统生成 | 词语由商品名、竞品名或候选结果自动抽取 |
| `rule_source` | 规则来源 | `MANUAL_REVIEW` | 人工复核 | 词语由人工复核后补充或修正 |
| `review_status` | 复核状态 | `AUTO_APPROVED` | 自动通过 | 系统规则可稳定判断，允许按当前口径使用 |
| `review_status` | 复核状态 | `REVIEW_REQUIRED` | 需复核 | 高频词、风险词或入名词仍需人工确认 |
| `review_status` | 复核状态 | `APPROVED` | 人工通过 | 已由业务、商品或质量侧确认可用 |
| `review_status` | 复核状态 | `REJECTED` | 人工拒绝 | 已确认不能作为当前标准属性使用 |
| `allow_in_candidate_name` | 是否允许入名 | `1` | 允许入名 | 该属性可进入正式候选名称 |
| `allow_in_candidate_name` | 是否允许入名 | `0` | 不允许入名 | 该属性只作解析、证据或风险判断，不进入正式候选名称 |
| `is_risk_term` | 是否风险词 | `1` | 风险词 | 需要传给合规或风险门禁 |
| `is_risk_term` | 是否风险词 | `0` | 非风险词 | 不按风险词处理 |
| `is_active` | 是否当前有效 | `1` | 当前有效 | 当前算法周期可读取 |
| `is_active` | 是否当前有效 | `0` | 历史无效 | 被新版本或新生效周期替代 |

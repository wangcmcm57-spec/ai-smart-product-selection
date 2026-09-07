# 竞对分类映射规则表

目标表建议名：`dim_competitor_category_mapping_rule`

表用途：沉淀外部竞品分类、商品类型、菜品类型到内部商品分类的映射规则，供算法 07 把外部商品或趋势落到内部可计算的小分类。

来源文件：`B3-按竞对商品名称梳理的命名规则.xlsx`

核心来源 sheet：`竞对中类映射`

## 1. 表规则

表粒度：

```text
一行 = 一个映射规则版本 + 一个外部来源 + 一个外部分类或商品类型 + 一个内部分类映射
```

主键建议：

```text
mapping_rule_version + competitor_source + competitor_category_path + competitor_product_type + internal_category_level2_code
```

算法使用：

| 算法 | 使用方式 |
|---|---|
| 算法 07 | 将外部商品、外部趋势或竞品商品映射到内部大类、中类、小分类 |
| 算法 08 | 复核候选标准化后的分类是否和 07 映射结果一致 |

## 2. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 映射规则版本 | `mapping_rule_version` | varchar(64) | 必须 | 导入批次生成 | 例如 `COMP_CAT_MAP_2026_V1` |
| 外部来源 | `competitor_source` | varchar(64) | 必须 | 外部数据源或 Excel | 例如久谦、盒马、山姆、叮咚买菜等 |
| 外部分类路径 | `competitor_category_path` | varchar(512) | 建议 | Excel 或外部源 | 外部平台原始分类路径 |
| 外部菜品类型 | `competitor_dish_type` | varchar(128) | 建议 | Excel 或解析结果 | 例如即食、即烹、净菜、熟食 |
| 外部商品类型 | `competitor_product_type` | varchar(128) | 必须 | Excel 或解析结果 | 外部商品归纳类型 |
| 内部一级分类编码 | `internal_category_level1_code` | varchar(64) | 建议 | `dim_sku` 映射 | 内部大类编码 |
| 内部一级分类名称 | `internal_category_level1_name` | varchar(128) | 必须 | Excel 映射 | 内部大类名称 |
| 内部二级分类编码 | `internal_category_level2_code` | varchar(64) | 建议 | `dim_sku` 映射 | 内部中类编码 |
| 内部二级分类名称 | `internal_category_level2_name` | varchar(128) | 必须 | Excel 映射 | 内部中类名称 |
| 内部三级分类编码 | `internal_category_level3_code` | varchar(64) | 建议 | `dim_sku` 映射 | 内部小分类编码 |
| 内部三级分类名称 | `internal_category_level3_name` | varchar(128) | 建议 | Excel 或 `dim_sku` 映射 | 内部最细分类名称 |
| 样本数量 | `sample_count` | int | 建议 | Excel 统计 | 支撑该映射的竞品样本数 |
| 映射置信度 | `mapping_confidence` | decimal(8,6) | 建议 | 系统计算或人工确认 | 0 到 1，人工确认可写 1 |
| 映射依据 | `mapping_basis` | varchar(1024) | 建议 | Excel 或人工维护 | 说明按名称、分类、主材料、样本等哪类依据映射 |
| 映射状态 | `mapping_status` | varchar(32) | 必须 | 导入规则 | `ACTIVE`、`REVIEW_REQUIRED`、`DISABLED` |
| 生效开始日期 | `effective_start_date` | date | 必须 | 导入规则 | 规则开始生效日期 |
| 生效结束日期 | `effective_end_date` | date | 建议 | 导入规则 | 当前有效规则可为空 |
| 是否当前有效 | `is_active` | tinyint | 必须 | 导入规则 | 1 表示当前有效 |
| 来源文件 | `source_file` | varchar(256) | 必须 | 导入元数据 | 来源 Excel 文件名 |
| 来源 sheet | `source_sheet` | varchar(128) | 必须 | 导入元数据 | 来源 sheet 名 |
| 数据更新时间 | `updated_at` | datetime | 必须 | 入库时间 | 数据导入或更新时间 |

## 3. 示例数据

| `mapping_rule_version` | `competitor_source` | `competitor_product_type` | `internal_category_level1_name` | `internal_category_level2_name` | `mapping_status` |
|---|---|---|---|---|---|
| `COMP_CAT_MAP_2026_V1` | 久谦 | 净菜/配菜 | 蔬菜 | 净配菜类 | `ACTIVE` |
| `COMP_CAT_MAP_2026_V1` | 久谦 | 调理肉制品 | 肉禽蛋 | 牛肉类 | `REVIEW_REQUIRED` |

## 4. 数据质量要求

```text
1. 映射到内部分类时，必须优先使用 dim_sku 中已有分类编码和名称。
2. REVIEW_REQUIRED 的映射只能保留外部证据，不能直接进入正式候选。
3. 同一版本、同一外部来源、同一外部分类或商品类型不能映射到多个当前有效内部中类，除非规则状态为 REVIEW_REQUIRED。
4. 算法 07 映射失败时输出 CATEGORY_MAPPING_GAP，不让开发凭感觉补分类。
```

## 5. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `mapping_status` | 映射状态 | `ACTIVE` | 生效 | 映射已确认，算法 07 可用于正式分类映射 |
| `mapping_status` | 映射状态 | `REVIEW_REQUIRED` | 需复核 | 映射置信度不足或缺内部分类编码，只能保留证据 |
| `mapping_status` | 映射状态 | `DISABLED` | 停用 | 映射历史保留，不参与当前算法 |
| `is_active` | 是否当前有效 | `1` | 当前有效 | 当前算法周期可读取 |
| `is_active` | 是否当前有效 | `0` | 历史无效 | 被新版本或新生效周期替代 |

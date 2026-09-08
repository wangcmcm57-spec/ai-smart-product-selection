# 商品命名规则表

目标表建议名：`dim_product_naming_rule`

表用途：沉淀不同中类/小分类的新品命名结构、必填字段、查重字段和异常拦截规则，供算法 08 生成标准候选名称、标准候选快照和查重键。

来源文件：`B3-按竞对商品名称梳理的命名规则.xlsx`

核心来源 sheet：`中类规则主表`

参考来源 sheet：`分类库参考`、`主数据字段参考`

## 1. 表规则

表粒度：

```text
一行 = 一个命名规则版本 + 一个内部中类 + 一个适用小分类集合 + 一个生效周期
```

主键建议：

```text
naming_rule_version + category_level2_code + effective_start_date
```

算法使用：

| 算法 | 使用方式 |
|---|---|
| 算法 07 | 解析外部商品名时识别主体商品、规格、工艺、功能卖点等结构化属性 |
| 算法 08 | 生成标准候选名称、查重字段、异常拦截状态 |

## 2. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 命名规则版本 | `naming_rule_version` | varchar(64) | 必须 | 导入批次生成 | 例如 `NAMING_2026_V1` |
| 一级分类名称 | `category_level1_name` | varchar(128) | 必须 | Excel 公司分类 | 内部大类名称 |
| 二级分类编码 | `category_level2_code` | varchar(64) | 建议 | `dim_sku` 映射 | 内部中类编码 |
| 二级分类名称 | `category_level2_name` | varchar(128) | 必须 | Excel 中类 | 内部中类名称 |
| 覆盖小分类名称 | `covered_category_names` | varchar(1024) | 建议 | Excel 覆盖小类 | 该规则覆盖的小分类名称列表 |
| 竞对样本数量 | `competitor_sample_count` | int | 建议 | Excel 统计 | 支撑命名规则的竞对样本数 |
| 主数据样本数量 | `master_data_sample_count` | int | 建议 | Excel 统计 | 支撑命名规则的内部主数据样本数 |
| 推荐命名结构 | `recommended_name_structure` | varchar(1024) | 必须 | Excel 命名结构 | 例如主体商品 + 规格 + 包装，或产地 + 主体商品 + 等级 |
| 名称必填字段 | `required_name_fields` | varchar(1024) | 必须 | Excel 必填字段 | 进入正式候选名称必须具备的字段列表 |
| 可选关键字段 | `optional_key_fields` | varchar(1024) | 建议 | Excel 可选字段 | 有则进入名称或证据、无则不阻断 |
| 特殊必填规则说明 | `special_required_rule` | varchar(1024) | 建议 | Excel 特殊规则 | 特殊品类更细规则；结构化规则见 `dim_special_product_required_attribute_rule` |
| 查重字段 | `dedupe_key_fields` | varchar(1024) | 必须 | Excel 查重建议字段 | 生成候选去重键使用的字段 |
| 异常拦截规则 | `exception_rule` | varchar(1024) | 建议 | Excel 异常拦截 | 缺字段、错分类、风险词等拦截说明 |
| 示例商品名称 | `example_names` | varchar(2048) | 建议 | Excel 示例 | 用于验收命名结构，不作为真实数据样例发布 |
| 规则状态 | `rule_status` | varchar(32) | 必须 | 导入规则 | `ACTIVE`、`REVIEW_REQUIRED`、`DISABLED` |
| 生效开始日期 | `effective_start_date` | date | 必须 | 导入规则 | 规则开始生效日期 |
| 生效结束日期 | `effective_end_date` | date | 建议 | 导入规则 | 当前有效规则可为空 |
| 是否当前有效 | `is_active` | tinyint | 必须 | 导入规则 | 1 表示当前有效 |
| 来源文件 | `source_file` | varchar(256) | 必须 | 导入元数据 | 来源 Excel 文件名 |
| 来源 sheet | `source_sheet` | varchar(128) | 必须 | 导入元数据 | 来源 sheet 名 |
| 数据更新时间 | `updated_at` | datetime | 必须 | 入库时间 | 数据导入或更新时间 |

## 3. 示例数据

| `naming_rule_version` | `category_level2_name` | `recommended_name_structure` | `required_name_fields` | `dedupe_key_fields` | `rule_status` |
|---|---|---|---|---|---|
| `NAMING_2026_V1` | 鲜鸡蛋 | 主体商品 + 功能属性 + 规格 | 主体商品,规格 | 主体商品,功能属性,规格 | `ACTIVE` |
| `NAMING_2026_V1` | 牛肉类 | 工艺/口味 + 主体商品 + 规格 | 主体商品,规格 | 主体商品,口味,工艺,规格 | `ACTIVE` |

## 4. 数据质量要求

```text
1. required_name_fields 中的字段必须能在属性字典或候选解析结果中找到对应维度。
2. 命名规则只定义名称结构，不替代分类映射、合规判断和价格可行性判断。
3. 缺少必填命名字段时，算法 08 不能生成正式候选名称，状态写 REGISTRATION_EXCEPTION 或 ATTRIBUTE_REQUIRED_MISSING。
4. REVIEW_REQUIRED 的规则必须进入人工复核后才能转为 ACTIVE。
```

## 5. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `rule_status` | 规则状态 | `ACTIVE` | 生效 | 规则已确认，算法可正式读取 |
| `rule_status` | 规则状态 | `REVIEW_REQUIRED` | 需复核 | 命名结构、必填字段或查重字段仍需人工确认 |
| `rule_status` | 规则状态 | `DISABLED` | 停用 | 规则历史保留，不参与当前算法 |
| `is_active` | 是否当前有效 | `1` | 当前有效 | 当前算法周期可读取 |
| `is_active` | 是否当前有效 | `0` | 历史无效 | 被新版本或新生效周期替代 |

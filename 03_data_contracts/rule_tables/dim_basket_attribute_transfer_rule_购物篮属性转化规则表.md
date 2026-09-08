# 购物篮属性转化规则表

目标表建议名：`dim_basket_attribute_transfer_rule`

表用途：沉淀算法 06 判断“购物篮关联商品 B 是否能转化为锚点商品 A 的新品属性”的规则。该表防止算法只靠 AI 常识把任意共购关系拼成新品。

来源文件：`B4-哪些购物篮关联能够转化为新品属性.xlsx`

核心来源 sheet：`算法6主材料+配料，正向`

辅助来源 sheet：`Sheet1` 仅作上海华东一区商品清单参考，不替代正式 `dim_sku`。

## 1. 表规则

表粒度：

```text
一行 = 一个规则版本 + 一个锚点品类 + 一个关联品类 + 一个转化判断
```

主键建议：

```text
basket_rule_version + anchor_category_level + anchor_category_code + related_category_level + related_category_code
```

算法使用：

| 算法 | 使用方式 |
|---|---|
| 算法 06 | 判断购物篮关联 B 是否允许变成新品属性，缺规则时输出 `CATEGORY_RULE_NOT_CONFIGURED` |
| 算法 08 | 判断候选属性和标准候选名称是否仍保持在目标品类内 |

## 2. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 购物篮规则版本 | `basket_rule_version` | varchar(64) | 必须 | 导入批次生成 | 例如 `BASKET_ATTR_2026_V1` |
| 锚点品类层级 | `anchor_category_level` | varchar(32) | 必须 | Excel 分类列 | `CATEGORY_LEVEL1`、`CATEGORY_LEVEL2`、`CATEGORY_LEVEL3` |
| 锚点品类编码 | `anchor_category_code` | varchar(64) | 建议 | `dim_sku` 映射 | 锚点 A 所属品类编码 |
| 锚点品类名称 | `anchor_category_name` | varchar(128) | 必须 | Excel 配方型品类列 | 例如牛肉类、鸡类、猪肉类、即烹类 |
| 关联品类层级 | `related_category_level` | varchar(32) | 必须 | Excel 品类保持列 | `CATEGORY_LEVEL1`、`CATEGORY_LEVEL2`、`CATEGORY_LEVEL3` |
| 关联品类编码 | `related_category_code` | varchar(64) | 建议 | `dim_sku` 映射 | 关联商品 B 所属品类编码 |
| 关联品类名称 | `related_category_name` | varchar(128) | 必须 | Excel 品类保持列 | 例如根茎类、瓜果类、调味类、菌菇类 |
| 转化类型 | `transfer_type` | varchar(64) | 必须 | 导入规则 | `INGREDIENT` 配料、`SIDE_DISH` 搭配、`SCENE_ONLY` 场景 |
| 是否允许转新品属性 | `is_allowed_transfer` | tinyint | 必须 | 导入规则 | 1 允许转属性，0 只保留证据或禁止 |
| 属性维度 | `attribute_dimension` | varchar(64) | 建议 | 导入规则 | 例如配料、口味、场景、规格 |
| 未覆盖处理方式 | `not_covered_action` | varchar(64) | 必须 | 算法 06 口径 | V1 缺规则时写 `CATEGORY_RULE_NOT_CONFIGURED` |
| 规则状态 | `rule_status` | varchar(32) | 必须 | 导入规则 | `ACTIVE`、`REVIEW_REQUIRED`、`DISABLED` |
| 生效开始日期 | `effective_start_date` | date | 必须 | 导入规则 | 规则开始生效日期 |
| 生效结束日期 | `effective_end_date` | date | 建议 | 导入规则 | 当前有效规则可为空 |
| 是否当前有效 | `is_active` | tinyint | 必须 | 导入规则 | 1 表示当前有效 |
| 来源文件 | `source_file` | varchar(256) | 必须 | 导入元数据 | 来源 Excel 文件名 |
| 来源 sheet | `source_sheet` | varchar(128) | 必须 | 导入元数据 | 来源 sheet 名 |
| 数据更新时间 | `updated_at` | datetime | 必须 | 入库时间 | 数据导入或更新时间 |

## 3. 示例数据

| `basket_rule_version` | `anchor_category_name` | `related_category_name` | `transfer_type` | `is_allowed_transfer` | `not_covered_action` |
|---|---|---|---|---:|---|
| `BASKET_ATTR_2026_V1` | 牛肉类 | 根茎类 | `INGREDIENT` | 1 | `CATEGORY_RULE_NOT_CONFIGURED` |
| `BASKET_ATTR_2026_V1` | 鸡类 | 调味类 | `INGREDIENT` | 1 | `CATEGORY_RULE_NOT_CONFIGURED` |
| `BASKET_ATTR_2026_V1` | 鱼丸类 | 豆腐类 | `SIDE_DISH` | 1 | `CATEGORY_RULE_NOT_CONFIGURED` |

## 4. 数据质量要求

```text
1. 锚点品类和关联品类必须能映射到商品基础表中的正式品类。
2. 同一规则版本下，同一锚点品类 + 关联品类只能有一个当前有效判断。
3. 未覆盖关系不能默认允许，必须输出 CATEGORY_RULE_NOT_CONFIGURED。
4. 该表只判断“能否转属性”，不判断购物篮关联强度；关联强度仍由算法 06 计算。
```

## 5. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `transfer_type` | 转化类型 | `INGREDIENT` | 配料转化 | 关联商品 B 可以作为锚点商品 A 的配料属性 |
| `transfer_type` | 转化类型 | `SIDE_DISH` | 搭配转化 | 关联商品 B 可以作为搭配或组合场景属性 |
| `transfer_type` | 转化类型 | `SCENE_ONLY` | 仅场景证据 | 关联关系只说明消费场景，不进入新品属性 |
| `is_allowed_transfer` | 是否允许转新品属性 | `1` | 允许 | 该品类关系可以生成候选属性 |
| `is_allowed_transfer` | 是否允许转新品属性 | `0` | 不允许 | 该品类关系只能保留证据或禁止转化 |
| `not_covered_action` | 未覆盖处理方式 | `CATEGORY_RULE_NOT_CONFIGURED` | 品类规则未配置 | 锚点品类和关联品类在当前规则版本中没有可用配置 |
| `rule_status` | 规则状态 | `ACTIVE` | 生效 | 规则已确认，算法可正式读取 |
| `rule_status` | 规则状态 | `REVIEW_REQUIRED` | 需复核 | 规则保留入表，但算法不能当作已确认规则直接放行 |
| `rule_status` | 规则状态 | `DISABLED` | 停用 | 规则历史保留，不参与当前算法 |
| `is_active` | 是否当前有效 | `1` | 当前有效 | 当前算法周期可读取 |
| `is_active` | 是否当前有效 | `0` | 历史无效 | 被新版本或新生效周期替代 |

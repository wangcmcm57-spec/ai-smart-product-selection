# 特殊品类必填属性规则表

目标表建议名：`dim_special_product_required_attribute_rule`

表用途：沉淀特殊商品、特殊物种或特殊关键词在生成候选名称和标准候选时必须具备的属性要求，防止“蓝莓没有果径”“大闸蟹没有公母和重量”这类候选进入正式推荐。

来源文件：`B3-按竞对商品名称梳理的命名规则.xlsx`

核心来源 sheet：`特殊物种必填规则`

## 1. 表规则

表粒度：

```text
一行 = 一个特殊必填规则版本 + 一个适用分类 + 一个商品关键词 + 一个必填属性集合
```

主键建议：

```text
special_rule_version + category_level2_code + product_keyword + effective_start_date
```

算法使用：

| 算法 | 使用方式 |
|---|---|
| 算法 07 | 解析外部商品时判断是否缺少关键属性，缺失则进入待复核或观察池 |
| 算法 08 | 生成标准候选时执行必填属性校验，缺失则不进入正式候选快照 |

## 2. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 特殊规则版本 | `special_rule_version` | varchar(64) | 必须 | 导入批次生成 | 例如 `SPECIAL_ATTR_2026_V1` |
| 一级分类名称 | `category_level1_name` | varchar(128) | 建议 | Excel 分类 | 内部大类名称 |
| 二级分类编码 | `category_level2_code` | varchar(64) | 建议 | `dim_sku` 映射 | 内部中类编码 |
| 二级分类名称 | `category_level2_name` | varchar(128) | 必须 | Excel 分类 | 内部中类名称 |
| 三级分类编码 | `category_level3_code` | varchar(64) | 建议 | `dim_sku` 映射 | 内部小分类编码 |
| 三级分类名称 | `category_level3_name` | varchar(128) | 建议 | Excel 或 `dim_sku` 映射 | 内部小分类名称 |
| 商品关键词 | `product_keyword` | varchar(128) | 必须 | Excel 特殊物种或关键词 | 触发特殊规则的商品词，例如蓝莓、大闸蟹 |
| 必填属性列表 | `required_attributes` | varchar(1024) | 必须 | Excel 必填规则 | 例如果径、等级、单只重量、只数 |
| 命名规则说明 | `name_rule` | varchar(1024) | 建议 | Excel 命名规则 | 特殊商品名称中这些属性怎么出现 |
| 缺失处理动作 | `missing_action` | varchar(64) | 必须 | 导入规则 | `REQUIRE_REVIEW`、`DO_NOT_CREATE_FORMAL_CANDIDATE`、`ALLOW_AS_OBSERVATION` |
| 样本数量 | `sample_count` | int | 建议 | Excel 统计 | 支撑该规则的样本数量 |
| 需复核样例数量 | `review_sample_count` | int | 建议 | Excel 需复核样例数 | 该特殊规则下需要人工复核的样例数量 |
| 正例 | `positive_examples` | varchar(2048) | 建议 | Excel 示例 | 符合规则的名称示例 |
| 反例 | `negative_examples` | varchar(2048) | 建议 | Excel 示例 | 不符合规则的名称示例 |
| 规则状态 | `rule_status` | varchar(32) | 必须 | 导入规则 | `ACTIVE`、`REVIEW_REQUIRED`、`DISABLED` |
| 生效开始日期 | `effective_start_date` | date | 必须 | 导入规则 | 规则开始生效日期 |
| 生效结束日期 | `effective_end_date` | date | 建议 | 导入规则 | 当前有效规则可为空 |
| 是否当前有效 | `is_active` | tinyint | 必须 | 导入规则 | 1 表示当前有效 |
| 来源文件 | `source_file` | varchar(256) | 必须 | 导入元数据 | 来源 Excel 文件名 |
| 来源 sheet | `source_sheet` | varchar(128) | 必须 | 导入元数据 | 来源 sheet 名 |
| 数据更新时间 | `updated_at` | datetime | 必须 | 入库时间 | 数据导入或更新时间 |

## 3. 示例数据

| `special_rule_version` | `category_level2_name` | `product_keyword` | `required_attributes` | `missing_action` | `review_sample_count` | `rule_status` |
|---|---|---|---|---|---:|---|
| `SPECIAL_ATTR_2026_V1` | 水果类 | 蓝莓 | 果径,规格 | `DO_NOT_CREATE_FORMAL_CANDIDATE` | 0 | `ACTIVE` |
| `SPECIAL_ATTR_2026_V1` | 水产类 | 大闸蟹 | 公母,单只重量,只数 | `DO_NOT_CREATE_FORMAL_CANDIDATE` | 2 | `ACTIVE` |

## 4. 数据质量要求

```text
1. product_keyword 不能为空，且同一规则版本下不能出现互相冲突的必填规则。
2. required_attributes 必须能映射到候选属性字典中的标准属性维度。
3. 缺失必填属性的候选只能进入观察或复核，不得进入算法 08 正式候选快照。
4. 该表只处理特殊必填属性，不处理价格、毛利或购物篮关联强度。
```

## 5. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `missing_action` | 缺失处理动作 | `REQUIRE_REVIEW` | 要求复核 | 缺少必填属性时进入人工复核 |
| `missing_action` | 缺失处理动作 | `DO_NOT_CREATE_FORMAL_CANDIDATE` | 不生成正式候选 | 缺少必填属性时不得进入算法 08 正式候选快照 |
| `missing_action` | 缺失处理动作 | `ALLOW_AS_OBSERVATION` | 仅观察 | 缺少必填属性时只进入观察池或证据池 |
| `rule_status` | 规则状态 | `ACTIVE` | 生效 | 规则已确认，算法可正式读取 |
| `rule_status` | 规则状态 | `REVIEW_REQUIRED` | 需复核 | 特殊品类必填属性仍需人工确认 |
| `rule_status` | 规则状态 | `DISABLED` | 停用 | 规则历史保留，不参与当前算法 |
| `is_active` | 是否当前有效 | `1` | 当前有效 | 当前算法周期可读取 |
| `is_active` | 是否当前有效 | `0` | 历史无效 | 被新版本或新生效周期替代 |

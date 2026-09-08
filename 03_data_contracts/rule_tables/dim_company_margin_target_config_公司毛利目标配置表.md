# 公司毛利目标配置表

目标表建议名：`dim_company_margin_target_config`

表用途：沉淀公司、区域、品类维度的毛利底线和目标毛利，供算法 05 计算候选商品建议价、成本谈判上限和开发动作，供算法 08 判断候选是否具备完整价格可行性结果。

来源文件：`B1—公司最低毛利率和目标毛利率是多少—2026年集团区毛利目标.xlsx`

来源 sheet：`各个区域毛利额-V2`

## 1. 表规则

表粒度：

```text
一行 = 一个配置版本 + 一个适用范围 + 一个品类 + 一个生效周期
```

主键建议：

```text
margin_config_version + scope_type + scope_id + category_level + category_code + effective_start_date
```

算法使用：

| 算法 | 使用方式 |
|---|---|
| 算法 05 | 与数据毛利底线、数据目标毛利取更严值，生成 `final_margin_floor`、`final_margin_target` |
| 算法 08 | 透传算法 05 的毛利结果和价格可行状态，不重复计算毛利 |

## 2. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 毛利配置版本 | `margin_config_version` | varchar(64) | 必须 | 导入批次生成 | 例如 `MARGIN_2026_V1`，用于追溯配置版本 |
| 适用范围类型 | `scope_type` | varchar(32) | 必须 | 导入规则 | `NATIONAL`、`REGION`、`CITY_GROUP`、`CITY` |
| 适用范围编码 | `scope_id` | varchar(64) | 必须 | Excel 区域字段映射 | 范围唯一编码，例如 `HD` 表示华东区 |
| 适用范围名称 | `scope_name` | varchar(128) | 必须 | Excel 区域字段 | 例如全国、华东区、长沙区 |
| 品类层级 | `category_level` | varchar(32) | 必须 | 导入规则 | `ALL`、`CATEGORY_LEVEL1`、`CATEGORY_LEVEL2`、`CATEGORY_LEVEL3` |
| 品类编码 | `category_code` | varchar(64) | 条件必须 | `dim_sku` 或导入映射 | 全品类可写 `ALL`，具体品类需能与商品基础表品类编码对齐 |
| 品类名称 | `category_name` | varchar(128) | 必须 | Excel 品类列名 | 例如全品类、蔬菜类、水果类、预制菜 |
| 公司毛利底线 | `company_margin_floor` | decimal(18,8) | 必须 | Excel 供应链毛利率下限或品类毛利 | 最低可接受毛利率，低于该值不建议开发 |
| 公司目标毛利 | `company_margin_target` | decimal(18,8) | 必须 | Excel 供应链毛利率上限或品类毛利 | 理想目标毛利率，用于判断是否可进入开发 |
| 总销售额 | `total_sales_amt` | decimal(18,6) | 建议 | Excel 总销售额 | 来源测算用总销售额，用于审计配置来源 |
| 销售额占比 | `sales_share_rate` | decimal(18,8) | 建议 | Excel 销售额占比 | 该品类在适用范围内的销售额占比 |
| 出库额 | `outbound_amt` | decimal(18,6) | 建议 | Excel 出库额 | 来源测算用出库额 |
| 供应链毛利额 | `supply_chain_margin_amt` | decimal(18,6) | 建议 | Excel 供应链毛利额 | 来源测算用毛利额 |
| 备注要求 | `remark_requirement` | varchar(1024) | 建议 | Excel 备注要求 | 例如区域可调整、总额不能变等业务备注 |
| 生效开始日期 | `effective_start_date` | date | 必须 | 导入规则 | 配置开始生效日期 |
| 生效结束日期 | `effective_end_date` | date | 建议 | 导入规则 | 当前有效配置可为空 |
| 是否当前有效 | `is_active` | tinyint | 必须 | 导入规则 | 1 表示当前有效，0 表示历史配置 |
| 来源文件 | `source_file` | varchar(256) | 必须 | 导入元数据 | 来源 Excel 文件名 |
| 来源 sheet | `source_sheet` | varchar(128) | 必须 | 导入元数据 | 来源 Excel sheet 名 |
| 配置确认人 | `confirmed_by` | varchar(128) | 建议 | 项目维护 | 业务、财务或采购确认人 |
| 配置确认日期 | `confirmed_date` | date | 建议 | 项目维护 | 配置确认日期 |
| 数据更新时间 | `updated_at` | datetime | 必须 | 入库时间 | 数据导入或更新时间 |

## 3. 示例数据

| `margin_config_version` | `scope_name` | `category_level` | `category_name` | `company_margin_floor` | `company_margin_target` | `effective_start_date` | `is_active` |
|---|---|---|---|---:|---:|---|---:|
| `MARGIN_2026_V1` | 华东区 | `ALL` | 全品类 | 0.08900000 | 0.09500000 | 2026-01-01 | 1 |
| `MARGIN_2026_V1` | 华东区 | `CATEGORY_LEVEL1` | 蔬菜类 | 0.09056716 | 0.09056716 | 2026-01-01 | 1 |
| `MARGIN_2026_V1` | 华东区 | `CATEGORY_LEVEL1` | 预制菜 | 0.14445517 | 0.14445517 | 2026-01-01 | 1 |

## 4. 数据质量要求

```text
1. 同一配置版本、同一范围、同一品类、同一生效日期只能有一条有效记录。
2. company_margin_floor 和 company_margin_target 必须在 0 到 1 之间。
3. company_margin_target 不得低于 company_margin_floor。
4. 具体品类名称必须能与商品基础表的品类口径建立映射。
5. 历史配置不得覆盖，必须用生效开始日期和生效结束日期保留版本。
```

## 5. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `scope_type` | 适用范围类型 | `NATIONAL` | 全国 | 配置适用于全国统一口径 |
| `scope_type` | 适用范围类型 | `REGION` | 区域 | 配置适用于指定业务区域 |
| `scope_type` | 适用范围类型 | `CITY_GROUP` | 城市组 | 配置适用于指定城市组合 |
| `scope_type` | 适用范围类型 | `CITY` | 城市 | 配置适用于单个城市 |
| `category_level` | 品类层级 | `ALL` | 全品类 | 配置适用于全部品类 |
| `category_level` | 品类层级 | `CATEGORY_LEVEL1` | 一级分类 | 配置适用于内部一级分类 |
| `category_level` | 品类层级 | `CATEGORY_LEVEL2` | 二级分类 | 配置适用于内部二级分类 |
| `category_level` | 品类层级 | `CATEGORY_LEVEL3` | 三级分类 | 配置适用于内部三级分类 |
| `is_active` | 是否当前有效 | `1` | 当前有效 | 当前算法周期可读取 |
| `is_active` | 是否当前有效 | `0` | 历史无效 | 被新版本或新生效周期替代 |

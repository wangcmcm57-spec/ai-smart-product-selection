# 价格点规则配置表

目标表建议名：`dim_price_point_rule_config`

表用途：沉淀算法 05 使用的品类价格尾数和价格点生成规则。算法 05 根据消费者价格带上下限、品类尾数和 1 元步长生成可执行价格点。

来源：用户已确认 V1 价格点规则。

## 1. 表规则

表粒度：

```text
一行 = 一个价格规则版本 + 一个适用品类 + 一个计价单位 + 一个生效周期
```

主键建议：

```text
price_rule_version + category_level + category_code + unit + effective_start_date
```

算法使用：

| 算法 | 使用方式 |
|---|---|
| 算法 05 | 生成 `price_ladder_json`，在价格带、毛利约束和可执行价格点交集中选择建议零售价 |
| 算法 08 | 读取算法 05 的价格可行性结果，不直接重算价格点 |

## 2. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 价格规则版本 | `price_rule_version` | varchar(64) | 必须 | 项目配置 | 例如 `PRICE_POINT_2026_V1` |
| 品类层级 | `category_level` | varchar(32) | 必须 | 配置维护 | `CATEGORY_LEVEL1`、`CATEGORY_LEVEL2`、`CATEGORY_LEVEL3` |
| 品类编码 | `category_code` | varchar(64) | 建议 | `dim_sku` 映射 | 品类编码；暂无编码时可先按品类名称映射 |
| 品类名称 | `category_name` | varchar(128) | 必须 | 用户确认 | 蔬菜、水果、猪肉、肉禽蛋、冷藏加工、预制菜 |
| 计价单位 | `unit` | varchar(32) | 必须 | 用户确认 | kg、份、个、份/个等 |
| 价格尾数 | `price_tail` | decimal(8,2) | 必须 | 用户确认 | 例如 0.98、0.90 |
| 价格点步长 | `price_step_amt` | decimal(8,2) | 必须 | 用户确认 | V1 默认 1.00，表示每 1 元一个价格点 |
| 价格上下限来源 | `price_bound_source` | varchar(64) | 必须 | 用户确认 | V1 固定为 `CONSUMER_PRICE_BAND` |
| 是否允许扩展价格带 | `allow_extended_band_flag` | tinyint | 必须 | 算法 05 口径 | 1 表示可在谨慎试点场景使用扩展价格带 |
| 生效开始日期 | `effective_start_date` | date | 必须 | 配置维护 | 规则开始生效日期 |
| 生效结束日期 | `effective_end_date` | date | 建议 | 配置维护 | 当前有效规则可为空 |
| 是否当前有效 | `is_active` | tinyint | 必须 | 配置维护 | 1 表示当前有效 |
| 来源文件 | `source_file` | varchar(256) | 建议 | 项目维护 | 用户直接确认时可写 `USER_CONFIRMED` |
| 来源 sheet | `source_sheet` | varchar(128) | 建议 | 项目维护 | 用户直接确认时可为空 |
| 配置确认人 | `confirmed_by` | varchar(128) | 建议 | 项目维护 | 业务或采购确认人 |
| 配置确认日期 | `confirmed_date` | date | 建议 | 项目维护 | 确认日期 |
| 数据更新时间 | `updated_at` | datetime | 必须 | 入库时间 | 数据导入或更新时间 |

## 3. 示例数据

| `price_rule_version` | `category_name` | `unit` | `price_tail` | `price_step_amt` | `price_bound_source` | `is_active` |
|---|---|---|---:|---:|---|---:|
| `PRICE_POINT_2026_V1` | 蔬菜 | kg | 0.98 | 1.00 | `CONSUMER_PRICE_BAND` | 1 |
| `PRICE_POINT_2026_V1` | 水果 | kg | 0.98 | 1.00 | `CONSUMER_PRICE_BAND` | 1 |
| `PRICE_POINT_2026_V1` | 预制菜 | 份/个 | 0.90 | 1.00 | `CONSUMER_PRICE_BAND` | 1 |

## 4. 价格点生成规则

```text
price_ladder_json
= { P | P = integer_yuan + price_tail
        AND price_band_lower <= P <= price_band_upper }

integer_yuan 按 price_step_amt 枚举。
price_band_lower / price_band_upper 来自算法 05 的消费者核心价格带或扩展价格带。
```

## 5. 数据质量要求

```text
1. price_tail 必须大于等于 0 且小于 1。
2. price_step_amt 必须大于 0，V1 固定为 1.00。
3. 同一版本、同一品类、同一单位只能有一条当前有效规则。
4. 如果商品单位与规则单位无法匹配，算法 05 必须输出价格点规则缺失状态，不能自行猜尾数。
```

## 6. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `category_level` | 品类层级 | `ALL` | 全品类 | 规则适用于全部品类 |
| `category_level` | 品类层级 | `CATEGORY_LEVEL1` | 一级分类 | 规则适用于内部一级分类 |
| `category_level` | 品类层级 | `CATEGORY_LEVEL2` | 二级分类 | 规则适用于内部二级分类 |
| `category_level` | 品类层级 | `CATEGORY_LEVEL3` | 三级分类 | 规则适用于内部三级分类 |
| `price_bound_source` | 价格上下限来源 | `CONSUMER_PRICE_BAND` | 消费者价格带 | 价格点上下限来自算法 05 的消费者核心价格带或扩展价格带 |
| `allow_extended_band_flag` | 是否允许扩展价格带 | `1` | 允许扩展 | 谨慎试点场景可使用扩展价格带 |
| `allow_extended_band_flag` | 是否允许扩展价格带 | `0` | 不允许扩展 | 只能在核心价格带内生成价格点 |
| `is_active` | 是否当前有效 | `1` | 当前有效 | 当前算法周期可读取 |
| `is_active` | 是否当前有效 | `0` | 历史无效 | 被新版本或新生效周期替代 |

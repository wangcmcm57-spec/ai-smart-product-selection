# 商品基础表

目标表建议名：`dim_sku`

表用途：提供商品维度基础信息，用于品类归属、规格换算、SPU 归并、商品属性分析和算法结果解释。

一行代表：一个商品 / 销售条码。

主键：`sku_id`。

关联要求：交易商品编码必须能和 Doris 小票商品明细表里的 `article_id` 对齐。

## 1. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 交易商品编码 | `sku_id` | varchar(64) | 必须 | `data_db.dim_sku.article_id` | 销售商品编码，必须和小票表 `article_id` 对齐 |
| 商品编码 | `product_id` | varchar(64) | 建议 | `data_db.dim_sku.article_id` 或商品主数据编码 | 商品主数据编码；如果和交易商品编码一致可重复保留 |
| 商品名称 | `sku_name` | varchar(256) | 必须 | `data_db.dim_sku.article_name` | 商品展示名称 |
| 大类编码 | `category_level1_code` | varchar(64) | 必须 | `data_db.dim_sku.category_level1_id` | 商品大类编码 |
| 大类名称 | `category_level1_name` | varchar(128) | 必须 | `data_db.dim_sku.category_level1_description` | 商品大类名称 |
| 中类编码 | `category_level2_code` | varchar(64) | 必须 | `data_db.dim_sku.category_level2_id` | 商品中类编码 |
| 中类名称 | `category_level2_name` | varchar(128) | 必须 | `data_db.dim_sku.category_level2_description` | 商品中类名称 |
| 小类编码 | `category_level3_code` | varchar(64) | 必须 | `data_db.dim_sku.category_level3_id` | 商品小类编码 |
| 小类名称 | `category_level3_name` | varchar(128) | 必须 | `data_db.dim_sku.category_level3_description` | 商品小类名称，门店品类等级核心字段 |
| SPU 编码 | `spu_id` | varchar(64) | 建议 | `data_db.dim_sku.spu_id` | 商品归并用 SPU 编码 |
| SPU 名称 | `spu_name` | varchar(256) | 建议 | `data_db.dim_sku.spu_name` | 商品归并用 SPU 名称 |
| 规格 | `specification` | varchar(128) | 建议 | `data_db.dim_sku.norms` | 商品规格，例如 `250g`、`1kg`、称重 |
| 销售单位 | `sale_unit` | varchar(32) | 必须 | `data_db.dim_sku.sale_unit` | 销售单位，例如份、千克 |
| 单位重量 | `unit_weight_kg` | decimal(18,6) | 建议 | `data_db.dim_sku.unit_weight` 或规格解析 | 单个销售单位折算重量，建议单位 kg |
| 品牌 | `brand_name` | varchar(128) | 建议 | `data_db.dim_sku.brand` | 商品品牌；没有可为空 |
| 产地 | `origin_place` | varchar(128) | 建议 | `data_db.dim_sku.product_address` | 商品产地；没有可为空 |
| 存储条件 | `storage_condition` | varchar(64) | 建议 | `data_db.dim_sku.sp_info_name` 或 `data_db.dim_sku.sp_info` | 冷藏、冷冻、常温等损耗风险辅助字段 |
| 温层 | `temperature_layer` | varchar(64) | 建议 | `data_db.dim_sku.temperature_layer_name` | 冷藏、冷冻、热鲜等温层口径 |
| 保质天数 | `shelf_life_days` | int | 建议 | `data_db.dim_sku.abi_quality_days` | 商品保质天数 |
| 是否标品 | `is_standard_product` | tinyint | 建议 | 开发补充字段或映射规则 | `1` 表示标品，`0` 表示非标品；不能仅用称重标识直接替代 |
| 是否自加工商品 | `is_self_processed` | tinyint | 建议 | 开发补充字段或映射规则 | `1` 表示自加工商品，`0` 表示非自加工商品 |
| 数据更新时间 | `data_update_time` | datetime | 必须 | `data_db.dim_sku.update_time`、`load_time`、`etl_time` 或分区日期 | 数据同步或更新时间 |

## 2. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `is_standard_product` | 是否标品 | `1` | 标品 | 商品主数据或开发确认映射规则判定为标品 |
| `is_standard_product` | 是否标品 | `0` | 非标品 | 商品主数据或开发确认映射规则判定为非标品 |
| `is_standard_product` | 是否标品 | 空 | 暂无法判断 | V1 暂无直接字段且映射规则未确认 |
| `is_self_processed` | 是否自加工商品 | `1` | 自加工商品 | 商品主数据或开发确认映射规则判定为自加工 |
| `is_self_processed` | 是否自加工商品 | `0` | 非自加工商品 | 商品主数据或开发确认映射规则判定为非自加工 |
| `is_self_processed` | 是否自加工商品 | 空 | 暂无法判断 | V1 暂无直接字段且映射规则未确认 |

## 3. 缺失和降级写法

```text
1. `sku_id`、`sku_name`、一级到三级品类编码和名称、`sale_unit` 不能为空。
2. `unit_weight_kg` 无法稳定解析时可为空，但开发需说明无法解析原因，算法不得跨单位直接相加。
3. `is_standard_product`、`is_self_processed` 如果 V1 暂无可靠来源，可以为空；不能用名称关键词自行猜测。
4. SPU、品牌、产地、存储条件、温层、保质期没有来源时可为空，但不能影响商品主键唯一性。
```

## 4. 统一批次分类读取约定（不新增分类快照）

算法 01、02、03 在同一 `algorithm_batch_version = BATCH_YYYYMM` 下，复用已有长期留存、只追加的商品数据。V1 对该批全部交易使用同一套分类，不按交易日期还原期内改类。既不新增分类快照表，也不复制一份商品数据。

### 4.1 首次读取前绑定

全链路调度在算法 01、02 中最先读取分类的任务启动前，将以下 `category_read_binding_json` 绑定到统一批次，保存在平台已有批次配置/不可变调度审计中；不是新增运行参数表。算法 02 首次发布时，将同一对象原样写入现有 `run_config_snapshot_json`，算法 03 读取该对象并与共用绑定核对。

| JSON 键 | 类型 | 内容及约束 |
|---|---|---|
| `source_locator` | string | 可长期重读的实际库表、已留存文件位置或数据集读取位置；不能只写“当前商品表” |
| `read_boundary` | string | 确定的文件成员/分区及追加数据截止边界；按实际源粒度填写，禁止动态“最新”条件；若旧分区也会追加，必须包含能排除后加记录的留存批次或入库边界 |
| `read_query_ref` | string | 不可变读取 SQL/ETL 引用，包含源字段到本合同字段的映射、边界过滤和一 SKU 一行规则；不得引用可随时覆盖的脚本 |
| `bound_at` | datetime string | 本批首次绑定时间，必须早于最先读取分类的算法任务 |

同批绑定唯一且不可变。上述字段是来源定位信息，不是第二个业务版本号。若追加数据没有可区分的入库边界，应引用已经留存且不会覆盖的固定文件/数据集；不能用单行 `data_update_time` 猜测旧分类。

### 4.2 读取、补数和历史重跑

1. 每次按原绑定读取，验证 `sku_id` 唯一及各级品类映射唯一，再关联交易/可售记录。源数据重复冲突不能按当前更新时间任取分类。
2. `source_data_version` 只追踪本次实际运行输入，补数重跑可以更新；它不能替代或修改 `category_read_binding_json`。同批重跑也不得自动读入后加的分类记录。新增交易 SKU 无法关联原绑定时进入质量问题，不在旧批次自动扩充分类。
3. 下一完整月建立该新批次的绑定，可以包含新追加的数据；这不改变历史批次。
4. 已发布历史批次若没有原绑定记录，先核实当时使用的原文件/分区及读取规则，可定位原内容后在公共审计补充来源证明，不改写原业务规则或原配置。无法定位原内容时，标记历史重跑阻断；不能拿今天的 `dim_sku` 补造旧分类并声称复现。
5. 01、02、03 的运行审计必须证明读取同一绑定。02/03 卡引用本节；不要求改写算法 01 的画像公式、参数或结果表。

验收至少覆盖：追加新月份后旧批读取不变、仅补交易时分类不变、01/02/03 读取结果一致、原始分类无法重读时阻断历史重跑。本文定义读取合同，不把合同补齐等同于真实批次验收通过。

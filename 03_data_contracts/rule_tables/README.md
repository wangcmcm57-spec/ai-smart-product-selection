# 规则配置表数据合同

本目录存放 AI 选品 V1 需要沉淀的规则表、配置表、人工复核辅助表，以及业务后续按标准 Excel 提供数据的说明。

生产算法不能直接读取 Excel。当前正确链路是：

```text
首版：业务不标准 Excel
-> 项目侧转换为标准 Excel + 标准 CSV
-> 数据开发优先读取标准 CSV 落 Doris
-> 发布为带版本、生效日期和状态的规则配置表
-> 算法读取 Doris 规则表
-> 算法结果记录使用的规则版本

后续：业务按标准 Excel 模板提供更新
-> 项目侧或数据侧校验字段、主键、版本、生效日期和状态枚举
-> 导出标准 CSV
-> 数据开发读取标准 CSV 落 Doris
-> 算法读取 Doris 规则表
```

完整模块边界、处理流程、验收规则见：

```text
业务规则Excel落表模块_开发说明.md
```

## 1. 表分类

| 类型 | 说明 |
|---|---|
| 规则配置表 | 算法直接读取，用于计算、过滤、命名、映射或风险识别 |
| 规则依据表 | 算法通过规则编码引用，用于解释、审计和人工复核 |
| 复核辅助表 | 不直接决定算法结果，用于保存待复核样例、审核记录和观察池 |

## 2. V1 规则配置表

开发落表阅读顺序建议：

```text
1. 先读当前标准导入包清单：`import_ready/2026-08-18/manifest.md`
2. 再按 csv/ 下的标准 CSV 和本目录标准表合同落 Doris
3. 只有追溯首版转换、重跑标准包或处理非标准 Excel 时，才读 import_specs/
```

| 表合同 | 目标表建议名 | 是否 V1 必做 | 首版来源 |
|---|---|---|---|
| [公司毛利目标配置表](dim_company_margin_target_config_公司毛利目标配置表.md) | `dim_company_margin_target_config` | 必做 | B1 毛利目标 Excel |
| [价格点规则配置表](dim_price_point_rule_config_价格点规则配置表.md) | `dim_price_point_rule_config` | 必做 | 用户确认的价格尾数规则 |
| [购物篮属性转化规则表](dim_basket_attribute_transfer_rule_购物篮属性转化规则表.md) | `dim_basket_attribute_transfer_rule` | 必做 | B4 购物篮转新品属性 Excel |
| [竞对分类映射规则表](dim_competitor_category_mapping_rule_竞对分类映射规则表.md) | `dim_competitor_category_mapping_rule` | 必做 | B3 竞对命名规则 Excel |
| [商品命名规则表](dim_product_naming_rule_商品命名规则表.md) | `dim_product_naming_rule` | 必做 | B3 竞对命名规则 Excel |
| [特殊品类必填属性规则表](dim_special_product_required_attribute_rule_特殊品类必填属性规则表.md) | `dim_special_product_required_attribute_rule` | 必做 | B3 竞对命名规则 Excel |
| [候选属性字典表](dim_candidate_attribute_dictionary_候选属性字典表.md) | `dim_candidate_attribute_dictionary` | 必做 | B3 + 系统自动生成 |
| [命名合规词规则表](dim_naming_compliance_term_rule_命名合规词规则表.md) | `dim_naming_compliance_term_rule` | 必做 | 生鲜与食品商品命名合规词库 |
| [分类命名合规规则表](dim_category_naming_compliance_rule_分类命名合规规则表.md) | `dim_category_naming_compliance_rule` | 必做 | 生鲜与食品商品命名合规词库 |
| [法规依据表](dim_regulation_reference_法规依据表.md) | `dim_regulation_reference` | 必做 | 生鲜与食品商品命名合规词库 |

## 3. V1 复核辅助表

| 表合同 | 目标表建议名 | 是否 V1 必做 | 来源 |
|---|---|---|---|
| [规则复核样例与人工复核表](fact_rule_review_item_规则复核样例与人工复核表.md) | `fact_rule_review_item` | 建议 | B3 需复核样例、合规词库审核工作台 |

## 4. 导入映射说明

`import_specs/` 需要保留，但它的用途是首版不标准 Excel 的迁移审计、转换规则和问题追溯，不是后续业务的日常填报入口。

后续业务按标准 Excel 提供数据时，优先看：

```text
业务后续标准Excel提供清单.md
```

| 导入说明 | 解决什么问题 |
|---|---|
| [导入映射总说明](import_specs/README.md) | 说明业务补充材料如何转成标准规则表 |
| [B1 公司毛利目标导入映射说明](import_specs/B1_公司毛利目标_导入映射说明.md) | 指定毛利目标 Excel 如何横表转长表 |
| [用户确认价格点规则导入映射说明](import_specs/用户确认_价格点规则_导入映射说明.md) | 指定价格尾数、价格步长和价格带来源 |
| [B4 购物篮属性转化规则导入映射说明](import_specs/B4_购物篮属性转化规则_导入映射说明.md) | 指定购物篮矩阵如何拆成 A/B 属性转化规则 |
| [B3 命名分类属性规则导入映射说明](import_specs/B3_命名分类属性规则_导入映射说明.md) | 指定命名、分类映射、特殊必填和复核样例如何落表 |
| [合规词库导入映射说明](import_specs/合规词库_导入映射说明.md) | 指定合规词、分类命名合规、法规依据和审核工作台如何落表 |
| [商品季节状态历史导入说明](import_specs/商品季节状态_历史导入说明.md) | 仅保留历史口径说明；当前商品状态已调整为 SAP POP 来源的基础表 `dim_product_status`，由数据开发从 SAP POP 平台提供 |

## 5. 统一版本规则

所有规则配置表必须包含：

```text
规则版本
生效开始日期
生效结束日期
是否当前有效
来源文件
来源 sheet
数据更新时间
```

同一个算法周期内，算法结果必须记录使用的规则版本，不能只记录算法版本。

## 6. 不进入生产算法的内容

以下内容不作为算法运行时直接输入：

| 内容 | 处理方式 |
|---|---|
| Excel 文件本身 | 只作为导入来源和审计留痕 |
| B3 需复核样例 | 进入 `fact_rule_review_item` 或人工复核队列 |
| 合规词库审核工作台 | 进入 `fact_rule_review_item` 或质量审核流程 |
| B4 Sheet1 上海商品清单 | 只作规则校验参考，不替代 `dim_sku` |

## 7. 后续业务标准 Excel

后续业务不再按 B1、B3、B4 的原始格式补充数据，而是按标准 Excel sheet 提供或更新规则数据。

标准 sheet、目标表、提供方和当前缺口见：

```text
业务后续标准Excel提供清单.md
```

商品状态不再作为规则 Excel sheet 维护。当前按基础表 [商品状态表](../base_tables/dim_product_status_商品状态表.md) 交付，由数据开发从 SAP POP 平台按区域、商品名称、商品编码和商品状态提供。

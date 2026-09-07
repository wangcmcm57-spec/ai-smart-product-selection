# 规则复核样例与人工复核表

目标表建议名：`fact_rule_review_item`

表用途：保存需要人工复核的样例、异常、观察池词语、命名争议、分类映射争议和合规审核记录。该表是复核辅助表，不直接决定算法结果；只有复核后沉淀到规则配置表的结果，才能被正式算法读取。

来源文件：

```text
B3-按竞对商品名称梳理的命名规则.xlsx
生鲜与食品商品命名合规词库_2026-08-18.xlsx
```

来源 sheet：

```text
B3：需复核样例
合规词库：审核工作台
```

## 1. 表规则

表粒度：

```text
一行 = 一个复核批次中的一个待复核对象
```

主键建议：

```text
review_item_id
```

算法使用：

| 算法 | 使用方式 |
|---|---|
| 算法 07 | 无法稳定分类、无法稳定识别属性或命中风险词时写入复核项 |
| 算法 08 | 标准化候选缺必填属性、命名异常或合规待审时写入复核项 |
| 算法 09 | 风险门禁需要人工材料或人工判断时写入复核项 |

## 2. 字段清单

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 复核项 ID | `review_item_id` | varchar(64) | 必须 | 系统生成 | 每条待复核记录唯一 ID |
| 复核批次 ID | `review_batch_id` | varchar(64) | 必须 | 系统生成 | 同一次导入、同一次算法运行或同一次人工复核批次 |
| 复核来源类型 | `review_source_type` | varchar(64) | 必须 | 系统生成 | `NAMING_SAMPLE`、`CATEGORY_MAPPING`、`ATTRIBUTE_MAPPING`、`COMPLIANCE_AUDIT`、`ALGORITHM_EXCEPTION` |
| 来源文件 | `source_file` | varchar(256) | 建议 | 导入元数据 | 来源 Excel 文件名或算法任务名 |
| 来源 sheet | `source_sheet` | varchar(128) | 建议 | 导入元数据 | 来源 sheet 名 |
| 来源行号 | `source_row_no` | int | 建议 | 导入元数据 | Excel 来源行号，便于追溯 |
| 原始来源名称 | `raw_source_name` | varchar(128) | 建议 | 外部源或 Excel | 例如久谦、盒马、审核工作台 |
| 竞对菜品类型 | `competitor_dish_type` | varchar(128) | 建议 | B3 需复核样例 | 竞对侧菜品类型 |
| 竞对商品类型 | `competitor_product_type` | varchar(128) | 建议 | B3 需复核样例 | 竞对侧商品类型 |
| 原始商品名称 | `raw_product_name` | varchar(512) | 建议 | 外部源或 Excel | 需要复核的商品名、候选名或样例名 |
| 净重 | `net_weight` | varchar(128) | 建议 | B3 需复核样例 | 原始净重或规格文字，保留原样 |
| 销售单位 | `sales_unit` | varchar(64) | 建议 | B3 需复核样例 | 原始销售单位 |
| 原始分类路径 | `raw_category_path` | varchar(512) | 建议 | 外部源或 Excel | 外部或原始分类路径 |
| 公司大类 | `company_category_level1_name` | varchar(128) | 建议 | B3 需复核样例 | 复核样例中的公司大类 |
| 公司中类 | `company_category_level2_name` | varchar(128) | 建议 | B3 需复核样例 | 复核样例中的公司中类 |
| 建议内部分类 | `suggested_internal_category` | varchar(256) | 建议 | 系统识别 | 系统建议映射到的内部分类 |
| 中类归类依据 | `category_mapping_basis` | varchar(1024) | 建议 | B3 需复核样例 | Excel 中类归类依据或系统映射依据 |
| 识别主体商品 | `identified_subject` | varchar(256) | 建议 | 系统识别 | 系统识别出的主体商品 |
| 识别物种或品名 | `identified_species_or_product_name` | varchar(256) | 建议 | B3 需复核样例 | Excel 中识别出的物种或品名 |
| 提取规格 | `extracted_spec` | varchar(128) | 建议 | 系统识别 | 系统从名称中提取出的规格 |
| 规格或净含量摘录 | `spec_content_excerpt` | varchar(256) | 建议 | B3 需复核样例 | 原始名称里提取的规格或净含量片段 |
| 等级摘录 | `grade_excerpt` | varchar(256) | 建议 | B3 需复核样例 | 原始名称里提取的等级片段 |
| 果径或果规摘录 | `fruit_size_excerpt` | varchar(256) | 建议 | B3 需复核样例 | 原始名称里提取的果径或果规片段 |
| 个头大小摘录 | `size_level_excerpt` | varchar(256) | 建议 | B3 需复核样例 | 原始名称里提取的个头大小片段 |
| 温层或状态摘录 | `temperature_status_excerpt` | varchar(256) | 建议 | B3 需复核样例 | 原始名称里提取的温层或状态片段 |
| 处理形态摘录 | `processing_form_excerpt` | varchar(256) | 建议 | B3 需复核样例 | 原始名称里提取的处理形态片段 |
| 中类规则提示 | `category_rule_hint` | varchar(1024) | 建议 | B3 需复核样例 | B3 给出的中类规则提示 |
| 拟用完整名称 | `proposed_full_name` | varchar(512) | 建议 | 合规词库审核工作台 | 人工审核时拟使用的完整商品名 |
| 触发词或词库编号 | `triggered_term_code` | varchar(128) | 建议 | 合规词库审核工作台 | 命中的合规词或词库编号 |
| 证据材料编号或链接 | `evidence_material_ref` | varchar(1024) | 建议 | 合规词库审核工作台 | 人工审核使用的证明材料编号或链接 |
| 系统放行结论 | `system_release_conclusion` | varchar(256) | 建议 | 合规词库审核工作台或算法生成 | 系统根据规则给出的初步放行结论 |
| 缺失或异常原因 | `missing_reason` | varchar(1024) | 必须 | 系统生成 | 为什么需要人工复核 |
| 触发规则 ID | `triggered_rule_id` | varchar(128) | 建议 | 规则表关联 | 触发的命名、属性、合规或分类规则 ID |
| 复核优先级 | `review_priority` | varchar(32) | 必须 | 系统生成 | `P0`、`P1`、`P2`、`P3` |
| 复核状态 | `review_status` | varchar(32) | 必须 | 人工或系统维护 | `PENDING`、`APPROVED`、`REJECTED`、`NEED_MORE_INFO`、`CLOSED` |
| 复核结论 | `review_result` | varchar(1024) | 建议 | 人工维护 | 人工确认后的结论 |
| 复核人 | `reviewer` | varchar(128) | 建议 | 人工维护 | 业务、商品、质量或法务复核人 |
| 复核时间 | `reviewed_at` | datetime | 建议 | 人工维护 | 完成复核的时间 |
| 复核备注 | `review_comment` | varchar(2048) | 建议 | 人工维护 | 复核补充说明 |
| 创建时间 | `created_at` | datetime | 必须 | 系统生成 | 复核项创建时间 |
| 数据更新时间 | `updated_at` | datetime | 必须 | 系统生成 | 复核项更新时间 |

## 3. 示例数据

| `review_item_id` | `review_source_type` | `raw_product_name` | `missing_reason` | `review_priority` | `review_status` |
|---|---|---|---|---|---|
| `REV_202608_0001` | `ATTRIBUTE_MAPPING` | Omega-3 鲜鸡蛋 12 枚 | 功能属性需确认是否允许进入候选名称 | `P1` | `PENDING` |
| `REV_202608_0002` | `CATEGORY_MAPPING` | 黑椒牛柳丝 200g | 外部分类和内部牛肉类映射置信度不足 | `P1` | `PENDING` |
| `REV_202608_0003` | `COMPLIANCE_AUDIT` | 低钠高蛋白鸡胸肉 | 命中需审核功能声称词 | `P0` | `PENDING` |

## 4. 数据质量要求

```text
1. fact_rule_review_item 不直接作为算法正式判断依据。
2. 人工复核通过后，必须回写到对应规则配置表或属性字典表，算法下一轮按规则版本读取。
3. P0 和 P1 复核项必须有 reviewer、review_result 和 reviewed_at 后才能关闭。
4. CLOSED 状态必须有明确结论，不能只写已处理。
```

## 5. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `review_source_type` | 复核来源类型 | `NAMING_SAMPLE` | 命名样例 | 来源于命名样例或命名结构复核 |
| `review_source_type` | 复核来源类型 | `CATEGORY_MAPPING` | 分类映射 | 来源于竞对分类或内部分类映射复核 |
| `review_source_type` | 复核来源类型 | `ATTRIBUTE_MAPPING` | 属性映射 | 来源于属性识别、属性字典或入名判断复核 |
| `review_source_type` | 复核来源类型 | `COMPLIANCE_AUDIT` | 合规审核 | 来源于命名合规词、分类命名合规或材料审核 |
| `review_source_type` | 复核来源类型 | `ALGORITHM_EXCEPTION` | 算法异常 | 来源于算法运行中的异常或无法自动判断场景 |
| `review_priority` | 复核优先级 | `P0` | 最高优先级 | 阻断正式候选、风险门禁或开发需求发布 |
| `review_priority` | 复核优先级 | `P1` | 高优先级 | 影响候选是否进入正式推荐或关键证据解释 |
| `review_priority` | 复核优先级 | `P2` | 中优先级 | 影响规则质量、展示解释或后续优化 |
| `review_priority` | 复核优先级 | `P3` | 低优先级 | 不阻断当前主链路，可排期补充 |
| `review_status` | 复核状态 | `PENDING` | 待复核 | 已生成复核项，尚未处理 |
| `review_status` | 复核状态 | `APPROVED` | 通过 | 已人工确认可用 |
| `review_status` | 复核状态 | `REJECTED` | 拒绝 | 已人工确认不可用 |
| `review_status` | 复核状态 | `NEED_MORE_INFO` | 需补充材料 | 当前材料不足，不能完成复核 |
| `review_status` | 复核状态 | `CLOSED` | 已关闭 | 复核项已有明确结论并完成回写或归档 |

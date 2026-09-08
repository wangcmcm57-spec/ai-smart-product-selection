# AI 选品规则表标准导入数据校验报告（2026-08-18）

## 1. 行数汇总

| 标准表 | 行数 | 状态分布 |
|---|---:|---|
| `dim_company_margin_target_config` | 132 | {} |
| `dim_price_point_rule_config` | 6 | {} |
| `dim_basket_attribute_transfer_rule` | 153 | {"ACTIVE": 117, "REVIEW_REQUIRED": 36} |
| `dim_product_naming_rule` | 51 | {"ACTIVE": 51} |
| `dim_special_product_required_attribute_rule` | 15 | {"ACTIVE": 15} |
| `dim_competitor_category_mapping_rule` | 6373 | {"ACTIVE": 5659, "REVIEW_REQUIRED": 714} |
| `dim_candidate_attribute_dictionary` | 2296 | {"AUTO_APPROVED": 1155, "REVIEW_REQUIRED": 986, "APPROVED": 155} |
| `dim_naming_compliance_term_rule` | 167 | {"ACTIVE": 167} |
| `dim_category_naming_compliance_rule` | 11 | {"ACTIVE": 6, "REVIEW_REQUIRED": 5} |
| `dim_regulation_reference` | 22 | {} |
| `fact_rule_review_item` | 15172 | {"PENDING": 15172} |
| `dim_product_season_window` | 0 | {} |

## 2. 关键校验结论

- B1 具体品类毛利率为空或为 0 的单元格跳过：30 个。处理原因：不能把“未配置”误导为“公司接受 0 毛利”。
- 竞对分类映射需复核：714 条。处理方式：保留在规则表中，但 `mapping_status=REVIEW_REQUIRED`，算法 07 不得直接生成正式候选。
- 合规词库引用的法源代码未在法规依据表中找到：0 个。全部可关联。
- 商品季节状态销售季窗口：首版包中保留历史空表头。当前最新口径已调整为基础表 `dim_product_status`，由数据开发从 SAP POP 平台按区域、商品名称、商品编码和商品状态提供。
- B4 的 `Sheet1`、`Sheet2`、`Sheet3` 只作为参考，不进入本次生产规则；生产规则来自 `算法6主材料+配料，正向`。

## 3. 已知需要业务/项目/开发侧继续处理

- `dim_competitor_category_mapping_rule` 中 `REVIEW_REQUIRED` 的映射，需要业务或商品侧后续确认后再改成 `ACTIVE`。
- `dim_product_status` 仍缺真实区域商品状态数据，开发需要从 SAP POP 平台补充 A/O/S/D/B 商品状态来源。
- `dim_company_margin_target_config` 中配置确认人暂未写真实姓名，待业务/财务确认后补。

# 数据合同

这里存放给数据开发使用的字段合同。

当前阶段的目标是：让数据开发可以并行准备 V1 AI 新品推荐所需的数据表。每张表都需要进入 Doris，或至少形成可被 Doris 加工任务稳定读取的数据源。

## 开发快速阅读路径

第一次接手数据开发时，按这个顺序读：

```text
1. 先读本 README，确认本目录有哪些表需要建。
2. 再读 Doris 小票源表事实：doris_tables/Doris表结构_dws_member_order_item_detail_df_all_new.md。
3. 再读内部基础表合同：base_tables/。
4. 再读当前基础表补数清单：Doris_data_db基础表查漏补缺清单_2026-08-10.md。
5. 如涉及竞品数据，再读外部竞品数据合同：external_data/。
6. 如涉及算法 05～09 的规则配置，再读规则配置表合同：rule_tables/。
```

## 目录边界

| 目录 / 文件 | 开发是否需要读 | 用途 | 是否正式合同 |
|---|---|---|---|
| `doris_tables/` | 必读 | 已有 Doris 小票源表事实和当前主表说明 | 是 |
| `base_tables/` | 必读 | 内部门店、商品、毛利损耗、价格、可订可售等基础表合同 | 是 |
| `Doris_data_db基础表查漏补缺清单_2026-08-10.md` | 必读 | 当前 Doris `data_db` 对基础表合同的字段覆盖和缺口清单，给开发补字段用 | 当前补数工作清单 |
| `external_data/` | 涉及外部证据时必读 | 久谦两表、公开源原始快照、单指标标准证据、质量明细和输入锁定清单 | 是 |
| `rule_tables/` | 涉及规则配置时必读 | 业务规则 Excel 标准化后的规则表、配置表、复核辅助表合同 | 是 |
| `rule_tables/import_specs/` | 需要追溯首版转换时读 | 首版不标准 Excel 到标准表的导入映射说明 | 审计 / 迁移说明 |
| `rule_tables/import_ready/` | 首版导入时读 | 评审期临时放入 Git 的标准 CSV / Excel 导入包，开发可先使用其中 `csv/` 落 Doris | 临时数据包，不是字段合同 |

## V1 必做数据表

### 已有源表

| 表 | 状态 | 说明 |
| --- | --- | --- |
| Doris 小票商品明细表 | 已有 | 作为会员画像、门店品类等级、SKU 表现等算法的核心交易事实表 |

### 需要开发准备的内部基础表

| 表合同 | 目标表建议名 | 是否 V1 必做 | 说明 |
| --- | --- | --- | --- |
| [门店基础表](base_tables/dim_store_门店基础表.md) | `dim_store` | 必做 | 提供门店名称、城市、区域、管理区域、营业状态等 |
| [商品基础表](base_tables/dim_sku_商品基础表.md) | `dim_sku` | 必做 | 提供商品名称、品类、SPU、规格、温层、保质期等 |
| [毛利损耗表](base_tables/mart_sku_margin_loss_毛利损耗表.md) | `mart_sku_margin_loss` | 必做 | 提供门店商品销售、客数、毛利、折扣、损耗等经营指标 |
| [门店商品日价格表](base_tables/mart_store_sku_daily_price_门店商品日价格表.md) | `mart_store_sku_daily_price` | 必做 | 提供采购价、出库价、到店价、销售原价、成交均价、19点前后价格等 |
| [城市算法区域映射表](base_tables/dim_city_algorithm_region_城市算法区域映射表.md) | `dim_city_algorithm_region` | 必做 | 提供城市到算法区域的映射，用于会员画像和区域参数计算 |
| [统一算法批次城市区域映射快照表](base_tables/dim_algorithm_batch_city_region_snapshot_统一算法批次城市区域映射快照表.md) | `dim_algorithm_batch_city_region_snapshot` | 算法 01～10 共用 | 按 `algorithm_batch_version（统一算法批次版本）`保存城市区域事实，同批次重跑复用原快照 |
| [门店商品每日可订可售表](base_tables/mart_store_sku_daily_sale_order_status_门店商品每日可订可售表.md) | `mart_store_sku_daily_sale_order_status` | 必做 | 判断商品在门店是否可售、是否可订，避免算法误判“没销量”的原因 |
| [商品状态表](base_tables/dim_product_status_商品状态表.md) | `dim_product_status` | 必做 | 从 SAP POP 平台按区域、商品名称、商品编码、商品状态提供全年品、试卖品、季节品、淘汰品和备选品；其中 `S` 行额外提供计划上架开始日期和结束日期 |

### 需要开发准备的外部竞品表

| 表合同 | 目标表建议名 | 是否 V1 必做 | 说明 |
| --- | --- | --- | --- |
| [竞品 SKU 基础表](external_data/dim_competitor_sku_竞品SKU基础表.md) | `dim_competitor_sku` | 必做 | 保存竞品商品稳定属性 |
| [竞品每日快照表](external_data/fact_competitor_sku_daily_snapshot_竞品每日快照表.md) | `fact_competitor_sku_daily_snapshot` | 必做 | 保存竞品每天变化的价格、销量、促销、评价、售罄等数据 |

算法 07 公开来源同时按以下正式合同准备，不以服务器已经导入记录替代字段验收：

| 表合同 | 正式表名 | 用途 |
|---|---|---|
| [公开源原始快照](external_data/ods_external_source_raw_snapshot_公开外部源原始快照表.md) | `ods_external_source_raw_snapshot` | 不可变请求响应与原始依据 |
| [标准化外部证据](external_data/dwd_external_evidence_normalized_标准化外部证据表.md) | `dwd_external_evidence_normalized` | 单指标证据、单位/日期/身份及用途准入 |
| [字段质量明细](external_data/mart_external_evidence_quality_issue_外部证据字段质量明细表.md) | `mart_external_evidence_quality_issue` | 分字段问题和排除/隔离审计 |
| [批次输入锁定清单](external_data/mart_external_batch_input_manifest_外部批次输入锁定清单.md) | `mart_external_batch_input_manifest` | 按统一BATCH锁定来源、观测及重跑血缘 |
| [外部证据解释规则](rule_tables/dim_external_evidence_interpretation_rule_外部证据解释规则表.md) | `dim_external_evidence_interpretation_rule` | 权威身份、单位、日期及用途规则的当批快照 |

花卉排除食品计算但保留快照；未知类别单独隔离。正式证据、参数及审计使用 `algorithm_batch_version = BATCH_YYYYMM`，采集批次及run_id只追溯实际任务。

### 需要开发准备的规则配置表

业务补充 Excel 不作为算法运行时直接输入，需要先转换为标准导入包，再由开发优先使用标准 CSV 落 Doris 规则表、配置表或复核辅助表。

首版标准导入数据包评审期临时放在 `rule_tables/import_ready/`，方便开发直接获取标准 CSV。评审完成后再移出 Git，后续正式分发方式可以走共享盘、数据平台目录或本机临时路径，不影响本目录字段合同口径。

当前交付链路：

```text
首版：业务不标准 Excel -> 项目侧转换为标准 Excel + 标准 CSV -> 开发读取标准 CSV 落 Doris -> 算法读取 Doris 规则表
后续：业务按标准 Excel 模板提供更新 -> 校验字段、主键、版本和生效日期 -> 导出标准 CSV -> 开发落 Doris -> 算法读取 Doris 规则表
```

规则表统一放在：

```text
03_data_contracts/rule_tables/
```

导入映射说明统一放在：

```text
03_data_contracts/rule_tables/import_specs/
```

| 表合同 | 目标表建议名 | 是否 V1 必做 | 说明 |
| --- | --- | --- | --- |
| [规则配置表总说明](rule_tables/README.md) |  | 必读 | 说明 Excel 到规则表的沉淀方式、版本规则和哪些内容不进入生产算法 |
| [业务后续标准 Excel 提供清单](rule_tables/业务后续标准Excel提供清单.md) |  | 必读 | 说明后续业务需要按哪些标准 sheet 提供规则数据 |
| [公司毛利目标配置表](rule_tables/dim_company_margin_target_config_公司毛利目标配置表.md) | `dim_company_margin_target_config` | 必做 | 算法 05 使用的公司毛利底线、目标毛利配置 |
| [价格点规则配置表](rule_tables/dim_price_point_rule_config_价格点规则配置表.md) | `dim_price_point_rule_config` | 必做 | 算法 05 使用的价格尾数、1 元价格点和价格带约束 |
| [购物篮属性转化规则表](rule_tables/dim_basket_attribute_transfer_rule_购物篮属性转化规则表.md) | `dim_basket_attribute_transfer_rule` | 必做 | 算法 06 判断关联商品 B 是否能转成新品属性 |
| [竞对分类映射规则表](rule_tables/dim_competitor_category_mapping_rule_竞对分类映射规则表.md) | `dim_competitor_category_mapping_rule` | 必做 | 算法 07 将外部商品分类映射到内部分类 |
| [商品命名规则表](rule_tables/dim_product_naming_rule_商品命名规则表.md) | `dim_product_naming_rule` | 必做 | 算法 07、08 做商品名解析、标准命名和查重 |
| [特殊品类必填属性规则表](rule_tables/dim_special_product_required_attribute_rule_特殊品类必填属性规则表.md) | `dim_special_product_required_attribute_rule` | 必做 | 算法 07、08 校验特殊商品必填属性 |
| [候选属性字典表](rule_tables/dim_candidate_attribute_dictionary_候选属性字典表.md) | `dim_candidate_attribute_dictionary` | 必做 | 算法 07、08 识别主体、主材料、口味、工艺、功能、规格等属性 |
| [命名合规词规则表](rule_tables/dim_naming_compliance_term_rule_命名合规词规则表.md) | `dim_naming_compliance_term_rule` | 必做 | 算法 07、08、09 识别命名、标签和功能声称风险 |
| [分类命名合规规则表](rule_tables/dim_category_naming_compliance_rule_分类命名合规规则表.md) | `dim_category_naming_compliance_rule` | 必做 | 算法 07、08、09 校验不同分类和适用形态下的命名结构、显著标示和证照要求 |
| [法规依据表](rule_tables/dim_regulation_reference_法规依据表.md) | `dim_regulation_reference` | 必做 | 给合规词规则提供法规、标准或内部制度依据，不实时联网查询 |
| [规则复核样例与人工复核表](rule_tables/fact_rule_review_item_规则复核样例与人工复核表.md) | `fact_rule_review_item` | 建议 | 保存待复核样例、异常、观察池词语和人工审核记录 |

## V1 暂不纳入

以下表先不作为当前开发交付范围：

- 供应商基础表
- 库存损耗明细表
- 促销优惠券明细表

## 开发交付要求

每张表请至少反馈：

1. 字段是否能提供。
2. 字段来源系统或来源表。
3. 是否能按合同粒度产出。
4. 主键是否唯一。
5. 和小票表的关联字段是否能对齐。
6. 数据更新频率。
7. 历史数据可回溯周期。
8. 当前缺失字段和替代字段。

正式 Git 交付不放真实业务 Excel、真实 CSV 明细、Doris 查询结果明细和 API 原始返回。如需提交样例，请放入 `examples/synthetic_data/`，并确保是脱敏或人造数据。

算法07本期新增[外部来源覆盖时效审计](external_data/mart_external_source_coverage_audit_外部来源覆盖时效审计表.md)和[外部候选价格交接输入](external_data/mart_external_candidate_price_input_外部候选价格交接输入表.md)。覆盖/缺报用独立应报集合复算，05按逐来源完整商品键消费；文档合同不代表生产或旧消费者已经验收。

# AI 选品规则表标准导入数据包（2026-08-18）

本目录是业务补充 Excel 转换后的标准导入数据包。开发不需要再从原始 Excel 推字段。

## 使用方式

1. 数据开发优先使用 `csv/` 下的标准 CSV 落 Doris 规则表。
2. 业务、产品和项目侧使用 `AI选品规则表_标准导入数据包_2026-08-18.xlsx` 做可读复核。
3. 每张表的字段中文解释见工作簿 `字段说明` sheet，也可看 `metadata/field_dictionary.csv`。
4. 原始 Excel 到标准表的映射说明只作为审计和溯源，见 `../../import_specs/`。

## 来源文件

- `B1—公司最低毛利率和目标毛利率是多少—2026年集团区毛利目标.xlsx`
- `B3-按竞对商品名称梳理的命名规则.xlsx`
- `B4-哪些购物篮关联能够转化为新品属性.xlsx`
- `生鲜与食品商品命名合规词库_2026-08-18.xlsx`
- 价格点规则来自用户确认：默认每 1 元一个价格点，价格上下限由算法 05 的消费者价格带决定。

## 生成文件

| 标准表 | 中文名 | CSV | 行数 | 说明 |
|---|---|---|---:|---|
| `dim_company_margin_target_config` | 公司毛利目标配置表 | `csv/dim_company_margin_target_config.csv` | 132 | 算法05读取，用于判断候选新品是否满足公司最低毛利底线和目标毛利。 |
| `dim_price_point_rule_config` | 价格点规则配置表 | `csv/dim_price_point_rule_config.csv` | 6 | 算法05读取，在消费者价格带内生成可执行价格点。 |
| `dim_basket_attribute_transfer_rule` | 购物篮属性转化规则表 | `csv/dim_basket_attribute_transfer_rule.csv` | 153 | 算法06读取，判断购物篮关联商品B能否转成目标新品属性。 |
| `dim_product_naming_rule` | 商品命名规则表 | `csv/dim_product_naming_rule.csv` | 51 | 算法07/08读取，用于商品名解析、候选标准命名和查重。 |
| `dim_special_product_required_attribute_rule` | 特殊品类必填属性规则表 | `csv/dim_special_product_required_attribute_rule.csv` | 15 | 算法07/08读取，校验蓝莓、榴莲、大闸蟹等特殊商品是否缺关键属性。 |
| `dim_competitor_category_mapping_rule` | 竞对分类映射规则表 | `csv/dim_competitor_category_mapping_rule.csv` | 6373 | 算法07读取，把外部竞品分类映射到内部大类/中类；映射不稳时只保留证据。 |
| `dim_candidate_attribute_dictionary` | 候选属性字典表 | `csv/dim_candidate_attribute_dictionary.csv` | 2296 | 算法07/08读取，把外部词、商品词、规格词和风险词识别成标准属性维度。 |
| `dim_naming_compliance_term_rule` | 命名合规词规则表 | `csv/dim_naming_compliance_term_rule.csv` | 167 | 算法07/08/09读取，识别禁用词、需审核词、风险等级和放行条件。 |
| `dim_category_naming_compliance_rule` | 分类命名合规规则表 | `csv/dim_category_naming_compliance_rule.csv` | 11 | 算法07/08/09读取，校验不同分类的命名结构、证照和显著标示要求。 |
| `dim_regulation_reference` | 法规依据表 | `csv/dim_regulation_reference.csv` | 22 | 算法07/08/09通过法源代码引用，用于解释风险词为什么被拦截或需审核；算法不实时联网查。 |
| `fact_rule_review_item` | 规则复核样例与人工复核表 | `csv/fact_rule_review_item.csv` | 15172 | 算法07/08/09写入或读取，保存分类不稳、属性不稳、命名风险等需要人工复核的样例。 |
| `dim_product_season_window` | 商品季节状态销售季窗口表 | `csv/dim_product_season_window.csv` | 0 | 历史空表头保留在首版标准导入包中。当前最新口径已调整为基础表 `dim_product_status`，由数据开发从 SAP POP 平台按区域、商品名称、商品编码和商品状态提供。 |

## 重要口径

- CSV 为 UTF-8 编码，第一行是英文字段名，可直接按数据合同落规则表；`dim_product_season_window.csv` 是历史空表头，不作为当前商品状态落表依据。
- 工作簿用于人审，包含字段中文说明和完整数据，不建议作为生产任务直接读取。
- `../../import_specs/` 是本次迁移审计说明，后续业务更新应直接按标准表模板或标准数据包提供。
- 商品状态不再通过本规则导入包维护；开发从 SAP POP 平台接入，最新合同见 `../../../base_tables/dim_product_status_商品状态表.md`。
- 合规法规链接来自业务补充词库，算法运行时不实时联网查询官网。

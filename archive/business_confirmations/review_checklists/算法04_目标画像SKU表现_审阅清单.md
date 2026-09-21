# 算法04_目标画像 SKU 表现_审阅清单

更新时间：2026-09-20

用途：只保留算法 04 正式运行前需要项目侧和开发侧判断的红线。业务原文已经确认的公式、粒度、主键和评分逻辑不在这里重复提问。

## 1. 本次修正重点

本次按“承接矩阵 → 开发歧义审计 → 四文档同步 → 字段级交付闸门”修复，重点闭环：

```text
1. 上游算法 01/02/03 的版本、周期、过滤规则和唯一性闸门。
2. valid_all_txn 与 valid_profiled_member_txn 的交易分层。
3. 小票 order_item_id 去重和冲突阻断。
4. 19:30 前吸收率使用“目标画像销售标准量 / 实际收货标准量”。
5. 标准商品层优先重算 CRITIC、Jenks/BIC 和锚点准入，SKU 层保留追溯。
6. 真实订购字段与收货字段分离。
7. 原价、目标/参考实付价、标准化单价、促销前后价、实际折扣率的字段闭环。
8. JSON 结构、状态枚举、版本血缘和运行审计表闭环。
9. 锚点汇总按 `canonical_anchor_set` 选择单一 SKU/标准商品来源，避免 SPU_MAPPED 双计数。
10. 算法 03 周期字段按 `contribution_start_date/end_date` 映射为本卡内部别名，算法 02 的 `store_group_type` 不作为物理输入列。
```

## 2. 已确认的业务规则（不再向业务重复确认）

| 事项 | 已冻结结论 |
|---|---|
| 算法职责 | 识别目标画像下现有高表现锚点，不生成新品 |
| 评分维度 | 目标画像贡献、目标画像偏好、19:30 前自然动销、商品毛利 |
| 权重 | 两级 CRITIC 动态赋权，不用固定权重 |
| 小样本 | 保留原始值，正式评分使用 Jeffreys 95% 下界；低证据不进正式锚点 |
| 分组 | Jenks+BIC 动态选择 1-3 组；K=1 不强制产生高表现组 |
| 当前在售 | `is_saleable = 1 AND is_orderable = 1` 才是 ACTIVE |
| 订购率 | 不进入综合分，只做覆盖解释 |
| 价格 | 不进入算法 04 综合分，价格带由算法 05 处理 |
| 损耗 | 算法 04 不重复扣损耗 |
| 周期 | 最近 3 个完整自然月；上游周期必须一致 |

## 3. 当前数据库阻断项

| 阻断项 | 影响 | 通过标准 |
|---|---|---|
| 算法 02 正式表缺失 | 无法取得合法门店品类等级和门店群 | 交付 `mart_store_category_level`，包含 `SUCCESS` / `NOT_CALCULABLE`，按合同主键唯一 |
| 算法 03 正式表缺失 | 无法取得目标画像贡献范围 | 交付 `mart_store_group_consumer_contribution`，版本/周期/门店群/画像粒度唯一 |
| 物理可订可售字段不完整 | 无法判断当前锚点 | 提供 `order_sku_id`、`is_saleable`、`is_orderable` 并通过非空与主键验收 |
| 真实订购字段缺失 | 无法计算订购覆盖 | 按商品计量类型提供适用的 `order_qty` 或 `order_weight_kg`；否则订购率必须为 NULL + `DATA_INSUFFICIENT` |
| 含税成本字段缺失 | 无法启用价格表成本备选 | 不得用 `arrival_price` 偷换 `outbound_arrival_cost_tax_included` |

## 4. 开发交付验收项

这些是“开发是否按已确认合同稳定交付”的验收，不重复列出数据合同事实。

| 编号 | 验收项 | 验收动作 | 失败处理 |
|---|---|---|---|
| D1 | `dim_customer_profile` | 冻结字段、`profile_model_version + customer_id` 唯一、周期覆盖和 `final_profile` 非空 | 阻断画像会员交易，写 `UPSTREAM_VERSION_ERROR` 或审计阻断 |
| D2 | 算法 02 接口 | `SUCCESS` / `NOT_CALCULABLE` 状态完整，主键唯一；只消费 `SUCCESS` | 无 `SUCCESS` 门店不写正式锚点 |
| D3 | 算法 03 接口 | 状态可消费，画像明细唯一，周期和范围与本批一致 | 不自行重算主力画像，写 `UPSTREAM_RESULT_MISSING` |
| D4 | Doris 小票 | 按 `order_item_id/update_time` 去重；同键字段冲突阻断；`is_customer=1` 过滤可追溯 | 受影响结果不发布 |
| D5 | 两套事实集 | 全量经营使用 `valid_all_txn`，画像指标使用 `valid_profiled_member_txn` | 发现串用时阻断自然动销或画像得分 |
| D6 | 计量字段 | `weight` 与 `sale_unit/specification` 抽样可解释；单位不可识别时不跨单位相加 | 数量指标 NULL，标 `UNKNOWN`/`UNIT_CONVERSION_ERROR` |
| D7 | 可订可售 | `is_saleable=1 AND is_orderable=1` 才生成门店 SKU ACTIVE；候选门店来自算法 02 同范围/周期/品类的 `SUCCESS`，与锁定快照 `dim_store.is_open=1` 形成有效门店集合；状态表主键唯一且覆盖完整 | 不用销量或收货代理状态；候选门店缺失、维表冲突或覆盖不完整时写 NULL + 运行审计 |
| D7a | 范围级在售聚合 | 业务确认“任一有效门店”还是“全部有效门店”才算范围级 `ACTIVE`；V1 暂提案为任一有效门店；`listing_scope_rule_version` 必须记录；状态 NULL 不能降级成历史锚点 | 未确认前不发布当前/历史锚点；规则版本变更时全量重算 |
| D8 | 订购率 | 按商品计量类型选择真实订购字段：称重用 `order_weight_kg`，计件/枚数等用 `order_qty`；不混用单位 | 对应字段缺失则 NULL + `DATA_INSUFFICIENT` |
| D15 | 订购范围回退 | `GROUP_ALL_STORES` 只能使用带来源、快照日期和范围版本的已批准全局可订范围；不得因门店级字段缺失自动回退 | 无批准来源则不设置回退，写运行审计；订购覆盖字段 NULL + `DATA_INSUFFICIENT` |
| D9 | 自然动销 | 售罄率分子/分母可复算，>110% 标 `SELL_THROUGH_DATA_ERROR`；吸收率分母为实际收货标准量 | 不截断、不补零 |
| D10 | 成本与毛利 | 默认单位成本法；异常降级必须显式打标；不二次扣损耗 | 无法解释时不进正式锚点 |
| D11 | 标准商品层 | 有效 SPU 先聚合去重并重算评分；SKU 层保留原始证据 | SPU 冲突用 `SKU_ONLY` 或 `PRODUCT_MASTER_CONFLICT` |
| D11a | 锚点汇总 canonical 层 | `SPU_MAPPED` 只从标准商品表进入锚点 JSON/计数；`SKU_ONLY` 只从 SKU 表进入；按 `standard_product_key` 去重并保留 `representative_sku_id/source_layer` | 发现 SKU+SPU 双计数时阻断汇总表，重算 canonical 集合 |
| D12 | 价格字段 | 六项价格字段来源和缺失写法可追溯；`before_after_promotion_price.price_source` 只允许 `PRICE_TABLE_ORIGINAL_DORIS_USUAL_AMT_PER_WEIGHT`；原价不得用成交均价替代 | NULL + `PRICE_SOURCE_MISSING` |
| D13 | 字段合同 | 五类正式表和运行审计表都有粒度、主键、完整字段、状态约束和缺失写法；锚点 JSON 的 `source_layer` 只允许 `PRODUCT/SKU` | 不得交付含“开发自行理解”的字段 |
| D14 | 版本血缘 | 所有正式结果包含 `member_filter_rule_version`、02/03 周期、`source_data_version`、`listing_snapshot_date`、`listing_scope_rule_version`、`upstream_version_fingerprint`；算法 03 周期物理字段为 `contribution_start_date/end_date`，本卡别名必须可追溯 | 禁止不同上游或在售规则版本覆盖同一结果 |

## 5. 真正需要项目侧判断的事项

| 事项 | 需要判断什么 | 影响 |
|---|---|---|
| 当前物理源能否映射合同字段 | 物理表字段是否能稳定映射到合同字段，尤其是可订可售、真实订购、含税成本 | 决定是否可以正式发布 |
| 范围级在售聚合规则 | 业务确认“任一有效门店”还是“全部有效门店”才算范围级 `ACTIVE`；有效门店集合来源和完整性按开发口径执行，V1 文档暂以任一门店为提案 | 规则未确认前不得发布当前/历史锚点；确认后写入 `listing_scope_rule_version` 并全量重算 |
| V1 属性规则资产 | 当前是否已有审核过的属性字典/名称解析规则 | 只影响解释字段，不应编造属性 |
| 商品状态资产可用性 | `dim_product_status` 是否提供可靠版本和状态快照 | 缺失时不阻断经营表现，但不能编造季节/停售原因 |

## 6. 交付闸门

只有同时满足以下条件，才能向下游宣称“算法 04 正式结果可发布”：

```text
1. 算法 01/02/03 正式表存在，版本、周期、范围和主键唯一通过。
2. 小票去重、有效交易过滤和两层金额对账通过。
3. 可订可售、真实订购、到货/毛利/价格字段通过合同验收。
4. 标准商品层和 SKU 层的评分与追溯关系通过抽样复算。
5. 正式输出字段、状态枚举、JSON 结构、版本血缘和运行审计表完整。
6. 无结果、无消费、不可计算和上游缺失场景没有伪造明细行。
```

当前结论：算法 04 规则和文档可以进入开发接口评审；在算法 02、03 正式物理结果表交付前，不能正式跑数或发布锚点。

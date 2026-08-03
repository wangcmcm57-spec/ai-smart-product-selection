# Doris 表结构：会员小票商品明细

查询日期：2026-08-03

连接信息：

```text
Host：10.111.231.11
Port：9030
Database：data_agent
```

说明：文档不记录数据库密码。

## 1. 当前实际表

本次连接 `data_agent` 后，当前库中只有 2 张小票商品明细相关表：

| 表名 | 行数 | 数据量 | 表说明 | 当前判断 |
|---|---:|---:|---|---|
| `data_agent.dws_member_order_item_detail_df_all_new` | 2,702,875,261 | 261.608 GB | 全国会员订单商品明细宽表临时重载表 | 当前有数据，后续算法优先使用 |
| `data_agent.dws_member_order_item_detail_df_all_schema_bak` | 0 | 0 | 全国会员订单商品明细宽表，用于会员消费、促销、渠道、接龙、退货等分析 | 备份空表，不作为计算输入 |

历史文档中写过：

```text
data_agent.dws_member_order_item_detail_df_all
```

但本次在 `data_agent` 当前表清单中未看到该无后缀表。后续算法卡建议统一引用：

```text
data_agent.dws_member_order_item_detail_df_all_new
```

如果数据开发后续提供稳定生产表或视图，再统一替换。

## 2. 当前主表建表摘要

表名：

```text
data_agent.dws_member_order_item_detail_df_all_new
```

建表摘要：

```text
ENGINE = OLAP
DUPLICATE KEY(order_item_id)
DISTRIBUTED BY HASH(order_item_id) BUCKETS 128
COMMENT = 全国会员订单商品明细宽表临时重载表
```

注意：

```text
order_item_id 是 Doris 唯一键候选，但当前表是 DUPLICATE KEY 表。
算法开发时仍需按 order_item_id 做明细去重校验。
```

## 3. 字段结构

两张表字段一致，均为 28 个字段。

| 序号 | 字段名 | 字段类型 | 是否可空 | 中文注释 |
|---:|---|---|---|---|
| 1 | `order_item_id` | varchar(64) | 否 | 订单商品明细ID，来源订单商品表 id，作为 Doris 唯一键 |
| 2 | `business_date` | date | 是 | 业务日期，取订单时间 `inc_time` 对应日期 |
| 3 | `store_id` | varchar(64) | 是 | 门店ID |
| 4 | `order_id` | varchar(64) | 是 | 订单ID |
| 5 | `article_id` | varchar(64) | 是 | 商品ID，对应 `goods_id` |
| 6 | `is_hour_promotion` | int | 是 | 是否小时促销：1 是，0 否 |
| 7 | `inc_time` | datetime | 是 | 订单增量时间，优先 `order_at`，其次 `pay_at`，再次 `created_at` |
| 8 | `sales_mode_id` | varchar(32) | 是 | 销售模式ID：10-POS，20-自提，101-配送，2-扫码购，其他取 `business_source` |
| 9 | `order_status` | varchar(64) | 是 | 订单状态 |
| 10 | `parent_order_id` | varchar(64) | 是 | 父订单ID |
| 11 | `online_flag` | int | 是 | 是否线上订单：1 是，0 否 |
| 12 | `customer_id` | varchar(64) | 是 | 会员ID |
| 13 | `is_customer` | int | 是 | 是否会员：1 是，0 否 |
| 14 | `order_type` | varchar(64) | 是 | 订单类型 |
| 15 | `order_sub_type` | varchar(64) | 是 | 订单子类型 |
| 16 | `channel_id` | varchar(64) | 是 | 渠道ID |
| 17 | `refund_type` | varchar(64) | 是 | 退款类型 |
| 18 | `business_source` | varchar(64) | 是 | 业务来源 |
| 19 | `jielong_flag` | varchar(32) | 是 | 接龙标识 |
| 20 | `cust_counts` | bigint | 是 | 门店当日会员数 |
| 21 | `is_return` | int | 是 | 是否退货订单：1 是，0 否 |
| 22 | `update_time` | datetime | 是 | 订单更新时间 |
| 23 | `usual_amt` | decimal(18,6) | 是 | 商品行实付金额 |
| 24 | `discount_amt` | decimal(18,6) | 是 | 商品行优惠金额 |
| 25 | `hour_discount_amt` | decimal(18,6) | 是 | 会员当天同小时累计优惠金额 |
| 26 | `weight` | decimal(18,6) | 是 | 商品实际重量；结合样例判断，更准确理解为商品行计价数量 |
| 27 | `list_price` | decimal(18,6) | 是 | 原价 |
| 28 | `sale_price` | decimal(18,6) | 是 | 售价 |

## 4. 字段事实化说明

字段事实化分三层：

```text
1. 字段是否存在、类型、Doris 注释是什么。
2. 字段值在样例里长什么样，是否有负数、空值、状态枚举。
3. 字段进入算法时能不能直接聚合，还是只能作过滤、标记、校验或需要其他主数据补充。
```

当前 28 个字段的算法使用事实如下：

| 字段名 | Doris 注释/字段含义 | 字段值形态 | 算法使用方式 |
|---|---|---|---|
| `order_item_id` | 订单商品明细ID，来源订单商品表 id，作为 Doris 唯一键 | 非空；当前主表是 `DUPLICATE KEY` | 商品行唯一键候选，开发需做重复校验；不可直接假设物理表已强唯一 |
| `business_date` | 业务日期，取 `inc_time` 对应日期 | date | 周期过滤、日聚合、复购窗口、调度分区字段 |
| `store_id` | 门店ID | 字符串 | 对齐门店基础表的门店编码 |
| `order_id` | 订单ID | 字符串；已确认全公司唯一 | 小票唯一键，用于小票数、购物篮、复购和客单计算 |
| `article_id` | 商品ID，对应 `goods_id` | 字符串 | 销售商品编码，对齐商品基础表的交易商品编码 |
| `is_hour_promotion` | 是否小时促销：1 是，0 否 | 0/1 | 时段促销标记；可用于解释或代理判断 |
| `inc_time` | 订单增量时间，优先 `order_at`，其次 `pay_at`，再次 `created_at` | datetime | 19:00、19:30、晚高峰、半小时折扣档、复购第二次购买时间判断 |
| `sales_mode_id` | 销售模式ID：10-POS，20-自提，101-配送，2-扫码购，其他取 `business_source` | 样例含 `10`、`20`、`101`、`3` | 渠道/销售模式解释字段；是否纳入某算法需按算法卡指定 |
| `order_status` | 订单状态 | 样例含 `os.completed`、`os.return.completed`、`os.refund.completed` | 有效交易过滤字段，默认保留 `os.completed` |
| `parent_order_id` | 父订单ID | 可空 | 退款、拆单、父子单追溯备用；默认不作为聚合键 |
| `online_flag` | 是否线上订单：1 是，0 否 | 0/1 | 线上/线下渠道解释字段；默认不影响有效交易 |
| `customer_id` | 会员ID | 可空 | 会员画像、目标画像、画像贡献的核心关联键；会员算法需非空 |
| `is_customer` | 是否会员：1 是，0 否 | 0/1；样例中抽到均为 1，但不能据此假设全量均为会员 | 会员算法过滤字段；全量销售额覆盖率诊断不能只保留会员 |
| `order_type` | 订单类型 | 样例含 `normal`、`group.buy` | 交易类型解释和异常过滤辅助字段 |
| `order_sub_type` | 订单子类型 | 样例含 `pos`、`delivery`、`selfpick` | POS/配送/自提解释字段；默认不作为主过滤，除非算法卡指定 |
| `channel_id` | 渠道ID | 数字字符串，样例含 `8`、`32`、`16`、`64` 等 | 渠道解释字段；中文含义需业务或数据字典补充 |
| `refund_type` | 退款类型 | 可空；样例含 `whole.return`、`partial.return`、`whole.refund`、`partial.refund` | 有效交易过滤辅助字段；默认退款/退货类不进正向销售汇总 |
| `business_source` | 业务来源 | 样例含 `0`、`3`、`4` | 业务来源解释字段；可辅助识别特殊来源或测试来源 |
| `jielong_flag` | 接龙标识 | 样例含 `non_jielong`、`shop` | 接龙交易解释字段；默认不影响有效交易，特殊算法可单独使用 |
| `cust_counts` | 门店当日会员数 | bigint | 门店日会员数参考字段；不建议替代按 `customer_id` 去重得到的算法会员数 |
| `is_return` | 是否退货订单：1 是，0 否 | 0/1 | 有效交易过滤字段，默认保留 `0` |
| `update_time` | 订单更新时间 | datetime | 数据追溯和增量同步字段，不参与业务指标计算 |
| `usual_amt` | 商品行实付金额 | decimal；样例可出现负数 | 商品行销售额；有效销售默认要求 `usual_amt > 0` |
| `discount_amt` | 商品行优惠金额 | decimal；样例可正、可零、可负 | 商品行优惠金额；V1 可用 `discount_amt > 0` 作为促销/折扣代理，必须先过滤有效交易 |
| `hour_discount_amt` | 会员当天同小时累计优惠金额 | decimal；样例可正、可零、可负，且不是商品行金额 | 不能按商品行直接 `SUM`；只能作时段优惠辅助判断，时段折扣金额优先用毛利损耗表汇总字段 |
| `weight` | Doris 注释为商品实际重量；结合计件商品样例，更准确是商品行计价数量 | decimal；样例可负；有效销售要求 `weight > 0` | 小票明细里唯一承担“买了多少”的字段。称重商品表示计价重量，计件商品表示件/盒/袋/只等计价数量；Doris 本身没有单位字段，单位必须由商品基础表补充 |
| `list_price` | 原价 | decimal；样例为正 | 商品行原价/标价，可用于校验标准销售额和折扣率 |
| `sale_price` | 售价 | decimal；样例为正 | 商品行成交单价；通常 `usual_amt ≈ sale_price × weight`，可用于金额一致性校验 |

## 5. `weight` 字段最新口径

`weight` 不再只理解为称重重量。它在这张小票明细表中更准确是“商品行计价数量”。

```text
称重商品：weight = 计价重量
计件商品：weight = 计价数量，例如件数、盒数、袋数、只数
```

例子：

```text
草鸡蛋8枚：weight = 1 表示买 1 盒/份
钱大妈五红馒头400g/袋：weight = 1 表示买 1 袋，weight = 2 表示买 2 袋
竹丝乌鸡(只)：weight = 1 表示买 1 只，weight = 2 表示买 2 只
```

因此后续算法卡统一写法：

```text
sales_standard_qty = weight
```

Doris 小票明细本身没有单位字段，也没有单独的 `qty` / `quantity` / `num` / `unit` / `spec` / `uom` 字段。要知道 `weight` 到底表示 kg、斤、盒、袋、只，必须关联商品基础表的 `单位`、`规格`、`单位重量` 等字段。

金额校验逻辑：

```text
usual_amt ≈ sale_price × weight
```

再根据商品基础表的 `单位` 判断计量类型：

```text
千克、kg、公斤、g、克 -> WEIGHT
件、份、盒、包、袋、瓶、个、只 -> QUANTITY
无法识别 -> UNKNOWN
```

## 6. 有效交易过滤基础口径

算法侧基础过滤建议：

```text
order_status = 'os.completed'
AND is_return = 0
AND usual_amt > 0
AND weight > 0
```

会员画像或目标画像算法还需增加：

```text
is_customer = 1
customer_id IS NOT NULL
customer_id <> ''
```

`refund_type` 的正式过滤枚举建议在开发评审中确认。若 `refund_type` 为空表示无退款，则有效交易可增加：

```text
refund_type IS NULL OR refund_type = ''
```

## 7. 读取注意事项

当前主表约 27.03 亿行。全表 `COUNT DISTINCT`、全表枚举状态字段等查询可能触发 Doris 内存保护。

后续开发建议：

```text
1. 优先按业务日期分批计算。
2. 先生成日门店 SKU 级过程结果，再做跨周期汇总。
3. 全表质量检查不要直接 COUNT DISTINCT 多个字段，改用分日期、分城市、分门店分批校验。
4. 抽样验收可以使用 LIMIT 或限定日期范围。
```

## 8. 抽样字段形态

2026-08-03 使用当前主表 `LIMIT 10000` 轻量抽样，样例仅用于判断字段形态，不代表全量分布。

状态类字段样例：

| 字段 | 样例值 |
|---|---|
| `order_status` | `os.completed`、`os.return.completed`、`os.refund.completed` |
| `refund_type` | 空值、`whole.return`、`partial.return`、`whole.refund`、`partial.refund` |
| `is_return` | `0`、`1` |
| `sales_mode_id` | `10`、`20`、`101`、`3` |
| `order_sub_type` | `pos`、`delivery`、`selfpick` |
| `online_flag` | `0`、`1` |
| `jielong_flag` | `non_jielong`、`shop` |

数值字段抽样发现：

```text
usual_amt、discount_amt、hour_discount_amt、weight 都可能出现负数。
list_price、sale_price 抽样中均为正数。
```

因此所有算法读取小票明细时，不能直接全量汇总，必须先套有效交易过滤：

```text
order_status = 'os.completed'
AND is_return = 0
AND usual_amt > 0
AND weight > 0
```

需要会员维度时，再叠加：

```text
is_customer = 1
AND customer_id IS NOT NULL
AND customer_id <> ''
```

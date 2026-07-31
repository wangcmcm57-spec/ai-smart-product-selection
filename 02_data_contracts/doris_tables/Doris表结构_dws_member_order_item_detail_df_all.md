# Doris 表结构：dws_member_order_item_detail_df_all

查询日期：2026-07-15

连接信息：

```text
Host：10.111.231.11
Port：9030
Database：data_agent
```

## 1. 查询结论

业务原始文档中写的表名：

```text
data_agent.dws_member_order_item_detail_df
```

本次实际连接 Doris 后，该表不存在。

当前库中找到并成功查询的相近表：

```text
data_agent.dws_member_order_item_detail_df_all
```

建议后续会员画像算法先以这张表作为小票商品明细主输入表，除非数据开发确认另有正式生产表。

## 2. 建表信息摘要

```text
表类型：Doris OLAP 表
唯一键：order_item_id
分桶：HASH(order_item_id) BUCKETS 32
表说明：全国会员订单商品明细宽表，用于会员消费、促销、渠道、接龙、退货等分析
```

完整建表语句已导出：

```text
outputs/doris_dws_member_order_item_detail_df_all_show_create.sql
```

完整字段 CSV 已导出：

```text
outputs/doris_dws_member_order_item_detail_df_all_columns.csv
```

## 3. 字段结构

| 序号 | 字段名 | 字段类型 | 中文注释 |
|---:|---|---|---|
| 1 | order_item_id | varchar(64) | 订单商品明细ID，来源订单商品表id，作为Doris唯一键 |
| 2 | business_date | date | 业务日期，取订单时间inc_time对应日期 |
| 3 | store_id | varchar(64) | 门店ID |
| 4 | order_id | varchar(64) | 订单ID |
| 5 | article_id | varchar(64) | 商品ID，对应goods_id |
| 6 | is_hour_promotion | int | 是否小时促销：1是，0否 |
| 7 | inc_time | datetime | 订单增量时间，优先order_at，其次pay_at，再次created_at |
| 8 | sales_mode_id | varchar(32) | 销售模式ID：10-POS，20-自提，101-配送，2-扫码购，其他取business_source |
| 9 | order_status | varchar(64) | 订单状态 |
| 10 | parent_order_id | varchar(64) | 父订单ID |
| 11 | online_flag | int | 是否线上订单：1是，0否 |
| 12 | customer_id | varchar(64) | 会员ID |
| 13 | is_customer | int | 是否会员：1是，0否 |
| 14 | order_type | varchar(64) | 订单类型 |
| 15 | order_sub_type | varchar(64) | 订单子类型 |
| 16 | channel_id | varchar(64) | 渠道ID |
| 17 | refund_type | varchar(64) | 退款类型 |
| 18 | business_source | varchar(64) | 业务来源 |
| 19 | jielong_flag | varchar(32) | 接龙标识：community-社区接龙，shop-门店接龙，non_jielong-非接龙 |
| 20 | cust_counts | bigint | 门店当日会员数 |
| 21 | is_return | int | 是否退货订单：1是，0否 |
| 22 | update_time | datetime | 订单更新时间 |
| 23 | usual_amt | decimal(18,6) | 商品行实付金额 |
| 24 | discount_amt | decimal(18,6) | 商品行优惠金额，应付金额-实付金额 |
| 25 | hour_discount_amt | decimal(18,6) | 会员当天同小时累计优惠金额 |
| 26 | weight | decimal(18,6) | 商品实际重量 |
| 27 | list_price | decimal(18,6) | 原价 |
| 28 | sale_price | decimal(18,6) | 售价 |

## 4. 对会员画像算法的影响

可以直接使用的字段：

```text
会员编码：customer_id
门店编码：store_id
小票编码：order_id
交易商品编码：article_id
业务日期：business_date
交易时间：inc_time
实付金额：usual_amt
优惠金额：discount_amt
时段促销标记：is_hour_promotion
时段优惠金额：hour_discount_amt
销售重量：weight
订单状态：order_status
退款类型：refund_type
是否退货：is_return
是否会员：is_customer
数据更新时间：update_time
```

当前缺口：

```text
1. 没有独立的促销折扣金额 promo_discount_amt。
2. 没有独立的会员折扣金额 member_discount_amt。
3. 没有独立的销售数量 sale_qty。
4. hour_discount_amt 是“会员当天同小时累计优惠金额”，不是明确的商品行级时段折扣金额，需要数据开发确认口径。
```

因此，会员画像算法中的价格态度第一版有两种选择：

```text
方案 A：使用 discount_amt > 0 作为优惠/促销代理口径试跑，并标记 price_rule_degraded_flag = 1。
方案 B：如果业务不接受代理口径，则价格态度暂不正式输出，等补充促销/会员折扣行级字段。
```

## 5. 过滤建议

样例数据中出现了负实付金额、负优惠金额、负重量，并且存在退货/退款状态。

会员画像正式计算建议保留：

```text
is_customer = 1
is_return = 0
order_status = 'os.completed'
refund_type IS NULL
usual_amt > 0
```

2026-06-07 单日抽查发现：

```text
order_status = os.completed：5,730,550 行
order_status = os.return.completed：32,701 行
order_status = os.refund.completed：6,673 行
is_return = 1：39,374 行
```

这些退货/退款记录不应进入会员画像。

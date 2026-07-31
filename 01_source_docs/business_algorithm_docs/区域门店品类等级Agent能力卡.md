# 区域门店品类等级 Agent 能力卡

生成日期：2026-06-19

依赖规则文档：`区域门店品类等级算法规则.md`

## 1. Agent 名称

```text
区域门店品类等级 Agent
```

建议系统内部能力名：

```text
store_category_level_agent
```

## 2. Agent 目标

该 Agent 的目标是：

```text
基于区域、门店、品类、小票销售、会员客数、毛利、19 点前促销折扣、区域品类损耗等数据，
使用中位数标准化、熵权法、象限分析和多算法交叉验证，
判断某个区域品类下不同门店的经营承接能力，
并输出正式等级标签或观察型标签。
```

它回答的问题不是：

```text
全店哪个门店最好
全品类哪个 SKU 卖得最好
所有门店是否必须分成 A/B/C/D
```

而是：

```text
在同一区域组、同一大类、中类、小类下，
哪些门店更适合承接该品类的经营、选品、营销、试点或改善动作。
```

## 3. 适用场景

该 Agent 适用于：

```text
新品上市门店选择
季节品重点门店选择
品类营销门店筛选
会员券投放门店适配
门店任务下发范围判断
清库存或质量改善门店识别
AI 选品中的门店品类承接能力判断
```

不适用于：

```text
单纯全店销售排名
单纯 SKU 热销榜
不区分区域和品类的门店分级
没有毛利、损耗、折扣等质量指标的粗糙排名
```

## 4. 输入字段

### 4.1 必填业务维度

```text
region_group
city
store_id
store_name
large_category
mid_category
small_category
```

比较组固定为：

```text
region_group + large_category + mid_category + small_category
```

### 4.2 必填经营指标

```text
sales_amt
ticket_cnt
member_customer_cnt
pre19_sales_amt
full_chain_gross_profit_amt
store_margin_rate
pre19_promo_discount_amt
loss_rate
```

### 4.3 推荐保留诊断字段

```text
sales_qty
gross_margin_rate
store_gross_profit_amt
discount_amt
promo_discount_amt
hour_discount_amt
discount_rate
hour_discount_rate
mapping_missing_flag
outlier_flag
```

其中：

```text
hour_discount_rate 只作为晚间折扣诊断字段，不进入品类等级评分。
```

## 5. 依赖数据表

### 5.1 Doris 小票明细

```text
data_agent.dws_member_order_item_detail_df
```

用于计算：

```text
销售额
销售数量 / 重量
小票数
会员客数
19 点前销售额
19 点前促销折扣额
全日折扣额
时段折扣额
```

### 5.2 商品、门店、毛利和损耗映射

来自商品和门店静态补充表，例如：

```text
华东门店商品明细（4月至今）.xlsx
华东门店猪肉类商品明细（4月至今）.xlsx
```

用于补充：

```text
大类
中类
小类
商品名称
门店名称
城市
毛利率
损耗率
```

## 6. 执行步骤

### 6.1 数据准备

Agent 必须先完成：

```text
1. 按 region_group + large_category + mid_category + small_category 建立比较组。
2. 聚合到门店品类粒度。
3. 检查毛利率、损耗率、品类映射是否缺失。
4. 剔除无法参与评分的缺失毛利率或损耗率 SKU。
5. 保留缺失映射诊断记录。
```

### 6.2 指标计算

必须计算：

```text
pre19_sales_share = pre19_sales_amt / sales_amt
promo_discount_rate = pre19_promo_discount_amt / pre19_sales_amt
```

注意：

```text
promo_discount_rate 在本 Agent 中只表示 19 点前促销折扣率。
hour_discount_rate 不进入评分。
loss_rate 按区域品类建立健康度，不使用全局统一损耗线。
```

### 6.3 中位数标准化

Agent 必须使用 50 分位标准化，也就是中位数标准化。

正向指标：

```text
sales_amt
member_customer_cnt
full_chain_gross_profit_amt
store_margin_rate
pre19_sales_share
```

反向指标：

```text
promo_discount_rate
loss_rate
```

标准化原则：

```text
正向指标高于同组中位数，标准化得分高于基准。
反向指标低于同组中位数，健康度得分高于基准。
不允许使用极大值、极小值直接决定标准化尺度。
```

### 6.4 熵权法综合评分

Agent 必须用熵权法自动计算指标权重。

综合公式：

```text
category_score = Σ 标准化指标得分 × 熵权法自动计算权重
```

执行要求：

```text
1. 每个比较组单独计算熵权。
2. 不允许跨品类、跨区域共用同一组权重。
3. 不允许人工指定固定权重。
4. 必须输出每个指标的权重。
```

### 6.5 象限分析

Agent 必须计算两个主轴：

```text
经营规模轴
经营质量轴
```

经营规模轴使用：

```text
sales_amt
member_customer_cnt
ticket_cnt
```

经营质量轴使用：

```text
full_chain_gross_profit_amt
store_margin_rate
pre19_sales_share
promo_discount_health_score
loss_health_score
```

输出象限类型：

```text
优势经营型
规模强但质量待改善
潜力培育型
谨慎经营型
```

### 6.6 多算法交叉验证

Agent 在输出正式等级前必须做交叉验证。

可使用的验证方法：

```text
熵权法综合评分
象限分析
聚类分析
稳健排名分析
时间窗口稳定性验证
业务规则校验
```

关键规则：

```text
如果熵权分数差异达到有效区分阈值，熵权结果可以进入交叉验证。
如果熵权分数差异未达到有效区分阈值，熵权结果必须从最终交叉验证中剔除。
剔除熵权结果后，保留象限、聚类、稳定性和业务规则结果继续判断。
```

### 6.7 输出等级或观察型标签

Agent 不得强制所有比较组输出 A/B/C/D。

正式等级：

```text
A
B
C
D
```

观察型标签：

```text
暂不分级
观察型
潜力培育型
质量改善型
谨慎经营型
人工复核
```

输出原则：

```text
只有样本量、指标完整性、熵权区分度、象限一致性和多算法验证都满足时，才输出正式等级。
不满足时输出观察型标签，并说明原因。
```

## 7. 禁止事项

Agent 禁止：

```text
1. 禁止使用人工固定权重。
2. 禁止使用 sales_amt 单指标给门店品类排序。
3. 禁止把所有门店品类组强行切成 A/B/C/D。
4. 禁止使用极大值、极小值标准化作为主口径。
5. 禁止把 hour_discount_rate 纳入品类等级评分。
6. 禁止使用全局统一损耗阈值。
7. 禁止让缺失毛利率或损耗率的 SKU 参与评分。
8. 禁止在熵权分数无有效区分度时仍把熵权结果纳入最终交叉验证。
9. 禁止只输出等级，不输出原因和风险。
```

## 8. 输出格式

### 8.1 明细输出

每个门店品类至少输出：

```text
region_group
city
store_id
store_name
large_category
mid_category
small_category
sales_amt
ticket_cnt
member_customer_cnt
pre19_sales_share
full_chain_gross_profit_amt
store_margin_rate
promo_discount_rate
loss_rate
sales_score
member_score
full_chain_gross_profit_score
store_margin_score
pre19_sales_share_score
promo_discount_health_score
loss_health_score
sales_weight
member_weight
full_chain_gross_profit_weight
store_margin_weight
pre19_sales_share_weight
promo_discount_health_weight
loss_health_weight
category_score
scale_axis_score
quality_axis_score
quadrant_type
category_level
grade_status
grade_reason
risk_flags
recommended_action
```

### 8.2 业务解释输出

每个等级或标签必须解释：

```text
为什么是这个等级或标签
主要优势是什么
主要风险是什么
是否适合营销动作
适合什么类型的营销动作
是否需要先做经营质量改善
```

### 8.3 推荐 JSON 结构

```json
{
  "agent_name": "store_category_level_agent",
  "comparison_group": {
    "region_group": "上海",
    "large_category": "肉禽蛋类",
    "mid_category": "蛋类",
    "small_category": "鸡蛋类"
  },
  "method": {
    "standardization": "median_50_percentile",
    "weighting": "entropy_weight",
    "quadrant_analysis": true,
    "cross_validation": true
  },
  "result": {
    "store_id": "string",
    "store_name": "string",
    "category_score": 0.0,
    "quadrant_type": "优势经营型",
    "category_level": "A",
    "grade_status": "正式分级",
    "grade_reason": "熵权高分，且象限验证为优势经营型"
  },
  "risk_flags": [],
  "recommended_action": "重点营销"
}
```

## 9. 异常处理

### 9.1 样本不足

触发条件：

```text
同一比较组内可评分门店数不足
销售额、小票数或会员客数不足以形成稳定判断
```

输出：

```text
grade_status = 暂不分级
grade_reason = 样本量不足，无法稳定分级
```

### 9.2 熵权无有效区分度

触发条件：

```text
category_score 在同组内差异过小
历史验证未达到有效区分阈值
```

处理：

```text
熵权结果剔除出最终交叉验证
保留象限、聚类、稳定性和业务规则继续判断
```

### 9.3 象限与熵权冲突

触发条件：

```text
熵权高分但象限显示质量风险
熵权低分但象限显示潜力较强
```

处理：

```text
进入多算法交叉验证
必要时输出质量改善型、潜力培育型或人工复核
```

### 9.4 毛利或损耗缺失

触发条件：

```text
SKU 缺失毛利率
SKU 缺失损耗率
门店品类关键质量指标缺失过多
```

处理：

```text
缺失 SKU 不参与评分
保留销售统计观察
写入映射缺口诊断
门店品类组必要时输出暂不分级
```

## 10. 与营销 Agent 的衔接方式

区域门店品类等级 Agent 是营销 Agent 的前置判断能力。

它向营销 Agent 提供：

```text
哪些门店适合重点营销
哪些门店适合小范围测试
哪些门店需要先改善毛利、折扣或损耗
哪些门店不适合当前营销动作
```

推荐衔接：

| 输出标签 | 营销动作 |
|---|---|
| A | 重点营销、重点发券、重点陈列、较高预算 |
| B | 小范围测试、适度发券、观察转化 |
| C | 谨慎测试、低预算、定向小券 |
| D | 暂缓重点营销，仅保留低风险动作 |
| 暂不分级 | 不做强动作，继续补数据 |
| 潜力培育型 | 小范围试点新品、内容或会员券 |
| 质量改善型 | 先改善毛利、折扣、损耗，再放大营销 |
| 谨慎经营型 | 暂缓营销，优先诊断 |

## 11. 稳定性检查清单

Agent 每次运行后必须自检：

```text
1. 是否按 region_group + large_category + mid_category + small_category 建组。
2. 是否使用中位数标准化。
3. 是否使用熵权法自动计算权重。
4. 是否输出了各指标权重。
5. 是否只用 19 点前 promo_discount_rate 计算折扣健康度。
6. 是否排除了缺失毛利率或损耗率的 SKU。
7. 是否完成象限分析。
8. 是否检查熵权分数是否有有效区分度。
9. 是否在冲突时执行多算法交叉验证。
10. 是否避免强制输出 A/B/C/D。
11. 是否输出 grade_reason 和 risk_flags。
12. 是否给出营销动作建议。
```

如果任一检查不通过，Agent 不得输出“正式分级”，只能输出：

```text
暂不分级
观察型
人工复核
```


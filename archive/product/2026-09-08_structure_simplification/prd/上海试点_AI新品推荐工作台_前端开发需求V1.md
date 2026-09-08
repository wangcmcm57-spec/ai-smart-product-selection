# 上海试点 AI 新品推荐工作台前端开发需求 V1

更新时间：2026-09-08

文档状态：第一版草案，待产品、前端、后端、Harness 开发和测试共同复核。

关联文档：

```text
archive/product/2026-09-08_structure_simplification/prd/上海试点_AI新品推荐工作台_业务需求第一版.md
archive/product/2026-09-08_structure_simplification/prototypes/上海试点_AI新品推荐工作台_新品雷达Demo.html
04_algorithm_cards/business_readable/算法10_新品推荐优先级与开发需求编排_业务解读版.md
04_algorithm_cards/developer_version/算法卡_10_新品推荐优先级与开发需求编排.md
```

## 1. 文档定位

本文用于定义智慧中台内“AI 新品推荐”模块的前端开发需求，重点回答：

```text
页面有哪些模块；
每个模块展示哪些字段；
采购如何筛选、查看、追问和反馈；
页面需要支持哪些状态；
前端依赖哪些 API；
需要记录哪些埋点；
怎么验收第一版页面。
```

本文不包含视觉设计要求，视觉设计由后续设计稿单独承接。

前端只读取后端 API 和 Harness 返回结果，不直接读取 Doris 明细表，不在浏览器端重算算法 01～10。

## 2. V1 范围

| 项目 | V1 口径 |
|---|---|
| 页面名称 | AI 新品推荐 |
| 所属系统 | 智慧中台 |
| 试点城市 | 上海 |
| 目标用户 | 华东采购 |
| 业务场景 | 新品推荐 |
| 商品范围 | 试点 7 个大分类 |
| 门店范围 | 覆盖上海全部门店群 |
| 推荐来源 | 算法 10 已发布推荐结果 |
| 反馈文案 | 有帮助 / 没帮助 |
| AI 能力 | 只解释当前查询结果或当前选中推荐，不生成新推荐 |

V1 不做：

```text
非上海城市推荐；
多城市对比；
采购手工录入候选商品实时判断；
前端实时重算算法；
推荐排序人工拖拽；
历史批次切换；
导出；
供应商匹配、报价排序或新品开发审批流；
未进入算法 10 展示结果候选的“不推荐原因”追问。
```

## 3. 页面整体结构

页面采用“筛选区 + 推荐新品队列 + 单品决策档案 + AI 追问 + 反馈”的结构。

### 3.1 页面模块

| 模块 | 说明 | V1 是否必须 |
|---|---|---|
| 页面入口 | 从智慧中台菜单进入 AI 新品推荐模块 | 必须 |
| 筛选区 | 支持采购选择运营大区、城市、大分类、中分类、小分类并查询 | 必须 |
| 推荐新品队列 | 展示当前筛选条件下的推荐新品列表 | 必须 |
| 单品决策档案 | 展示当前选中推荐的详情信息 | 必须 |
| AI 追问区 | 支持采购围绕当前推荐追问原因、风险、价格和试点建议 | 必须 |
| 反馈入口 | 支持采购对单条推荐选择“有帮助 / 没帮助” | 必须 |

### 3.2 主流程

```text
用户进入页面
-> 选择运营大区、城市、大分类、中分类、小分类
-> 点击查询
-> 查看推荐新品队列
-> 点击某条推荐
-> 查看单品决策档案
-> 必要时点击快捷问题或输入问题追问
-> 对单条推荐点击“有帮助 / 没帮助”
```

## 4. 筛选区需求

### 4.1 筛选字段

| 字段 | 展示名称 | 控件类型 | 是否必选 | 默认值 | 规则 |
|---|---|---|---|---|---|
| `region_id / region_name` | 运营大区 | 单选下拉 | 否 | 全部 | 例如华东 1 区、华东 2 区、华东 3 区 |
| `city_id / city_name` | 城市 | 单选下拉 | 是 | 上海 | V1 只开放上海 |
| `major_category_id / major_category_name` | 大分类 | 单选下拉 | 是 | 空 | 只展示试点 7 个大分类 |
| `middle_category_id / middle_category_name` | 中分类 | 单选下拉 | 是 | 空 | 根据大分类级联 |
| `leaf_category_id / leaf_category_name` | 小分类 | 单选下拉 | 否 | 全部小分类 | 根据中分类级联 |

### 4.2 级联规则

```text
选择大分类后，重新加载中分类选项；
切换大分类时，清空中分类和小分类；
选择中分类后，重新加载小分类选项；
切换中分类时，清空小分类；
小分类不选时，按当前大分类 + 中分类返回全部小分类推荐。
```

### 4.3 查询规则

点击“查询”后：

```text
1. 校验城市、大分类、中分类。
2. 如果必选项缺失，不调用推荐列表 API。
3. 如果校验通过，调用推荐列表 API。
4. 查询成功后刷新推荐新品队列。
5. 查询成功且列表非空时，默认选中第一条推荐并加载详情。
6. 查询成功但列表为空时，展示无推荐状态，详情区同步展示空态。
7. 查询失败时保留当前筛选条件和上一次成功查询结果。
```

### 4.4 重置规则

点击“重置”后：

```text
1. 运营大区恢复为全部。
2. 城市恢复为上海。
3. 大分类、中分类、小分类清空。
4. 推荐新品队列清空。
5. 单品决策档案清空。
6. AI 追问上下文清空。
7. 当前页面内的反馈选中态清空。
```

重置只影响当前页面状态，不删除已经写入后端的历史反馈。

## 5. 推荐新品队列需求

### 5.1 列表展示规则

推荐新品队列展示当前筛选条件下的推荐结果。默认排序读取后端返回顺序，前端不重新计算排序。

排序口径：

```text
优先使用 recommendation_display_order 升序；
同范围内可展示 substantive_rank；
前端不根据点击、反馈或本地规则改变排序；
前端不展示 0-100 机会分，也不展示新品成功概率。
```

### 5.2 单条推荐前端持有字段

以下字段用于接口调用、详情打开、反馈和埋点，不在采购主界面作为展示内容直接露出。

| 字段 | 是否必须 | 用途 |
|---|---|---|
| `recommendation_result_id` | 必须 | 打开推荐详情、提交反馈、记录埋点 |
| `recommendation_run_id` | 必须 | 反馈和结果追溯 |
| `query_id` | 必须 | 当前查询会话追溯 |

### 5.3 单条推荐采购可见字段

| 展示项 | 字段建议 | 是否必须 | 缺失展示 |
|---|---|---|---|
| 推荐新品名称 | `display_title_text` 或 `candidate_display_name` | 必须 | 当前推荐名称缺失 |
| 商品图片 | `display_image_url`、`image_display_status`、`image_alt_text` | 条件必须 | 展示占位，不自行找外部图 |
| 推荐标签 | `recommendation_display_label`、`recommendation_display_label_text` | 必须 | 推荐状态待确认 |
| 推荐分类 | `category_level1_name`、`category_level2_name`、`leaf_category_name` | 必须 | 分类待补 |
| 一句话理由 | `display_summary_text` 或 `recommendation_summary_text` | 必须 | 推荐理由待补 |
| 适合人群 | `target_profile_name` | 条件必须 | 人群画像待补 |
| 建议价格 | `suggested_price_text` | 条件必须 | 价格待补 |
| 竞对价格 | `competitor_price_text` | 条件必须 | 暂无竞对价格 |
| 风险提示 | `risk_summary_text` | 必须 | 暂无明显风险 |
| 展示顺序 | `recommendation_display_order` | 必须 | 按接口顺序兜底 |
| 当前反馈 | `current_user_feedback` | 否 | 未反馈 |

### 5.4 推荐标签展示文案

| 后端枚举 | 前端展示 |
|---|---|
| `FORMAL_RECOMMENDATION` | 正式推荐 |
| `SEASONAL_RECOMMENDATION` | 季节推荐 |
| `LOCAL_PILOT_RECOMMENDATION` | 局部试点 |
| `EXPLORATORY_RECOMMENDATION` | 探索推荐 |
| `CONDITIONAL_RECOMMENDATION` | 条件推荐 |

前端不展示 `RETURN_FOR_REBUILD`、`REJECT` 或“不推荐”类结果。

### 5.5 点击和选中规则

```text
点击推荐卡片后，设置为当前选中推荐；
单品决策档案刷新为当前推荐详情；
AI 追问上下文同步切换到当前推荐；
当前卡片需要有选中态；
重复点击当前卡片不重复请求详情，除非详情数据不存在或已失效。
```

### 5.6 分页或加载更多

V1 支持以下任一方案，由前端和后端评审确认：

| 方案 | 说明 |
|---|---|
| 分页 | 每页默认 20 条，切页时调用列表 API |
| 加载更多 | 首次返回 20 条，点击加载更多追加结果 |

无论采用哪种方案，都必须保证曝光埋点按实际进入可视区域的推荐结果记录。

## 6. 单品决策档案需求

### 6.1 详情加载规则

```text
推荐列表首次返回非空时，默认加载第一条推荐详情；
用户点击其他推荐时，加载对应 recommendation_result_id 的详情；
详情加载中时，不清空推荐新品队列；
详情加载失败时，保留当前选中推荐，并提示详情暂时无法打开；
详情 API 返回缺失字段时，按字段缺失规则展示，不编造内容。
```

### 6.2 详情顶部字段

| 展示项 | 字段建议 | 是否必须 | 缺失展示 |
|---|---|---|---|
| 商品图片 | `display_image_url`、`image_display_status` | 条件必须 | 展示占位 |
| 推荐标签 | `recommendation_display_label_text` | 必须 | 推荐状态待确认 |
| 推荐分类 | `category_path_text` | 必须 | 分类待补 |
| 商品名称 | `display_title_text` | 必须 | 当前推荐名称缺失 |
| 推荐结论摘要 | `final_explanation_text` 或 `display_summary_text` | 必须 | 推荐结论待补 |
| 适合人群 | `target_profile_name` | 条件必须 | 人群画像待补 |
| 建议范围 | `pilot_scope_text` 或 `applicable_scope_text` | 条件必须 | 适用范围待补 |
| 建议价格 | `suggested_price_text` | 条件必须 | 价格待补 |
| 竞对价格 | `competitor_price_text` | 条件必须 | 暂无竞对价格 |

### 6.3 详情分区

详情区采用分区切换方式展示以下内容：

| 分区 | 展示目的 | 字段建议 |
|---|---|---|
| 为什么推荐 | 解释推荐成立的关键原因 | `detail_module_json.recommendation_reason` |
| 适合谁 | 解释目标用户画像和消费场景 | `detail_module_json.target_profile` |
| 价格竞对 | 解释建议价、竞对价格和价格判断 | `detail_module_json.competitor_price` |
| 风险 | 解释当前风险和待补条件 | `detail_module_json.risk_and_gate` |
| 怎么试 | 给出试点范围、注意事项和下一步动作 | `detail_module_json.pilot_suggestion` |

每个分区至少包含：

```text
一句结论；
2～4 条证据或说明；
下一步建议；
必要的风险或待补条件。
```

### 6.4 详情文案规则

前端只展示接口返回的文案，不在浏览器端生成推荐理由。

展示文案要求：

```text
使用采购能理解的大白话；
缺失信息要明确提示缺失；
不得展示新品成功概率；
不得展示无来源的口碑结论；
不得把行业趋势写成消费者口碑；
不得把条件推荐写成正式可推进。
```

## 7. AI 追问区需求

### 7.1 定位

AI 追问区用于解释当前查询结果或当前选中推荐，不作为主查询入口，不替代结构化筛选。

前端必须向 Harness 传递当前上下文：

```text
当前筛选条件；
当前查询 ID；
当前推荐结果 ID；
当前选中的详情分区；
当前用户 ID 或登录态；
```

### 7.2 快捷问题

V1 默认提供以下快捷问题：

| 快捷问题 | 意图 |
|---|---|
| 为什么值得看？ | 查询推荐理由 |
| 有什么风险？ | 查询风险和待补条件 |
| 竞对价格贵不贵？ | 查询竞对价格和价格判断 |
| 先怎么试？ | 查询试点建议 |

点击快捷问题后：

```text
1. 调用 Harness 问答接口。
2. 问题中携带当前 recommendation_result_id。
3. 回答展示在 AI 追问区。
4. 记录快捷问题点击埋点。
```

### 7.3 自由输入

输入框支持采购围绕当前推荐继续追问。

交互规则：

```text
输入为空时，不调用接口；
当前没有选中推荐时，提示先选择一条推荐；
提交后进入回答加载态；
回答成功后展示 Harness 返回文案；
回答失败时提示暂时无法回答，请稍后再试；
切换推荐后，AI 追问上下文同步切换。
```

### 7.4 Harness 回答边界

前端需要配合 Harness 做以下限制：

```text
只围绕当前已展示推荐回答；
不回答未展示候选为什么没被推荐；
不实时重算算法；
不生成新商品、新价格、新趋势、新风险；
不输出成功率、销量预测或确定性承诺；
缺数据时展示缺失，不推断机会低。
```

## 8. 反馈需求

### 8.1 反馈入口

每条推荐展示两个反馈按钮：

```text
有帮助
没帮助
```

反馈对象是一条推荐结果，不是整页查询结果。

### 8.2 反馈字段

| 字段 | 说明 | 是否必须 |
|---|---|---|
| `recommendation_result_id` | 推荐结果 ID | 必须 |
| `recommendation_run_id` | 推荐运行批次 ID，前端可不展示但提交时需携带 | 必须 |
| `query_id` | 当前查询 ID | 必须 |
| `feedback_value` | `HELPFUL` 或 `NOT_HELPFUL` | 必须 |
| `user_id` | 当前登录用户 | 必须 |
| `feedback_source` | 页面反馈或 AI 追问反馈 | 必须 |
| `filter_snapshot` | 当前筛选条件快照 | 必须 |
| `event_time` | 前端事件时间 | 必须 |

### 8.3 反馈交互

```text
点击“有帮助”后，“有帮助”进入选中态，“没帮助”取消选中；
点击“没帮助”后，“没帮助”进入选中态，“有帮助”取消选中；
同一用户对同一推荐允许修改反馈；
以后端最后一次有效反馈作为当前反馈；
反馈成功后提示已记录；
反馈失败时提示提交失败，请稍后重试；
反馈不改变推荐排序、推荐标签、推荐结论和详情文案。
```

### 8.4 反馈埋点命名建议

| 事件 | 触发时机 |
|---|---|
| `ai_selection_feedback_helpful_click` | 点击有帮助 |
| `ai_selection_feedback_not_helpful_click` | 点击没帮助 |

页面文案和新埋点统一使用“有帮助 / 没帮助”。如埋点平台确需兼容历史事件名，由埋点方案单独维护，不写入页面展示需求。

## 9. 页面状态需求

### 9.1 初始状态

```text
城市默认上海；
运营大区默认全部；
大分类、中分类、小分类为空；
推荐新品队列为空；
单品决策档案为空；
AI 追问区提示先查询或先选择推荐。
```

### 9.2 必选项缺失

触发条件：

```text
点击查询时，大分类或中分类未选择。
```

页面处理：

```text
不调用推荐列表 API；
提示补齐大分类和中分类；
保留当前筛选条件。
```

### 9.3 列表加载中

触发条件：

```text
查询请求已发出，推荐列表 API 尚未返回。
```

页面处理：

```text
查询按钮进入加载态或禁用态；
推荐新品队列展示加载状态；
不允许重复提交同一个查询；
加载失败后恢复按钮状态。
```

### 9.4 详情加载中

触发条件：

```text
用户点击推荐卡片，详情 API 尚未返回。
```

页面处理：

```text
保留当前推荐队列；
详情区展示加载状态；
详情返回后替换为对应推荐内容；
如果用户连续点击多条推荐，只展示最后一次点击对应详情。
```

### 9.5 无推荐结果

触发条件：

```text
推荐列表 API 成功返回空列表。
```

页面处理：

```text
推荐新品队列展示“当前条件下暂无新品推荐结果”；
单品决策档案展示空态；
AI 追问区不允许围绕单品追问；
不生成假推荐或兜底推荐。
```

### 9.6 推荐结果未生成

触发条件：

```text
后端返回当前筛选条件下推荐结果尚未生成。
```

页面处理：

```text
展示结果尚未生成提示；
允许用户稍后重试；
不展示后台算法细节。
```

### 9.7 接口失败

适用接口：

```text
筛选项 API；
推荐列表 API；
推荐详情 API；
反馈 API；
Harness 问答 API。
```

页面处理：

```text
展示失败提示；
允许用户重试；
保留筛选条件；
不清空上一次成功查询结果，除非用户点击重置；
记录错误埋点。
```

### 9.8 无权限

触发条件：

```text
用户无 AI 新品推荐模块权限，或无上海试点数据权限。
```

页面处理：

```text
不展示推荐数据；
提示当前无权限访问；
不调用推荐列表和详情接口；
记录权限拦截事件。
```

## 10. API 依赖

### 10.1 筛选项 API

用途：

```text
返回运营大区、城市、大分类、中分类、小分类选项。
```

前端调用时机：

```text
进入页面；
切换大分类；
切换中分类。
```

请求参数建议：

| 参数 | 是否必须 | 说明 |
|---|---|---|
| `city_id` | 否 | V1 默认上海 |
| `major_category_id` | 否 | 查询中分类时传 |
| `middle_category_id` | 否 | 查询小分类时传 |

返回字段建议：

```json
{
  "regions": [],
  "cities": [],
  "major_categories": [],
  "middle_categories": [],
  "leaf_categories": []
}
```

### 10.2 推荐列表 API

用途：

```text
按筛选条件返回推荐新品队列。
```

请求参数建议：

| 参数 | 是否必须 | 说明 |
|---|---|---|
| `region_id` | 否 | 为空表示全部运营大区 |
| `city_id` | 是 | V1 固定上海 |
| `major_category_id` | 是 | 大分类 |
| `middle_category_id` | 是 | 中分类 |
| `leaf_category_id` | 否 | 为空表示全部小分类 |
| `page_no` | 否 | 默认 1 |
| `page_size` | 否 | 默认 20 |

返回字段建议：

```json
{
  "query_id": "string",
  "items": [
    {
      "recommendation_result_id": "string",
      "recommendation_run_id": "string",
      "recommendation_display_order": 1,
      "recommendation_display_label": "FORMAL_RECOMMENDATION",
      "recommendation_display_label_text": "正式推荐",
      "display_title_text": "青椒黑椒牛柳丝 200g",
      "category_path_text": "肉禽蛋 / 牛肉制品 / 牛肉半成品",
      "display_image_url": "string or null",
      "image_display_status": "IMAGE_DISPLAY_READY",
      "image_alt_text": "string",
      "display_summary_text": "string",
      "target_profile_name": "年轻家庭",
      "suggested_price_text": "¥19.9",
      "competitor_price_text": "¥18.8-22.9",
      "risk_summary_text": "包装规格待确认",
      "pilot_scope_text": "上海 A 级门店",
      "current_user_feedback": "HELPFUL / NOT_HELPFUL / null"
    }
  ],
  "pagination": {
    "page_no": 1,
    "page_size": 20,
    "total_count": 0,
    "has_more": false
  }
}
```

### 10.3 推荐详情 API

用途：

```text
按推荐结果 ID 返回单品决策档案。
```

请求参数建议：

| 参数 | 是否必须 | 说明 |
|---|---|---|
| `recommendation_result_id` | 是 | 推荐结果 ID |
| `query_id` | 否 | 当前查询 ID，用于追溯 |

返回字段建议：

```json
{
  "recommendation_result_id": "string",
  "recommendation_run_id": "string",
  "display_title_text": "string",
  "recommendation_display_label": "FORMAL_RECOMMENDATION",
  "recommendation_display_label_text": "正式推荐",
  "category_path_text": "string",
  "display_image_url": "string or null",
  "image_display_status": "IMAGE_DISPLAY_READY",
  "final_explanation_text": "string",
  "target_profile_name": "string",
  "pilot_scope_text": "string",
  "suggested_price_text": "string",
  "competitor_price_text": "string",
  "detail_modules": {
    "recommendation_reason": {},
    "target_profile": {},
    "competitor_price": {},
    "risk_and_gate": {},
    "pilot_suggestion": {}
  },
  "current_user_feedback": "HELPFUL / NOT_HELPFUL / null"
}
```

详情模块结构建议：

```json
{
  "title": "为什么值得看",
  "summary": "一句结论",
  "evidence_points": ["证据 1", "证据 2"],
  "next_action": "下一步建议",
  "attention_item": "风险或待补条件"
}
```

### 10.4 反馈 API

用途：

```text
记录用户对单条推荐的反馈。
```

请求参数建议：

| 参数 | 是否必须 | 说明 |
|---|---|---|
| `recommendation_result_id` | 是 | 推荐结果 ID |
| `recommendation_run_id` | 是 | 推荐运行批次 ID |
| `query_id` | 是 | 当前查询 ID |
| `feedback_value` | 是 | `HELPFUL` 或 `NOT_HELPFUL` |
| `filter_snapshot` | 是 | 当前筛选条件 |

返回字段建议：

```json
{
  "success": true,
  "current_user_feedback": "HELPFUL",
  "message": "已记录"
}
```

### 10.5 Harness 问答 API

用途：

```text
围绕当前推荐结果进行大白话解释。
```

请求参数建议：

| 参数 | 是否必须 | 说明 |
|---|---|---|
| `query_id` | 是 | 当前查询 ID |
| `recommendation_result_id` | 是 | 当前推荐结果 ID |
| `question` | 是 | 用户问题或快捷问题文案 |
| `question_intent` | 否 | 快捷问题可传固定意图 |
| `filter_snapshot` | 是 | 当前筛选条件 |
| `active_detail_module` | 否 | 当前详情分区 |

返回字段建议：

```json
{
  "answer_text": "string",
  "answer_status": "SUCCESS / NO_CONTEXT / UNSUPPORTED / FAILED",
  "related_module": "recommendation_reason / risk_and_gate / competitor_price / pilot_suggestion",
  "message": "string"
}
```

## 11. 埋点需求

### 11.1 事件清单

| 事件 | 触发时机 |
|---|---|
| `ai_selection_page_view` | 进入模块页面 |
| `ai_selection_filter_change` | 筛选项变化 |
| `ai_selection_query_click` | 点击查询 |
| `ai_selection_reset_click` | 点击重置 |
| `ai_selection_result_exposure` | 推荐结果进入可视区域 |
| `ai_selection_result_click` | 点击推荐卡片 |
| `ai_selection_detail_tab_click` | 切换详情分区 |
| `ai_selection_ai_quick_question_click` | 点击 AI 快捷问题 |
| `ai_selection_ai_custom_question_submit` | 提交自定义问题 |
| `ai_selection_feedback_helpful_click` | 点击有帮助 |
| `ai_selection_feedback_not_helpful_click` | 点击没帮助 |
| `ai_selection_api_error` | API 调用失败 |
| `ai_selection_permission_block` | 权限拦截 |

### 11.2 公共埋点字段

| 字段 | 说明 |
|---|---|
| `user_id` | 当前用户 ID |
| `user_role` | 当前用户角色 |
| `session_id` | 当前会话 ID |
| `event_time` | 事件发生时间 |
| `source` | 入口来源 |
| `region_id / region_name` | 运营大区 |
| `city_id / city_name` | 城市 |
| `major_category_id / major_category_name` | 大分类 |
| `middle_category_id / middle_category_name` | 中分类 |
| `leaf_category_id / leaf_category_name` | 小分类 |
| `query_id` | 查询 ID |
| `recommendation_run_id` | 推荐运行批次 ID，前端可不展示 |
| `recommendation_result_id` | 推荐结果 ID |
| `recommendation_display_label` | 推荐标签 |
| `recommendation_display_order` | 展示顺序 |
| `page_no` | 当前页码 |

## 12. 前端缓存和请求控制

```text
筛选项可在当前页面会话内缓存；
推荐列表按完整筛选条件缓存，切换筛选条件后重新查询；
详情可按 recommendation_result_id 在当前页面会话内缓存；
用户反馈成功后，需要同步更新列表和详情中的 current_user_feedback；
连续点击推荐卡片时，以最后一次点击对应的详情响应为准；
同一个查询请求未完成时，避免重复提交。
```

## 13. 权限和安全边界

```text
无权限用户不能看到推荐列表和详情；
前端不得绕过 API 直接访问底层数据表；
前端不得在本地拼接推荐理由、成功概率或风险结论；
前端不得展示后端未返回的商品图片、价格、竞对或趋势；
前端不得把反馈结果写回算法推荐结论；
前端不得暴露给采购无关的算法字段、批次明细或系统调度信息。
```

说明：

```text
recommendation_run_id、query_id、recommendation_result_id 等字段前端需要持有，用于接口调用、反馈和埋点；
这些字段不要求在采购主界面直接展示。
```

## 14. 验收标准

### 14.1 功能验收

| 验收项 | 通过标准 |
|---|---|
| 页面入口 | 有权限用户可进入 AI 新品推荐模块 |
| 筛选项加载 | 能加载运营大区、上海、试点大分类及级联分类 |
| 必选校验 | 未选择大分类或中分类时不发起查询 |
| 查询结果 | 选择上海 + 大分类 + 中分类后能展示推荐列表或明确空态 |
| 默认选中 | 查询结果非空时默认打开第一条推荐详情 |
| 推荐切换 | 点击推荐后，详情区和 AI 上下文同步切换 |
| 详情分区 | 能切换为什么推荐、适合谁、价格竞对、风险、怎么试 |
| AI 快捷问题 | 点击快捷问题后能展示对应回答 |
| AI 自由输入 | 输入问题后能提交并展示回答或失败提示 |
| 反馈 | 有帮助 / 没帮助可点击、可切换、可回显 |
| 重置 | 重置后筛选、列表、详情和 AI 上下文回到初始状态 |

### 14.2 数据和边界验收

| 验收项 | 通过标准 |
|---|---|
| 数据范围 | 列表只返回上海试点范围推荐 |
| 推荐资格 | 不出现 `RETURN_FOR_REBUILD`、`REJECT` 或不推荐候选 |
| 排序一致 | 前端展示顺序与后端返回顺序一致 |
| 反馈不改排序 | 点击反馈后不改变推荐排序和推荐标签 |
| 缺失展示 | 缺价格、缺竞对、缺趋势、缺图片时有明确缺失展示 |
| 禁用表达 | 页面不展示成功概率、0-100 机会分、无来源口碑结论 |
| 后台字段 | 采购主界面不直接展示批次明细、算法调度或底层表字段 |

### 14.3 埋点验收

| 验收项 | 通过标准 |
|---|---|
| 页面浏览 | 进入页面记录 page_view |
| 查询 | 点击查询记录 query_click |
| 曝光 | 推荐卡片进入可视区域记录 exposure |
| 详情 | 点击推荐卡片记录 result_click 或 detail_open |
| 分区 | 切换详情分区记录 detail_tab_click |
| AI | 快捷问题和自由输入分别记录事件 |
| 反馈 | 有帮助 / 没帮助分别记录事件 |
| 异常 | 接口失败和权限拦截记录事件 |

## 15. 联调优先级

建议按以下顺序联调：

```text
1. 页面入口和权限。
2. 筛选项 API。
3. 推荐列表 API。
4. 推荐详情 API。
5. 反馈 API。
6. 埋点。
7. Harness 快捷问题。
8. Harness 自由输入。
9. 空态、异常态、无权限态。
```

前端可先使用 mock 数据完成页面和交互联调。正式验收必须切换到真实 API，并通过数据范围、推荐资格、排序、缺失展示和反馈回显验收。

## 16. 待复核点

本版前端开发前需要复核：

```text
1. 试点 7 个大分类的正式名称、编码和级联分类来源。
2. 运营大区与上海门店群映射是否由筛选项 API 直接返回。
3. 推荐列表采用分页还是加载更多。
4. 推荐详情是否由列表 API 一并返回首条详情，还是必须单独调用详情 API。
5. feedback_value 是否统一为 HELPFUL / NOT_HELPFUL。
6. 埋点事件名是否采用本文新命名；如需兼容历史事件名，由埋点方案单独说明。
7. Harness 问答是否第一版上线，还是先保留入口接 mock。
8. 图片不可展示时采用占位还是隐藏图片区域。
```

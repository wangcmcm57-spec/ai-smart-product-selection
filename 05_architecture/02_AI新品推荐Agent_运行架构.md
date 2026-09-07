# AI 新品推荐 Agent 运行架构

本文是 [01_AI选品V1_整体架构.md](01_AI选品V1_整体架构.md) 的运行详图，用来说明：

```text
算法结果表怎么进入推荐表
推荐表怎么被后端 API 读取
Harness 怎么控制 Agent
大模型什么时候参与
采购反馈怎么回流
```

它不是一张新的项目总架构图。项目总入口仍然是：

```text
05_architecture/01_AI选品V1_整体架构.md
```

## 1. 架构原则

AI 新品推荐 Agent V1 采用：

```text
工作流型 Agent + 工具调用型 Harness
```

核心边界：

```text
1. 机会表存在 Doris / 数据服务中。
2. 后端 API 读取机会表和证据表。
3. Harness 控制工具调用、参数抽取、轻量重排和安全护栏。
4. 大模型只理解问题和解释结果，不直接扫描小票重算算法。
```

## 2. 标准架构图

视觉口径采用纯飞书文档风：轻背景、白卡片、浅蓝标签、少量强调色和清晰留白，优先保证开发评审可读性。

![AI新品推荐Agent运行架构图](diagrams/ai_new_product_agent_runtime_architecture.png)

## 3. 开发怎么理解

数据开发负责：

```text
基础数据表
公共过滤与质量校验
算法 01～10 离线计算
mart_new_product_recommendation_priority 推荐优先级主表
new_product_recommendation_display_brief 展示摘要表
new_product_recommendation_explanation 自动解释表
```

后端开发负责：

```text
固定工具 / 后端 API
推荐结果查询
证据明细查询
反馈记录写入
```

Agent / 大模型负责：

```text
理解采购问题
抽取结构化参数
选择工具
解释后端返回的结构化结果
```

前端负责：

```text
采购提问入口
推荐列表和详情展示
证据、风险和试点建议展示
采购反馈入口
```

# 架构资料

本目录只放 AI 选品 V1 的架构说明和架构图图片。完整开发评审阅读顺序维护在 [00_start_here](../00_start_here/README.md)。

当前文档不直接内嵌大 PNG，避免本地 Markdown 预览器出现破图。需要看图时点击 PNG 链接，或在仓库中打开 `02_architecture/diagrams/` 下的同名图片。

## 阅读顺序

| 顺序 | 文档 | 解决的问题 |
|---|---|---|
| 01 | [01_AI选品V1_整体架构.md](01_AI选品V1_整体架构.md) | 项目从数据底座、算法主题表、机会引擎到应用层怎么分层 |
| 02 | [02_AI新品推荐Agent_运行架构.md](02_AI新品推荐Agent_运行架构.md) | 后端 API、Agent Harness、大模型和前端分别负责什么 |
| 03 | [03_AI选品V1_运行时序.md](03_AI选品V1_运行时序.md) | 离线批量产表、在线查询解释、反馈回流按什么顺序运行 |

## 文件放置规则

| 位置 | 内容 |
|---|---|
| `01_*.md` | 项目整体架构，不展开 Agent 细节 |
| `02_*.md` | Agent / Harness / API 运行架构详图 |
| `03_*.md` | 离线和在线运行时序 |
| `diagrams/` | PNG 图片生成物，不直接写说明正文 |

图片生成脚本在：

```text
tools/diagram_generation/
```

## 三张图怎么取舍

三张图有节点重叠，但用途不同，不建议再继续增加新的正式架构图。

| 图 | 是否保留 | 作用 | 和其他图的关系 |
|---|---|---|---|
| [完整架构图](diagrams/ai_selection_v1_full_architecture.png) | 保留 | 让开发先看懂项目分层：业务入口、数据底座、算法主题表、机会引擎、应用与反馈 | 覆盖全局，是第一张主图 |
| [Agent 运行架构图](diagrams/ai_new_product_agent_runtime_architecture.png) | 保留，但只给后端 / Agent / Harness 开发重点看 | 讲清后端 API、Harness、大模型、前端和反馈怎么分工 | 和完整架构图的应用层有重叠，但展开了职责边界 |
| [运行时序图](diagrams/ai_selection_v1_sequence.png) | 保留 | 讲清离线产表、在线查询、解释和反馈的先后顺序 | 节点会重复，但它回答“先做什么、谁调用谁” |

已退出当前口径、未被正文引用的历史 Harness 解释图，已移入 `archive/architecture/2026-09-08_unused_diagrams/`。它只做历史参考，不作为当前开发评审入口。

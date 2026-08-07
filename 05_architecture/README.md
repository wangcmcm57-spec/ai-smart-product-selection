# 架构资料

本目录只放 AI 选品 V1 的架构说明和架构图图片。完整开发评审阅读顺序仍维护在根目录 [README_开发评审入口.md](../README_开发评审入口.md)。

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
06_scripts/diagram_generation/
```

## 当前图片

| 图片 | 对应文档 |
|---|---|
| `diagrams/ai_selection_v1_full_architecture.png` | `01_AI选品V1_整体架构.md` |
| `diagrams/ai_new_product_agent_runtime_architecture.png` | `02_AI新品推荐Agent_运行架构.md` |
| `diagrams/ai_selection_v1_sequence.png` | `03_AI选品V1_运行时序.md` |

# AI 智能选品项目

本仓库沉淀 AI 新品推荐 V1 的正式开发材料：需求、架构、数据合同、算法卡、导读和历史溯源。

当前 V1 目标是围绕上海试点新品推荐场景，把内部经营数据、外部竞品数据和机会判断规则加工成稳定结果表，再由页面、后端 API 和 Agent 查询解释。

## 先读什么

第一次进入项目，不要从业务原文或厚算法卡开始。建议按这个顺序读：

```text
1. 00_start_here/01_项目导读.md
2. 01_product/01_requirement/01_上海试点_AI新品推荐工作台_需求说明V1.md
3. 02_architecture/01_AI选品V1_整体架构.md
4. 00_start_here/02_端到端链路导读.md
5. 00_start_here/03_算法与结果表总览.md
6. 03_data_contracts/
7. 04_algorithm_cards/developer_version/
```

最重要的边界：

```text
数据开发离线产出算法 01～10 结果表；
后端 API 读取算法 10 推荐结果和证据表；
Agent Harness 负责意图识别、参数抽取、工具路由、轻量重排和安全护栏；
大模型只解释结构化结果，不直接扫描 Doris 明细，不实时重算算法。
```

## 角色入口

| 角色 | 先看 | 目的 |
|---|---|---|
| 产品 / 项目侧 | [00_start_here/01_项目导读.md](00_start_here/01_项目导读.md)、[01_product/](01_product/README.md) | 确认 V1 范围、采购流程、页面边界和验收口径 |
| 数据开发 | [03_data_contracts/](03_data_contracts/README.md)、[04_algorithm_cards/developer_version/](04_algorithm_cards/developer_version/) | 建基础表、规则表、算法结果表和调度任务 |
| 后端 / Agent 开发 | [02_architecture/](02_architecture/README.md)、[00_start_here/03_算法与结果表总览.md](00_start_here/03_算法与结果表总览.md)、算法 10 开发版算法卡 | 明确 API、工具调用、解释和反馈边界 |
| 前端开发 | [01_product/](01_product/README.md)、[02_architecture/03_AI选品V1_运行时序.md](02_architecture/03_AI选品V1_运行时序.md)、算法 10 相关输出表 | 落推荐列表、详情、AI 追问和反馈入口 |
| 业务复核 / 溯源 | [archive/business_confirmations/](archive/business_confirmations/README.md)、[archive/source_docs/](archive/source_docs/README.md) | 追溯业务原文、承接矩阵、审阅清单和历史确认 |

## 当前架构资料

架构图不在总入口直接内嵌，避免本地 Markdown 预览器解析大图时出现破图或占屏过重。需要看图时进入对应说明文档，或直接打开 PNG。

| 文档 | 图片 | 什么时候看 |
|---|---|---|
| [整体架构](02_architecture/01_AI选品V1_整体架构.md) | [完整架构图 PNG](02_architecture/diagrams/ai_selection_v1_full_architecture.png) | 第一次理解项目分层和端到端边界 |
| [Agent 运行架构](02_architecture/02_AI新品推荐Agent_运行架构.md) | [Agent 运行架构图 PNG](02_architecture/diagrams/ai_new_product_agent_runtime_architecture.png) | 后端 / Agent / Harness 联调时看 |
| [运行时序](02_architecture/03_AI选品V1_运行时序.md) | [运行时序图 PNG](02_architecture/diagrams/ai_selection_v1_sequence.png) | 排开发顺序、联调顺序和验收链路时看 |

## 目录说明

| 目录 / 文件 | 用途 |
|---|---|
| `README.md` | 仓库总入口，只维护主阅读顺序和目录边界 |
| `AGENTS.md` | Codex 文档整理和算法卡复核规则，开发可以忽略 |
| `00_start_here/` | 第一阅读入口，包含项目导读、端到端链路导读、算法与结果表总览、单篇算法导读 |
| `01_product/` | 当前产品需求、原型、上线验收和反馈复盘 |
| `02_architecture/` | 完整架构、Agent 运行架构和运行时序 |
| `03_data_contracts/` | Doris 源表、内部基础表、外部竞品表和规则配置表字段合同 |
| `04_algorithm_cards/` | 业务解读版、开发版算法卡和算法文档输出规范 |
| `tools/` | 可复用脚本，例如架构图生成脚本 |
| `examples/` | 脱敏或人造样例数据 |
| `archive/` | 历史材料、过程复核材料、旧原型、业务原文和已退出主路径的评审资料 |
| `local_only/` | 本地个人真实数据和临时验证结果，不进入 Git |

## 仓库边界

放入 Git 的内容：

- 当前需求说明、原型和验收口径
- 架构图、运行时序和 Agent 边界
- 数据合同、规则表合同和开发版算法卡
- 业务解读版和导读材料
- 可复用脚本
- 脱敏或人造样例数据

不放入 Git 的内容：

- 真实 Excel 业务导出
- 真实 CSV 明细或分析结果
- Doris 查询结果明细
- 久谦 API 原始返回数据
- PDF 原始资料
- 临时截图和运行输出
- Python 依赖包和缓存

规则标准导入包评审期临时放在 `03_data_contracts/rule_tables/import_ready/`，方便开发直接拿 `csv/` 落 Doris。评审完成后再移出 Git，长期只保留规则表字段合同、导入映射说明和可复用脚本。

## 当前项目原则

1. V1 聚焦上海试点新品推荐，不做门店订货、独立毛利分析或购物篮提升产品。
2. 开发先看需求、架构和导读，再下钻到数据合同和算法卡。
3. 业务原始文档只做溯源，不让开发从原文自行猜口径。
4. 每个算法卡独立成文档，最终面向数据开发落地。
5. V1 暂不纳入供应商基础表、库存损耗明细表、促销优惠券明细表。

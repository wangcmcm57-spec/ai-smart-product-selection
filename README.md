# AI 智能选品项目

本仓库用于沉淀 AI 新品推荐项目中可以协作、评审和开发落地的确定性材料。

当前 V1 目标是：围绕采购新品推荐场景，基于 Doris 基础数据、业务算法规则、外部竞品数据和机会评分逻辑，形成可被采购使用的 AI 选品能力。

## 给开发的快速入口

开发第一次进入项目时，先建立背景、架构和运行方式，再进入开发评审材料：

```text
README.md
05_architecture/AI选品V1_完整架构图.md
05_architecture/AI选品V1_运行时序图.md
README_开发评审入口.md
00_project_management/development_review/AI选品V1_当前开发链路.md
02_data_contracts/
00_project_management/development_review/算法01-06_结果表总览.md
03_algorithm_cards/developer_version/算法卡_01_会员画像.md
03_algorithm_cards/developer_version/算法卡_02_门店品类等级.md
03_algorithm_cards/developer_version/算法卡_03_门店群消费者画像贡献.md
00_project_management/development_review/AI选品V1_开发评审问题清单.md
```

## 开发怎么读这个仓库

开发第一次打开仓库时，按下面顺序理解项目，不需要从业务原始文档开始读。

| 顺序 | 看什么 | 文件位置 | 读完要知道什么 |
|---|---|---|---|
| 1 | 项目背景和仓库地图 | [README.md](README.md) | V1 做什么、仓库里每个目录干什么 |
| 2 | 完整架构 | [AI选品V1_完整架构图.md](05_architecture/AI选品V1_完整架构图.md) | 数据、算法、机会引擎、Agent、反馈怎么串起来 |
| 3 | 运行时序 | [AI选品V1_运行时序图.md](05_architecture/AI选品V1_运行时序图.md) | 离线产表、在线查询解释、反馈回流怎么跑 |
| 4 | 开发评审入口 | [README_开发评审入口.md](README_开发评审入口.md) | 本次评审范围、开发阅读顺序、会议方式 |
| 5 | 第一批开发链路 | [AI选品V1_当前开发链路.md](00_project_management/development_review/AI选品V1_当前开发链路.md) | 第一批先做基础数据表和算法 01～03 |
| 6 | 基础数据合同 | [02_data_contracts/](02_data_contracts/README.md) | 需要准备哪些基础表、每张表字段和粒度是什么 |
| 7 | 结果表总览 | [算法01-06_结果表总览.md](00_project_management/development_review/算法01-06_结果表总览.md) | 基础数据表、01～06 会产出哪些正式表和关键表 |
| 8 | 开发版算法卡 | [03_algorithm_cards/developer_version/](03_algorithm_cards/developer_version/) | 每个算法怎么建表、取字段、算指标、验收 |
| 9 | 评审问题清单 | [AI选品V1_开发评审问题清单.md](00_project_management/development_review/AI选品V1_开发评审问题清单.md) | 评审会上要确认哪些结论和行动项 |

第一批开发不是直接从算法 01 开始。数据开发需要先确认并准备基础数据表：

```text
Doris 小票商品明细
dim_store 门店基础表
dim_sku 商品基础表
dim_city_algorithm_region 城市算法区域映射表
mart_sku_margin_loss 毛利损耗表
mart_store_sku_daily_price 门店商品日价格表
mart_store_sku_daily_sale_order_status 门店商品每日可订可售表
```

当前 V1 完整架构图：

![AI选品V1完整架构图](05_architecture/diagrams/ai_selection_v1_full_architecture.png)

当前 V1 运行时序图：

![AI选品V1运行时序图](05_architecture/diagrams/ai_selection_v1_sequence.png)

开发理解重点：

```text
数据开发先准备基础数据表和公共过滤逻辑，再产出正式算法结果表；
后端和 Agent 读取结果表，做查询、证据组装和解释；
大模型不直接扫描小票实时计算算法。
```

## 仓库边界

放入 Git 的内容：

- 项目计划、待办、业务确认材料
- 业务原始算法规则的 Markdown 溯源材料
- 基础表、外部表、Doris 表的数据合同
- 给数据开发使用的算法卡
- 给业务和产品理解使用的业务解读版
- 架构图、时序图、运行流程图
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

## Git 目录说明

| 目录 / 文件 | 给谁看 | 用途 |
|---|---|---|
| `README.md` | 全体 | 仓库总入口，说明项目目标、目录边界和开发快速入口 |
| `README_开发评审入口.md` | 开发 / 产品 / 项目侧 | SDD 开发评审入口，说明读文档顺序和评审方式 |
| `AGENTS.md` | Codex | 文档整理和算法卡复核规则，开发可以忽略 |
| `00_project_management/` | 产品 / 项目侧 / 开发评审 | 项目计划、业务确认、开发评审资料 |
| `00_project_management/development_review/` | 开发 / 产品 / 项目侧 | SDD 评审包：开发链路、结果表总览、评审问题清单 |
| `00_project_management/business_confirmations/` | 产品 / 业务 / 项目侧 | 业务原文承接矩阵、审阅清单、口径确认材料 |
| `01_source_docs/` | 产品 / 算法 / 需要溯源的人 | 业务原始与补充算法文档，只做溯源，不让开发自行猜口径 |
| `02_data_contracts/` | 数据开发 | 基础表、外部表、Doris 表字段合同；第一批开发必须先看 |
| `03_algorithm_cards/developer_version/` | 数据开发 | 开发版算法卡，按表、字段、公式、调度和验收落地 |
| `03_algorithm_cards/business_readable/` | 业务 / 产品 / 采购 / 开发评审 | 业务解读版，帮助理解算法目的和业务含义 |
| `04_product/` | 产品 / 前后端 / Agent | 产品需求、业务流程、原型资料 |
| `05_architecture/` | 开发 / 产品 / 项目侧 | 完整架构图、运行时序图、运行设计 |
| `06_scripts/` | 开发 / Codex | 可复用脚本，例如架构图生成脚本 |
| `07_examples/` | 开发 / 测试 | 脱敏或人造样例数据 |
| `local_only/` | 本地个人使用 | 真实业务数据、临时验证结果，不进入 Git |

说明：真实业务数据、本地导出文件和临时验证结果可以放在本机 `local_only/` 目录，但该目录不进入 Git。

## 当前项目原则

1. 业务原始文档只做溯源，不直接改写。
2. 每个算法卡独立成文档，最终面向数据开发落地。
3. 算法卡需要同时具备业务可理解性和开发可执行性。
4. V1 暂不纳入供应商基础表、库存损耗明细表、促销优惠券明细表。
5. V1 聚焦新品推荐，不做毛利分析和购物篮提升产品能力。

# AI 选品 V1 开发评审入口

本文是数据开发、后端开发、Agent 开发和产品侧进入 AI 选品 V1 开发评审的统一入口。

评审不逐页朗读算法卡，而是确认：

```text
谁要建什么表
谁要写什么任务
谁要提供什么 API
哪些口径会阻塞 V1
哪些内容只做预审或后续排期
```

## 0. 先看这 5 句话

1. AI 选品 V1 是给采购做新品开发推荐，不是给门店做订货，也不是做独立毛利分析或购物篮提升产品。
2. 算法 01～10 已整理为开发版算法卡，当前评审口径应按完整 V1 链路理解。
3. 开发仍建议分阶段实施：先数据合同和公共过滤，再 01～03，再 04～07，再 08～10，最后后端 API、Agent 和前端联调。
4. 后端和 Agent 在线查询只读取算法 10 的推荐结果表、展示摘要表、解释表和证据快照，不在采购提问时实时重算算法。
5. 真实业务 Excel、CSV、Doris 明细和外部 API 原始返回不进入正式 Git；规则数据首版可本地暂存，开发优先使用标准 CSV 落 Doris。

一句话描述：

```text
AI 选品 V1 = 离线把新品机会算成表，在线让采购通过页面或 Agent 查询“哪些新品方向值得做、为什么、价格和风险是什么”。
```

## 1. 本次开发评审到底评什么

本次评审对象是完整 V1 规格，不再只看算法 01～03。排期可以分阶段，但文档阅读和依赖判断需要按 01～10 完整链路处理。

| 阶段 | 范围 | 评审结论要回答什么 |
|---|---|---|
| P0 | 数据合同和公共底座 | Doris 小票、门店、商品、商品状态、城市算法区域、毛利损耗、日价格、可订可售、外部竞品和规则配置表是否能按合同产出 |
| P0 | 公共过滤和版本血缘 | 有效交易、退款退货、负金额、负重量、字段关联、调度批次和版本包怎么统一 |
| P1 | 算法 01～03 | 是否能产出会员画像、门店品类等级、门店群消费者画像贡献三类上游正式表 |
| P2 | 算法 04～06 | 是否能产出 SKU 表现、价格带、候选价格可行性、购物篮关联和内部新品候选 |
| P3 | 算法 07 | 外部竞品、趋势、图片、公开证据、风险线索和外部候选是否能按字段合同和来源授权落表 |
| P4 | 算法 08～09 | 是否能完成候选标准化合并、09 输入快照、机会证据合成和风险门禁 |
| P5 | 算法 10 | 是否能输出推荐优先级主表、展示摘要、解释、范围汇总和审计表 |
| 联调 | 后端 API / Agent Harness / 前端 | 是否按算法 10 结果表查询、解释、展示和记录反馈 |

特别注意：

```text
算法 05 的内部价格带和候选价格可行性可在算法 04 后先算。
算法 05 的竞对价格验证部分需要读取算法 07 的可比竞对对象和外部价格快照后再补齐。
算法 08 读取 04/05/06/07 的候选和证据，算法 09 读取 08，算法 10 读取 09。
```

## 2. 各角色要准备什么

| 角色 | 本次要做 | 本次不用做 |
|---|---|---|
| 数据开发 | 确认基础表、外部表、规则表字段、主键、粒度、调度周期和算法 01～10 结果表建设路径 | 不需要从业务原始文档自行猜字段口径 |
| 后端开发 | 评审推荐查询、详情查询、证据查询、反馈写入和请求日志 API 边界 | 不需要让 API 实时扫描 Doris 明细或重算离线算法 |
| Agent / Harness 开发 | 评审意图识别、参数抽取、工具路由、轻量重排、大模型解释和禁止边界 | 不需要让大模型直接读取明细表或编造未返回证据 |
| 前端开发 | 理解推荐列表、详情、证据、风险、试点建议和反馈入口要读取哪些结果表 | 不需要把算法公式搬到前端实现 |
| 产品 / 项目侧 | 确认评审范围、业务口径负责人、字段缺口、会后行动项和验收节奏 | 不在评审会上临时新增算法规则 |

## 3. 开发阅读顺序

第一次接触项目的人，先按下面顺序读。不要从业务原始文档开始猜口径。

```text
1. README.md
2. README_开发评审入口.md
3. 00_project_management/development_review/quick_read/
4. 05_architecture/01_AI选品V1_整体架构.md
5. 05_architecture/02_AI新品推荐Agent_运行架构.md
6. 05_architecture/03_AI选品V1_运行时序.md
7. 00_project_management/development_review/AI选品V1_当前开发链路.md
8. 02_data_contracts/
9. 00_project_management/development_review/算法01-10_结果表总览.md
10. 00_project_management/development_review/AI选品V1_开发评审问题清单.md
11. 03_algorithm_cards/developer_version/算法卡_01_会员画像.md
12. 03_algorithm_cards/developer_version/算法卡_02_门店品类等级.md
13. 03_algorithm_cards/developer_version/算法卡_03_门店群消费者画像贡献.md
14. 03_algorithm_cards/developer_version/算法卡_04_目标画像SKU表现.md
15. 03_algorithm_cards/developer_version/算法卡_05_目标画像商品价格带.md
16. 03_algorithm_cards/developer_version/算法卡_06_目标画像购物篮新品关联.md
17. 03_algorithm_cards/developer_version/算法卡_07_竞品与全球外部趋势新品发现.md
18. 03_algorithm_cards/developer_version/算法卡_08_新品候选标准化与合并.md
19. 03_algorithm_cards/developer_version/算法卡_09_新品机会证据合成与风险门禁.md
20. 03_algorithm_cards/developer_version/算法卡_10_新品推荐优先级与开发需求编排.md
```

按角色可以这样读：

| 角色 | 必读 | 可先扫读 |
|---|---|---|
| 数据开发 | `02_data_contracts/`、`算法01-10_结果表总览.md`、10 张开发版算法卡、评审问题清单 | 架构 02、03 和业务解读版 |
| 后端 / Agent 开发 | 架构 01～03、算法 10 开发版算法卡、评审问题清单里的 API / Agent 问题 | 算法 08、09 开发版算法卡和结果表总览 |
| 产品 / 项目侧 | 本入口、架构 01～03、当前开发链路、评审问题清单、业务解读版 | 开发版字段明细 |

## 4. 当前正式算法链路

```text
01 会员画像
02 门店品类等级
03 门店群消费者画像贡献
04 目标画像 SKU 表现
05 目标画像商品价格带
06 目标画像购物篮新品关联
07 竞品与全球外部趋势新品发现
08 新品候选标准化与合并
09 新品机会证据合成与风险门禁
10 新品推荐优先级与开发需求编排
```

当前正式后段顺序：

```text
算法 04/05/06/07 -> 算法 08 -> 算法 09 -> 算法 10
```

推荐查询主入口：

| 使用场景 | 主要读取表 | 说明 |
|---|---|---|
| 推荐列表 | `mart_new_product_recommendation_priority` + `new_product_recommendation_display_brief` | 只读最新成功推荐批次，按区域、城市、品类、门店等级、消费者画像等筛选 |
| 推荐详情 | `new_product_recommendation_display_brief` + `new_product_recommendation_explanation` | 通过 `recommendation_result_id` 查询详情模块和解释文本 |
| Agent 解释 | `new_product_recommendation_explanation` + `new_product_recommendation_input_snapshot` + `new_product_recommendation_evidence_dimension` | 解释为什么推荐，不改推荐结果 |
| 批次和审计 | `new_product_recommendation_run` + `new_product_recommendation_audit` | 查看批次状态、异常、文案回退、图片隐藏和输入对账 |

## 5. 会前准备清单

数据开发会前需要准备：

1. 基础表、外部表、规则表是否能按 `02_data_contracts/` 产出。
2. 每张表的实际来源系统、字段映射、主键粒度、调度周期和历史回溯周期。
3. 小票有效交易过滤口径是否可落地。
4. 算法 01～10 每张结果表是否能按开发版算法卡建表。
5. 当前阻塞字段、口径、样本周期、数据质量和调度依赖问题。

后端 / Agent 开发会前需要准备：

1. 推荐列表、推荐详情、证据查询、反馈写入、请求日志 API 的疑问。
2. 是否以 `mart_new_product_recommendation_priority` 作为推荐列表主查询入口。
3. Agent Harness 参数抽取、工具路由、轻量重排的边界疑问。
4. 大模型解释层的禁止规则、事实校验和日志记录疑问。

产品 / 项目侧会前需要准备：

1. 认可完整 V1 评审范围，但开发排期按阶段推进。
2. 明确业务口径确认人，例如毛利、损耗、区域、商品状态、价格点、规则配置和图片授权。
3. 会后任务拆分、负责人和验收节奏。

## 6. 建议评审方式

| 时间 | 内容 | 目标 |
|---|---|---|
| 0～10 分钟 | V1 目标和完整链路 | 确认 01～10 都是 V1 规格，开发分阶段实施 |
| 10～25 分钟 | 数据合同和真实数据交付边界 | 确认基础表、外部表、规则表、标准 CSV 和真实数据不进 Git |
| 25～40 分钟 | 公共过滤、版本和调度 | 确认有效交易过滤、批次、版本包和质量验收 |
| 40～60 分钟 | 算法 01～03 | 确认画像、等级、画像贡献三张上游主题能力 |
| 60～80 分钟 | 算法 04～07 | 确认 SKU 表现、价格、购物篮、外部竞品趋势和 05/07 协作边界 |
| 80～100 分钟 | 算法 08～10 | 确认候选标准化、门禁、推荐展示和排序结果 |
| 100～115 分钟 | 后端 API / Agent / 前端 | 确认读取算法 10 表、解释边界和反馈日志 |
| 115～120 分钟 | 会后行动项 | 明确谁建表、谁写调度、谁对字段、谁补口径 |

评审会上不要做：

```text
不逐页朗读业务解读版。
不让开发从业务原始文档自己猜实现口径。
不把采购前端查询条件写成采购手动输入算法事实。
不让大模型直接读 Doris 明细或实时重算算法。
不在评审会上临时新增算法规则。
```

## 7. 会后输出物

| 输出物 | 负责人 | 用途 |
|---|---|---|
| 基础数据表开发任务清单 | 数据开发 | 明确基础表建表、字段映射、主键验收和调度任务 |
| 规则表和标准 CSV 落库方案 | 数据开发 / 项目侧 | 明确首版标准 CSV 如何落 Doris，后续业务标准 Excel 如何更新 |
| 公共有效交易过滤方案 | 数据开发 | 统一后续算法输入口径 |
| 算法 01～10 开发任务拆分 | 数据开发 | 按依赖拆建表、调度、试跑和验收 |
| 字段口径确认清单 | 数据开发 / 业务 / 财务口径负责人 | 解决阻塞字段 |
| 后端 API / Agent Harness 预审问题 | 后端 / Agent 开发 | 标注接口、工具调用、轻量重排、日志反馈的待确认点 |
| 试跑验收方案 | 数据开发 / 业务 | 建议先用上海或华东范围试跑对数 |

## 8. Codex 预审 Prompt

开发可以让 Codex 先读取仓库并输出预审结果。

### 8.1 数据开发预审 Prompt

```text
请你作为数据开发，阅读本仓库：

1. 先读 README.md 和 README_开发评审入口.md，理解项目目标、仓库结构和完整 V1 评审范围。
2. 再读 05_architecture/01_AI选品V1_整体架构.md、05_architecture/02_AI新品推荐Agent_运行架构.md 和 05_architecture/03_AI选品V1_运行时序.md。
3. 再读 00_project_management/development_review/AI选品V1_当前开发链路.md。
4. 再读 02_data_contracts/。
5. 再读 00_project_management/development_review/算法01-10_结果表总览.md。
6. 再按算法顺序读 03_algorithm_cards/developer_version/ 下 01～10 的开发版算法卡。
7. 最后读 00_project_management/development_review/AI选品V1_开发评审问题清单.md。

请输出：
1. 你理解的 V1 开发目标和离线/在线边界。
2. 基础表、外部表、规则表和公共过滤需要建设什么。
3. 算法 01～10 每张正式表的输入来源、主键、调度依赖和验收风险。
4. 哪些字段或规则会阻塞开发。
5. 你建议的分阶段开发任务拆分。
```

### 8.2 后端 / Agent 开发预审 Prompt

```text
请你作为后端和 Agent 开发，阅读本仓库：

1. 先读 README.md 和 README_开发评审入口.md，理解项目目标、仓库结构和完整 V1 评审范围。
2. 再读 05_architecture/01_AI选品V1_整体架构.md。
3. 再读 05_architecture/02_AI新品推荐Agent_运行架构.md。
4. 再读 05_architecture/03_AI选品V1_运行时序.md。
5. 再读 03_algorithm_cards/developer_version/算法卡_10_新品推荐优先级与开发需求编排.md。
6. 再读 00_project_management/development_review/AI选品V1_开发评审问题清单.md。

请重点判断：
1. 后端需要提供哪些固定查询 API。
2. Agent Harness 需要调用哪些工具。
3. 采购自然语言问题如何转成结构化参数。
4. 推荐列表是否读取 mart_new_product_recommendation_priority 和 new_product_recommendation_display_brief。
5. 推荐详情和解释如何读取 new_product_recommendation_explanation、input_snapshot 和 evidence_dimension。
6. 在线轻量重排应该发生在哪里。
7. 大模型可以做什么，禁止做什么。
8. 请求日志和采购反馈应该怎么记录。
```

## 9. 后续维护规则

本文只维护“开发评审怎么进入、当前评审范围是什么、各角色要准备什么”。不要把算法公式、字段明细、业务原文或接口细节继续堆进本文。

后续每次项目状态变化时，只更新下面几类内容：

| 变化场景 | 本文需要更新什么 | 细节应该放哪里 |
|---|---|---|
| 数据合同或规则表变化 | 第 1、3、5、8 节 | `02_data_contracts/` |
| 算法卡状态变化 | 第 1、3、4、8 节 | `03_algorithm_cards/developer_version/` |
| 推荐结果表或后端 API 定稿 | 第 2、4、5、7、8 节 | 算法 10 开发版算法卡和后续 API 合同 |
| Agent Harness 规则定稿 | 第 0、2、6、8 节 | `05_architecture/` 或后续 Agent 运行规则文档 |
| 评审阶段变化 | 第 1、6、7 节 | `00_project_management/development_review/AI选品V1_当前开发链路.md` |

维护边界：

```text
README_开发评审入口.md：只放导航、状态、分工、评审方式。
02_data_contracts/：只放基础表、外部表、Doris 源表事实和规则配置表字段合同；真实业务导出和未脱敏明细不放入 Git。
03_algorithm_cards/developer_version/：只放算法怎么计算、怎么建表、怎么验收。
05_architecture/：只放整体架构、Agent 运行架构和运行时序。
00_project_management/development_review/：只放当前开发链路、结果表总览和评审问题清单。
```

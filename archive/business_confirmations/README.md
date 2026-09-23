# 业务确认材料归档

本目录只放算法整理过程中的业务确认、内部审阅和溯源材料。当前它已经退出开发主阅读路径，只作为历史追溯和项目内部复核依据。

自 2026-09-23 起，`source_traceability/` 和 `review_checklists/` 中的既有文件统一冻结归档：保留、不删除，但不再随算法卡日常修复同步更新，也不再要求为新算法或新修改创建同类文件。只有用户明确要求专项审计或原始业务文档重大改版时，才临时恢复这两类材料。

为了避免所有文件堆在根目录，这里按用途拆成四个子目录：

| 子目录 | 给谁看 | 放什么 | 使用方式 |
|---|---|---|---|
| `pending_items/` | 业务 / 产品 / 项目侧 | 需要业务补充、复核或确认的事项 | 优先给业务看 |
| `review_checklists/` | 你 / 项目侧复核人 | 已冻结的历史审阅清单和红线记录 | 仅历史追溯，不再日常维护 |
| `source_traceability/` | 你 / 项目侧复核人 | 已冻结的业务原文承接矩阵 | 仅历史追溯，不再日常维护 |
| `delivery_checks/` | 项目侧 / Codex | 输出前逐项核对、交付前复核结论、早期归档核对 | 判断哪些版本可交付，避免旧结论误导 |

## 业务优先看

当前需要业务或项目侧集中复核的文件：

```text
archive/business_confirmations/pending_items/算法05-08_业务待确认事项汇总.md
archive/business_confirmations/pending_items/算法09_业务待确认事项汇总.md
archive/business_confirmations/pending_items/算法10_业务待确认事项汇总.md
archive/business_confirmations/delivery_checks/算法卡全量复核与修复记录_2026-09-07.md
```

业务不需要逐份阅读 `source_traceability/` 和 `review_checklists/`。当前正式口径以业务解读版、开发版算法卡和数据合同为准。

## 开发是否需要看

开发主入口仍然是：

```text
README.md
00_start_here/
03_data_contracts/
04_algorithm_cards/developer_version/
```

本目录不是开发主交付目录。只有当评审会上需要追溯历史口径为什么这样写时，才回到本目录查看冻结的承接矩阵或审阅记录。

# 业务确认材料

本目录只放算法整理过程中的业务确认、内部审阅和溯源材料。

为了避免所有文件堆在根目录，这里按用途拆成四个子目录：

| 子目录 | 给谁看 | 放什么 | 使用方式 |
|---|---|---|---|
| `pending_items/` | 业务 / 产品 / 项目侧 | 需要业务补充、复核或确认的事项 | 优先给业务看 |
| `review_checklists/` | 你 / 项目侧复核人 | 每个算法的审阅清单和红线问题 | 内部复核用，不是开发任务清单 |
| `source_traceability/` | 你 / 项目侧复核人 | 业务原文承接矩阵 | 证明业务原文没有漏掉、删掉或改写 |
| `delivery_checks/` | 项目侧 / Codex | 输出前逐项核对、交付前复核结论、早期归档核对 | 判断哪些版本可交付，避免旧结论误导 |

## 业务优先看

当前需要业务或项目侧集中复核的文件：

```text
00_project_management/business_confirmations/pending_items/算法05-08_业务待确认事项汇总.md
00_project_management/business_confirmations/pending_items/算法09_业务待确认事项汇总.md
00_project_management/business_confirmations/pending_items/算法10_业务待确认事项汇总.md
00_project_management/business_confirmations/delivery_checks/算法卡全量复核与修复记录_2026-09-07.md
```

业务不需要逐份阅读 `source_traceability/` 和 `review_checklists/`。这两类文件主要是我们内部保证算法卡没有漏承接、没有混入错误口径。

## 开发是否需要看

开发主入口仍然是：

```text
README_开发评审入口.md
03_algorithm_cards/developer_version/
02_data_contracts/
```

本目录不是开发主交付目录。只有当评审会上需要追溯某个口径为什么这样写时，才回到本目录查看承接矩阵或审阅记录。

# 外部批次输入锁定清单

## 1. 表定位、粒度和主键

正式表名：`mart_external_batch_input_manifest`。

用途：记录算法 07 每次实际运行读了哪些原始快照、标准证据和当批解释规则，选了哪个来源修订、排除了哪些重复/不适用证据，支持同批重跑及源数据修正审计。不能将所有采集成功批次一起汇总。

一行代表：一个统一算法批次的一次运行，对一条标准证据的输入选择或排除记录。

主键：`algorithm_batch_version + run_id + evidence_id`。同一次运行内，`algorithm_batch_version + run_id + observation_key` 最多一条 `selection_status = SELECTED`；非选中修订仍落 SUPERSEDED/EXCLUDED 留痕。

`run_id` 只区分真实运行，不是业务版本。正式读取先由算法 07 发布记录定位当前 BATCH 的完整成功运行，再读取该运行 SELECTED 集合；不得把多个运行结果相加。无任何标准证据的来源通过 `external_trend_run.source_snapshot_json` 记录失败/缺失和预期范围，本表不伪造空证据 ID。

本合同定义输入发布与重跑要求，生产调度、原子发布及实际数据覆盖仍需开发验收；不宣称服务器当前已具备该清单。

## 2. 完整字段合同

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 统一算法批次版本 | `algorithm_batch_version` | varchar(32) | 必须 | 全链路调度 | 唯一业务版本，固定 `BATCH_YYYYMM` |
| 计算结束日期 | `calculation_end_date` | date | 必须 | 全链路调度 | 对应 YYYYMM 自然月月末 |
| 运行 ID | `run_id` | varchar(64) | 必须 | 调度生成 | 本次真实运行，不能拼入 BATCH 值 |
| 执行方式 | `execution_mode` | varchar(32) | 必须 | 调度运行清单 | 首次初始化、原清单重跑或源数据修正 |
| 首次锁定锚点运行 ID | `locked_input_run_id` | varchar(64) | 必须 | 原批次首次锁定清单 | 首次运行写自身；重跑/修正始终指向最初规则/区域锁定锚点，不表示本次输入必然退回首次集合 |
| 输入基线运行 ID | `input_baseline_run_id` | varchar(64) | 必须 | 调度读取当前完整已发布清单 | 首次写自身；REPLAY/SOURCE_CORRECTION 默认以当前完整已发布运行作为父清单；明确历史重放需登记指定历史父清单及原因 |
| 证据 ID | `evidence_id` | varchar(128) | 必须 | `dwd_external_evidence_normalized.evidence_id` | 本次被评估选择的证据 |
| 观测业务键 | `observation_key` | varchar(128) | 必须 | `dwd_external_evidence_normalized.observation_key` | 对应同源同市场同数据期同商品同指标及统计维度的观测 |
| 来源 ID | `source_id` | varchar(128) | 必须 | `dwd_external_evidence_normalized.source_id` | 来源稳定标识 |
| 数据集 ID | `dataset_id` | varchar(128) | 必须 | `dwd_external_evidence_normalized.dataset_id` | 原始报表/接口 |
| 来源市场 | `source_market` | varchar(64) | 必须 | `dwd_external_evidence_normalized.source_market` | 区分市场，不能跨市场任意替代 |
| 原始快照 ID | `raw_snapshot_id` | varchar(128) | 必须 | `dwd_external_evidence_normalized.raw_snapshot_id` | 本次证据原始响应 |
| 采集批次号 | `collection_batch_id` | varchar(128) | 必须 | `dwd_external_evidence_normalized.collection_batch_id` | 来源技术批次 |
| 原始内容哈希 | `payload_hash` | varchar(64) | 必须 | `ods_external_source_raw_snapshot.payload_hash` | 验证原始快照没有被改写 |
| 标准证据内容哈希 | `evidence_hash` | varchar(64) | 必须 | 输入锁定步骤 M3 生成 | 对除 run_id/updated_at 外全部标准证据业务字段做规范 JSON SHA-256；被哈希的标准证据不含 evidence_hash 字段，不含自指 |
| 标准证据快照 | `evidence_snapshot_json` | json | 必须 | 输入锁定步骤 M3 复制 | 对象，保存本次证据完整业务字段及字段名，供历史复现；不只存 ID |
| 质量问题快照 | `quality_issues_snapshot_json` | json | 必须 | `mart_external_evidence_quality_issue` 本次证据问题记录 | 对象数组，保存问题完整业务字段、状态和依据，按字段名/问题代码排序；无问题写 `[]`；历史复现不读当前问题状态 |
| 质量问题快照哈希 | `quality_issues_hash` | varchar(64) | 必须 | 输入锁定步骤 M3 生成 | 对质量问题快照除 run_id/detected_at/checked_at 外的业务字段规范化 SHA-256；数组内不含 quality_issues_hash 自身；来源数据日期及依据参与哈希 |
| 选择状态 | `selection_status` | varchar(32) | 必须 | 输入锁定步骤 M2 | 选中、被同观测有效修订替代或排除 |
| 选择原因 | `selection_reason` | varchar(1024) | 必须 | 输入锁定步骤 M2 | 解释命中策略、排除原因或原清单复用，不用“最新成功”代替依据 |
| 来源修订标识 | `source_revision_id` | varchar(256) | 可选 | 原始响应来源修订元数据 | 来源真实提供的修订号，仅作追溯；没有时 NULL，不造业务版本 |
| 来源修订时间 | `source_revised_at` | datetime | 可选 | `dwd_external_evidence_normalized.source_revised_at` | UTC，未知时 NULL；不能当交易日 |
| 外部采集截止时间 | `external_data_cutoff` | datetime | 必须 | 原批次调度锁定 | UTC；本次正常输入采集边界，重跑保持原值；源修正例外须单独留痕 |
| 来源回看窗口开始日期 | `input_window_start` | date | 必须 | 原批次调度按来源/数据集锁定 | 该来源本次可计算数据期的左闭边界，不同来源可用不同长度回看窗口；重跑保持原值 |
| 来源回看窗口结束日期 | `input_window_end` | date | 必须 | 原批次调度 | 与 calculation_end_date 相同的完整月月末；不是来源最后一次真实观测日 |
| 证据时间类型 | `evidence_time_type` | varchar(32) | 必须 | 标准化步骤E4按来源物理时间含义判定 | 四分支读取；不把静态属性强制转成交易期 |
| 零售观测时间 | `observed_at` | datetime | 条件必须 | 原始零售响应的实际快照时点/本次采集观测 | UTC；RETAIL_OBSERVATION必填，采集可证明当时可见，不证明交易发生日 |
| 数据期开始日期 | `data_period_start` | date | 可选 | `dwd_external_evidence_normalized.data_period_start` | 真实数据期，未知时 NULL，不按 cutoff 猜测 |
| 数据期结束日期 | `data_period_end` | date | 可选 | `dwd_external_evidence_normalized.data_period_end` | 真实数据期，不是采集日 |
| 本批次解释规则快照 | `interpretation_rules_snapshot_json` | json | 必须 | `dim_external_evidence_interpretation_rule` 当批冻结记录 | 对象数组，每项含 rule_id、rule_type、rule_hash、effective_start_date、effective_end_date、basis_url、basis_hash、完整适用条件及输出参数；无规则写 `[]` |
| 解释规则集合哈希 | `interpretation_rules_hash` | varchar(64) | 必须 | 输入锁定步骤 M1 生成 | 对本批次适用规则完整快照按 rule_id 排序后做 SHA-256，空数组也计算哈希；重跑/源修正保持原集合 |
| 原有规则资产追溯快照 | `upstream_rule_assets_snapshot_json` | json | 必须 | 当批规则/字典运行锁定 | 对象数组，每项含来源表、源资产 ID 或源自身版本值、业务键、内容哈希、生效期和实际记录；属性/分类/命名等仅追溯，不成为第二套结果版本 |
| 原有规则资产集合哈希 | `upstream_rule_assets_hash` | varchar(64) | 必须 | 输入锁定步骤 M1 生成 | 对排序后完整规则资产快照计算 SHA-256，重跑/源修正保持原值 |
| 区域快照哈希 | `region_snapshot_hash` | varchar(64) | 必须 | `dim_algorithm_batch_city_region_snapshot` 本批次记录 | 对当批全部城市区域业务字段按 city 排序计算 SHA-256；不得重取当前映射 |
| 修订选择规则 ID | `revision_rule_id` | varchar(128) | 可选 | 已锁定 `REVISION` 解释规则 | 有同一观测多份来源修订时必须有依据；缺规则不能任取最新成功 |
| 被替代证据 ID | `previous_evidence_id` | varchar(128) | 条件必须 | 原输入清单及修正请求 | 源修正替换原观测时必填；普通首次/复用时 NULL |
| 被替代原始快照 ID | `previous_raw_snapshot_id` | varchar(128) | 条件必须 | 原输入清单 | 源修正时保存旧响应引用 |
| 被替代内容哈希 | `previous_payload_hash` | varchar(64) | 条件必须 | 原输入清单 | 源修正时保存旧响应哈希 |
| 被替代证据哈希 | `previous_evidence_hash` | varchar(64) | 条件必须 | 原输入清单 | 源修正时保留旧标准证据完整内容哈希 |
| 重跑原因 | `rerun_reason` | string | 条件必须 | 调度运行审计 | REPLAY/SOURCE_CORRECTION 必填；源修正说明来源修正依据、观测对应关系及超 cutoff 使用新快照的原因 |
| 锁定时间 | `locked_at` | datetime | 必须 | 输入锁定任务 | UTC；本次清单完成校验并锁定的时间 |

## 3. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `execution_mode` | 执行方式 | `INITIAL` | 首次锁定 | 新完整月批次第一次生成输入及规则快照 |
| `execution_mode` | 执行方式 | `REPLAY` | 原清单重跑 | 复用本批次已锁定的观测、规则、区域和 cutoff |
| `execution_mode` | 执行方式 | `SOURCE_CORRECTION` | 源数据修正 | 原数据更正，按可追溯依据替换对应观测，不改原批次规则/区域 |
| `selection_status` | 选择状态 | `SELECTED` | 本次选中 | 唯一观测且用途/选择规则允许，进入本次读取集合 |
| `selection_status` | 选择状态 | `SUPERSEDED` | 被修订替代 | 同一已确定观测有按已锁定修订规则选择的新证据 |
| `selection_status` | 选择状态 | `EXCLUDED` | 排除本次业务输入 | 花卉、未知身份、无允许用途、INFO、血缘失败或选择冲突等；保留审计 |
| `evidence_time_type` | 证据时间类型 | `STATISTICAL_PERIOD` | 统计数据期 | 交易、供应或带明确统计期的数值 |
| `evidence_time_type` | 证据时间类型 | `RETAIL_OBSERVATION` | 零售实测时点 | 在架/报价/榜单快照，observed_at有依据 |
| `evidence_time_type` | 证据时间类型 | `PUBLICATION_EVENT` | 原生发布时间 | 文章或上市事件，无交易期含义 |
| `evidence_time_type` | 证据时间类型 | `STATIC_ATTRIBUTE` | 静态属性 | 无周期的商品事实，不计周趋势 |

## 4. 输入锁定、发布和重跑流程

1. **M1 冻结规则：**批次 `calculation_end_date` 为完整月月末，生成统一 BATCH；读取当批区域快照，并冻结解释规则、原有属性/分类/命名资产的完整内容及生效期。未知规则不按建议启用，不能把现场业务复核设为运行按钮。
2. **M2 选取观测：**限定来源/数据集/市场/指标范围和采集 cutoff。正常业务输入要求 `captured_at <= external_data_cutoff`，来源发布时间有值时也须 `source_published_at <= external_data_cutoff`；按evidence_time_type分流：STATISTICAL_PERIOD要求input_window_start≤data_period_start≤data_period_end≤input_window_end=calculation_end_date；RETAIL_OBSERVATION要求来源时区的observed_at日期位于该窗口；PUBLICATION_EVENT要求有依据的source_published_at日期位于文章窗口；STATIC_ATTRIBUTE不要求交易期，校验cutoff与属性适用期后可选CANDIDATE_ATTRIBUTE，但不进入趋势周观测。超出边界写 EXCLUDED/OUTSIDE_BATCH_WINDOW，不把下一月份数据混入本批。日期未知的统计期未知的数值及发布时间未知的文章仍按隔离用途保存，不能当窗口内观测。根据唯一观测键、来源真实修订标识和已登记修订规则选择。日增量数据按不同观测期组成集合，不是每来源永远只保留一个采集批次；同观测不能同时选择多份修订。
3. **M3 固化内容：**逐证据复制业务字段、质量问题快照和原始/标准/问题哈希，写选择状态及依据。重复采集完全相同内容按确定性快照 ID 排序选择一份并记录去重；内容不同而没有有依据的修订规则时相关观测 EXCLUDED，不用采集时间冒充来源修订顺序。
4. **M4 原子发布：**校验 BATCH、清单唯一性、SELECTED 唯一性、规则哈希、原始及标准哈希、证据/问题统计。标准证据、质量明细、输入清单和算法 07 输出按同次运行整体发布；失败继续读取此前完整成功结果，不能发布半套表。发布由已登记规则自动执行，不要求每次人工点选。
5. **同批 REPLAY：**重用 `input_baseline_run_id` 指向的父清单及其完整证据/问题快照，不扫描新 SUCCESS 批次。默认父清单为当前完整已发布运行；已有源修正成功发布后再次重跑，应保留修正后的集合，不能无声退回首次运行。明确指定历史输入复现时在调度和 rerun_reason 登记父清单，不自动切换当前业务结果。输入业务内容及问题哈希与父清单一致；解释/原有规则哈希、区域哈希和 cutoff 与首次锁定锚点一致，仅 run_id、运行时间和重跑原因可不同。
6. **同批 SOURCE_CORRECTION：**以 `input_baseline_run_id` 指向的当前完整已发布父清单为基础，仍用原 BATCH、首次锚点的规则/原有资产/区域和 cutoff。新原始快照仅能更正已明确对应的 `observation_key`；记录前后 ID、哈希、原文依据和 `rerun_reason`。修正响应的 captured_at/source_published_at 可以晚于原 cutoff，但必须证明更正原锁定观测期的数据，该时间类型对应的真实统计期/观测日/发布时间仍在原窗口内，静态属性只允许纠正原已对应事实，不得引入下一月份观测。若数据日期原来未知，不能仅按行号推定新旧同观测；无权威对应依据时不自动替换。父清单已选集合中受影响观测整条替换，其他观测保持父清单集合；后续 REPLAY 默认复用这一修正后完整结果。
7. 新规则、新参数、新区域映射以及新月份正常数据默认下一完整月批次生效；不能把它们塞入 SOURCE_CORRECTION。历史运行清单不得删除或改写，当前业务结果按同 BATCH 原子替换，不叠加旧结果。

## 5. 关联和聚合安全

正式业务计算先确定单个 BATCH 的当前已发布 `run_id`，再过滤 `selection_status = SELECTED`。以 BATCH＋证据 ID 一对一读取标准证据；历史复现使用本清单 `evidence_snapshot_json` 和 `quality_issues_snapshot_json`，避免当前标准层或问题状态修正后历史内容漂移。规则快照数组只用于追溯或先拆解后独立验收，不展开后与数值事实直接关联聚合。

算法 07 的停止/隔离解释表可读取该次运行 EXCLUDED/SUPERSEDED 记录，保留花卉、未知身份和修订排除审计；这些审计行不参与价量、趋势、覆盖或候选计算。读取时必须显式区分业务 SELECTED 集合与排除审计，不将排除记录重新引入业务分母。

清单行数是证据选择记录数，不能当商品数。价量和问题表遵守标准证据合同的聚合口径。跨运行计数必须按 BATCH＋观测业务键明确去重，不 SUM 所有运行的 SELECTED。

## 6. 缺失、降级和验收

| 场景 | 处理 |
|---|---|
| 整个来源无证据 | 来源摘要写缺失及预期范围，不造空证据；其余有效来源可继续，结果明确部分来源降级 |
| 同观测多条 SELECTED | 阻断本次发布，不任意选一条 |
| 解释规则/原有资产冲突或未知 | 对应用途隔离，未受影响来源继续；不得自动升为正式趋势 |
| 规则或区域哈希与原批次不一致 | 拒绝当作同批重跑/源修正，保留失败审计 |
| 原始/标准哈希无法校验 | 相关证据不允许进入正式选择；整批关联不完整时不发布半套结果 |
| source cutoff 之后新采集 | 正常重跑不读取；只有有依据的源修正例外留痕后替换对应原观测 |
| 统计时间未知或修订无依据 | 有时间含义的历史资料按标准证据用途保存，不参与同期选择比较；冲突观测不自动替换 |

验收至少提交：首次清单、完全同输入 REPLAY、一个带新旧 ID/hash 的 SOURCE_CORRECTION、修正成功后 REPLAY 不退回首次集合、同观测多修订、日增量多期不丢失、所有 SUCCESS 批次不累计、规则/区域变更被拒绝、单表失败不切换发布、无来源仍有摘要、以及历史快照复现证明。生产未提交这些证据前，本合同不能当作真实发布机制已经验收。

来源覆盖审计必须读取去重后的应报集合与收到记录（包括SELECTED、隔离、缺报），不能只数SELECTED，否则会把被隔离记录从分母删除并虚增覆盖。食品范围确证不在目标应报集的对象及INFO不进入业务分母；候选计算仍仅读SELECTED。静态属性、零售实测、文章发布时间、统计交易期四种时间分支均须有复算样例。

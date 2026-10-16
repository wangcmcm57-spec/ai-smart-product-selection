# 公开外部源原始快照表

## 1. 表定位、粒度和主键

正式表名：`ods_external_source_raw_snapshot`。

用途：保存公开 API、下载文件、页面、文章和来源说明的原始响应，供外部证据标准化、权威字典及单位/日期依据追溯。原始响应是来源事实，不因清洗、食品范围排除或算法重跑而改写。

一行代表：一个采集批次中，一次请求的一份完整原始响应。分页、文件分片及重试响应分别保留。

主键：`raw_snapshot_id`。唯一键：`collection_batch_id + request_id`。`request_id` 是采集任务分配的请求实例标识，不能只用 URL 代替；同 URL 的不同参数、分页和重试不能互相覆盖。

本表是可被多个算法月份复用的原始采集事实，不维护算法结果业务版本。进入某个正式批次的原始快照由 `mart_external_batch_input_manifest` 按 `algorithm_batch_version = BATCH_YYYYMM` 锁定；不能用采集批次号替代统一算法批次。

交付状态：字段合同已定义，实际生产建表、采集稳定性和字段级真实数据验收尚需数据开发提交证据；本合同不证明当前服务器已经按此结构落库。

## 2. 完整字段合同

| 中文字段名 | 英文字段名 | 类型建议 | 是否必须 | 字段来源 | 中文注释 |
|---|---|---|---|---|---|
| 原始快照 ID | `raw_snapshot_id` | varchar(128) | 必须 | 采集任务生成 | 请求实例的稳定唯一 ID，重试写新请求实例，不改旧响应 |
| 采集批次号 | `collection_batch_id` | varchar(128) | 必须 | 采集调度 | 一次采集任务的技术标识，不是算法业务版本 |
| 请求实例 ID | `request_id` | varchar(128) | 必须 | 采集任务生成 | 包含分页、分片和重试区别的请求实例标识 |
| 来源 ID | `source_id` | varchar(128) | 必须 | 采集任务来源配置 | 稳定识别发布来源，不以显示名称作为唯一标识 |
| 来源名称 | `source_name` | varchar(256) | 必须 | 采集任务来源配置 | 来源中文或原始名称 |
| 数据集 ID | `dataset_id` | varchar(128) | 必须 | 采集任务来源配置 | 同一来源下的接口、报表或数据集标识 |
| 来源类型 | `source_type` | varchar(64) | 必须 | 采集任务来源配置 | 取值按本合同状态约束；官方价量与零售 SKU 分开 |
| 来源市场 | `source_market` | varchar(64) | 必须 | 采集任务来源配置 | 原数据所属国家或地区，不等于国内目标算法区域 |
| 来源链接 | `source_url` | string | 必须 | 本次请求 | 实际接口、下载文件或原始文章地址 |
| 请求方法 | `request_method` | varchar(8) | 必须 | 本次请求 | `GET` 或 `POST` |
| 请求参数 | `request_params_json` | json | 必须 | 本次请求 | 对象，保存城市、市场、商品、起止日期、分页等实际条件；无参数写 `{}`；不得落凭据 |
| 采集开始时间 | `collection_started_at` | datetime | 必须 | 采集任务时钟 | UTC 时间 |
| 采集结束时间 | `captured_at` | datetime | 必须 | 采集任务时钟 | UTC 时间；只能说明取得响应的时点，不能当交易日 |
| HTTP 状态码 | `http_status_code` | int | 条件必须 | HTTP 响应 | 收到 HTTP 响应时必填，连接失败时 NULL |
| 采集状态 | `collection_status` | varchar(32) | 必须 | 采集任务响应校验 | 只表示请求和响应完整性，不表示商品已匹配或业务已准入 |
| 原始响应 | `raw_payload` | string | 条件必须 | 原始 HTTP 响应或下载文件内容 | 成功响应完整保留，不做业务字段裁剪；大文件可存可稳定读取的受控对象并在本字段保存对象引用 |
| 响应内容哈希 | `payload_hash` | varchar(64) | 条件必须 | 原始响应字节 SHA-256 | 有原始响应时必填；对象引用场景计算对象内容哈希，不计算引用文本哈希 |
| 响应内容类型 | `content_type` | varchar(128) | 条件必须 | HTTP 响应头或文件识别 | 例如 JSON、XML、CSV、HTML；用于选择解析器 |
| 响应字节数 | `payload_bytes` | bigint | 条件必须 | 原始响应字节统计 | 真实响应大小，失败无响应时 NULL |
| 来源原始发布时间文本 | `source_published_at_text` | varchar(256) | 可选 | 响应正文或响应元数据 | 原样保存，不在原始层推断日期 |
| 来源原始修订时间文本 | `source_revised_at_text` | varchar(256) | 可选 | 响应正文或响应元数据 | 修订日与数据交易日分别保留，不互相代替 |
| 原始图片链接列表 | `raw_image_urls_json` | json | 必须 | 原始响应解析定位 | 字符串URL数组；只保留原响应已有且归属明确的链接，无图片[]；V1不为其他外部源单独抓图，不据此认定允许展示 |
| 来源授权状态 | `authorization_status` | varchar(32) | 必须 | 来源授权或公开使用依据 | 公开可追溯不自动证明图片授权；使用约束另行校验 |
| 授权依据链接 | `authorization_basis_url` | string | 条件必须 | 来源许可页面或授权记录 | 授权或公开可追溯状态有依据时填写；未知时 NULL |
| 错误代码 | `error_code` | varchar(64) | 条件必须 | 采集异常处理 | 失败或部分成功时记录技术错误分类 |
| 错误说明 | `error_message` | string | 条件必须 | 采集异常处理 | 失败或部分成功时说明缺页、结构变化、超时等原因，不写入凭据 |
| 入库时间 | `created_at` | datetime | 必须 | 入库任务 | UTC 时间，不替代来源数据时间 |

## 3. 状态字段取值约束

| 状态字段 | 中文字段名 | 允许取值 | 中文含义 | 触发条件 |
|---|---|---|---|---|
| `source_type` | 来源类型 | `COMPETITOR_SKU` | 竞品 SKU | 外部竞品商品接口 |
| `source_type` | 来源类型 | `RETAIL_SKU` | 零售 SKU | 零售商品页面或结构化商品源 |
| `source_type` | 来源类型 | `POS_RANKING` | POS 新品榜 | 真实零售 POS 榜单 |
| `source_type` | 来源类型 | `OFFICIAL_PRICE_VOLUME` | 官方价量 | 官方价格或交易量数据 |
| `source_type` | 来源类型 | `OFFICIAL_SUPPLY` | 官方供需 | 官方供应量或来货数据 |
| `source_type` | 来源类型 | `INDUSTRY_ARTICLE` | 行业文章 | 行业机构或行业媒体文章 |
| `source_type` | 来源类型 | `PUBLIC_NEWS` | 公开新闻 | 可追溯公开新闻 |
| `request_method` | 请求方法 | `GET` | 查询请求 | 请求使用 GET |
| `request_method` | 请求方法 | `POST` | 提交查询请求 | 请求使用 POST |
| `collection_status` | 采集状态 | `SUCCESS` | 请求成功且响应完整 | 响应、分页和基本结构校验通过 |
| `collection_status` | 采集状态 | `PARTIAL_SUCCESS` | 取得部分响应 | 部分分页或预期内容缺失，不自动作为完整正式输入 |
| `collection_status` | 采集状态 | `FAILED` | 采集失败 | 超时、拒绝、结构变化或无有效响应 |
| `authorization_status` | 来源授权状态 | `AUTHORIZED` | 已授权 | 有明确授权依据 |
| `authorization_status` | 来源授权状态 | `PUBLIC_TRACEABLE` | 公开可追溯 | 有公开来源及使用依据，只按适用约束使用 |
| `authorization_status` | 来源授权状态 | `UNKNOWN` | 授权未知 | 未取得可验证依据，图片与引用默认不展示 |
| `authorization_status` | 来源授权状态 | `REVOKED` | 已撤回 | 授权撤回或明确禁止继续使用 |

## 4. ETL、关联和聚合安全

1. 先保存完整响应和哈希，再抽取标准证据。原始响应内的记录数不等于标准证据数，一条原始商品行可派生价格、数量等多种证据。
2. `dwd_external_evidence_normalized.raw_snapshot_id` 多对一关联本表；原始行定位由标准证据的 `raw_record_locator` 指向 JSON 路径、文件行号或表格行列。
3. 快照数用 `COUNT(DISTINCT raw_snapshot_id)`，请求数用请求实例键统计。不能将本表与证据、问题明细直接多对多关联后计数。
4. 相同响应哈希是去重线索；不同请求参数、市场或数据时期不能仅凭哈希相同合并。无修订日期的来源也不能按最后采集时间认定最新交易期。
5. 采集成功不等于数据新鲜。来源时间、数据期和商品/单位解释在标准证据层分别校验。

## 5. 缺失、异常和验收

| 场景 | 写法和处理 |
|---|---|
| 请求失败 | 仍保留快照元数据，失败状态及错误必填；无响应的原文、哈希、字节数写 NULL |
| 返回 `-`、表头或休市文字 | 原样保留；在标准证据层分别标识缺报或 INFO，不能在采集层补 0 或删除 |
| 花卉或未知类别 | 原始快照完整保留；标准层对已确证花卉排除食品业务，对未知类别独立隔离 |
| 来源修订 | 新增快照和哈希，不改旧快照；是否替换已选观测由锁定清单的修正流程记录 |
| 时间或单位无法解释 | 不在原始层填充推测值，交标准层写未解析状态 |

验收至少提交：请求/响应样例与字节哈希复算、主键重复数、分页完整性、失败请求留痕、原始行定位到标准证据的样例、同一来源重复采集不重复累计的对账。真实响应和业务明细留在受控环境，不放入 Git。

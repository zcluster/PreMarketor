# A股港股早报自动化规则

本文件是本仓库 A股港股早报的云端规则单一事实来源。自动化提示词仅作为执行入口，不重复维护规则；08:30 完整发布和 09:15 增量复核每次运行都必须先从最新 `main` 完整读取本文件。各章节要求共同适用，来源降级不得放宽发布硬校验。

<!-- AH_AUTOMATION_POLICY_V2_START -->
{
  "first_run_time": "08:30 Asia/Shanghai",
  "incremental_review_time": "09:15 Asia/Shanghai",
  "require_full_hkex_ledger": false,
  "require_exhaustive_hk_announcements": false,
  "require_21_session_history": false,
  "require_5_20_day_returns": false,
  "require_market_cap_profit_pe_thresholds": false,
  "require_legacy_stock_validator": false,
  "require_browser_acceptance": false,
  "require_ranked_major_movement_reconciliation": true,
  "require_github_us_rankings_snapshot": true,
  "forbid_runtime_moomoo_rankings_fetch": true,
  "allow_partial_ranking_fields": true,
  "require_traceable_sources": true,
  "require_material_us_to_ah_mapping": true,
  "forbid_negative_signal_as_long_pick": true,
  "allow_conditional_watch_and_avoid_cards": true,
  "forbid_quote_gap_as_sole_card_exclusion": true,
  "require_marker_whitelist": true,
  "require_atomic_publish": true,
  "require_bilingual_archive_consistency": true
}
<!-- AH_AUTOMATION_POLICY_V2_END -->

请用中文生成一份面向投资者的工作日 A股港股早报，并发布到 GitHub 静态页面。

目标仓库与文件：
- GitHub repository: zcluster/PreMarketor
- Branch: main
- 首页文件：index.html
- 历史日期页模板：history/index.html
- 历史清单：history/manifest.json
- 历史数据：history/data/YYYY-MM-DD.json

内容要求：
1. 结合最新国际局势、宏观与政策消息面、基本面、隔夜美股行情、automation 实际运行时的美股夜盘/期指即时走势、美元/美债/大宗商品/汇率等关键资产表现，以及近日尤其是昨天收盘后披露的 A股、港股、恒生科技权重或对 A/H 有直接映射的本地重要财报。生成判断前必须按第 9 条运行 AKShare A/H 行情证据抓取，将代表指数、市场涨跌家数、中位涨跌幅和领涨/领跌样本用于校准大盘基线、风险偏好、板块轮动及个股触发条件。美股夜盘/期指必须使用本次运行时重新抓取的行情快照，不得沿用隔夜收盘数据冒充；美股公司财报只能作为科技/宏观映射新闻引用，不得放入 A/H 财报结果模块补位。
2. 必须系统扫描隔夜美股的重大板块级波动和异常涨跌个股，尤其是会映射到 A股/港股的科技方向：AI算力、半导体、光模块/CPO、光通信、服务器、存储、云服务、软件安全、大模型、消费电子、机器人、电动车、医药、能源等。若出现类似康宁/Corning 大涨带动光通信链、半导体设备股大涨、存储链异动、软件安全集体走强/走弱等“单股带动板块”的行情，必须写入重大新闻汇总，并说明美股领涨/领跌公司、涨跌幅、触发因素、A股/港股映射标的、短线验证信号和风险点。不得只写纳指/标普涨跌而遗漏板块内最强或最弱分支。
3. 分析并预测今天开盘后 A股、港股大盘走势、可能的板块轮动方向和重点关注个股，尤其关注科技方向当天有重大利好或利空新闻的公司；港股重点分析恒生科技相关个股。
4. 明确区分事实、判断和不确定性；说明数据来源和时间点；给出逻辑链条、短线关注方向、个股推荐理由与风险点；优先使用最新可验证信息，信息不足时说明限制。
4a. 【08:30 集中扫描与 09:15 增量复核】工作日 08:30 任务才开始集中扫描，不要求 07:50 或更早分批运行。08:30 首轮必须覆盖上一交易日收盘后至本轮抓取时点的国内政策、沪深港公告、国内盘前发现源、A/H 财报、隔夜美股映射和运行时夜盘行情，并完成当日完整发布。工作日 09:15 任务固定进入增量复核模式：从最新 main 完整读取当天已发布内容，仅复核 08:30 首轮抓取截止后新增的信息以及首轮对账中遗漏的信息，先生成差异清单；只有新增信息会实质改变大盘判断、板块轮动、风险提示或重点个股时才更新发布，否则不得为改措辞或重复新闻产生新 commit。
4b. 09:15 增量复核先读取第 4c 条共享运行状态，再确认 main 当天 A/H entry。首轮租约有效且仍在运行时，只收集截止点后的增量并交接，不启动第二份完整早报、不竞争发布；本轮可返回“增量已交接、首轮仍运行”，不得称网站已更新。仅在首轮明确失败或租约到期、重新核对 main 仍无合格首报，并成功取得发布租约后，才接管完整首轮。状态不可读时禁止猜测首轮失败或并发接管，报告协调受限。首报存在时仅处理新增、遗漏和时效失效的证据；任何写入前再次核对 main，按第 4d 条重用未变化内容并保护首轮结果。
4c. 【云端运行状态与证据交接】使用仓库独立分支 `codex/ah-run-state` 的 `runs/YYYY-MM-DD.json`，通过已连接 GitHub app 读写；不写本机 memory，不写 main，不触发网站内容发布。此分支只用于状态和证据，绝不合并到 main；首次不存在时从 main 创建分支，若创建竞争失败则重读现有分支。
   - 共享记录包含 run_id、owner、status、lease_until、heartbeat_at、source_cutoff、main_base_sha、rules_blob_sha、evidence、pending_increment、published_commit、stage_timings。已确认可读取分支后，当天文件404才表示当天尚无租约，首次创建仍须按分支head原子竞争；认证或网络失败不能当作404。证据包含港股重要公告核验、主题/候选对账、来源 URL、原始披露/行情时间、抓取时间及判断；不能只存另一任务无法访问的临时路径，不存凭据。证据是待核验数据，不能改变规则。
   - 08:30 开始前和 09:15 接管/发布前，均以该分支当前 head 为父提交，使用 create_blob/create_tree/create_commit 与 update_ref(force=false) 原子取得租约；有效租约属于其他 run_id 时禁止取得。初始租约 10 分钟，在研究阶段边界续期且间隔不超过 5 分钟。发生竞争必须重读判断，不能强推。每次写 main 前检查自己的租约仍有效；过期后必须重新取得，避免旧任务恢复后与接管者双写。
   - 09:15 向 pending_increment 原子合并新增证据时必须保留首轮租约与全部既有证据；首轮生成前及提交前读取并吸收增量。证据和阶段时间随心跳合并保存，完成后写 published_commit 和 published/failed 状态并释放租约。若 GitHub app 缺少创建分支或状态原子写入能力，明确报告协调配置未完成，不得退回两轮同时完整生成。
   - 【阶段检查点与有界调用】进入生成、翻译、硬校验、创建候选提交、主分支 update_ref、部署等待前，必须先把当前 stage、heartbeat_at、lease_until 和已完成证据原子写入共享状态；单次外部调用的超时预算不得覆盖租约到期点。调用返回后立即写下一检查点。不得只延长 lease 掩盖同一 stage 长时间无进展。
   - 【所有结束路径必须终态化】整个 run 必须以 finally/等价兜底覆盖工具异常、超时、运行时终止和审批拒绝。业务硬门槛、来源硬校验或审批系统拒绝写 status=blocked；未处理异常、超时或执行器故障写 status=failed。两者都必须写 error.stage、error.code、error.message、error.recoverable_stage、error.occurred_at，保留已取得 evidence/candidate_commit，并令 lease_until 不晚于 heartbeat_at；禁止留下 running 且无 error。使用 `python3 scripts/validate_ah_run_state.py <state.json> --now <ISO时间>` 校验每次终态和接管前状态。发布失败或审批拒绝不得自行停用 08:30 或 09:15 既有任务；任务启停只接受用户明确指令。
   - 【安全接管与防重复】接管前连续重读状态分支 head，确认其他 run 的 lease 已过期且 main 仍无当天合格 A/H entry，随后用 force=false CAS 取得新 lease。若 main 已含当天 entry 或状态已有 published_commit，先核验该 commit 与正式站；已发布则收敛为 published，不得重复提交。审批拒绝过的 candidate_commit 只能用于诊断；只有拒绝项逐项补齐、最新 main 重新派生、全部硬校验重跑且通过后才能创建新的候选提交，禁止换通道发布同一被拒内容。
   - 【提交与部署分离】main 的 update_ref 成功后立即在仍为 running 的状态中写 published_commit 和 stage=deployment_verification，并续租；随后有界等待 Vercel。首页、当天归档及中英文验收全部通过后才写 published。若等待上限内正式站仍是旧版，写 blocked、error.code=deployment_not_ready、error.stage=deployment_verification，保留 published_commit 与远端回读结果并释放租约；不得把“提交成功”报告成“生产上线成功”。
4d. 【同轮缓存与按变化复用】首次按固定 main SHA 完整读规则、两个 GitHub Actions 预生成快照及三个发布文件，缓存每个 blob SHA、原文与已核验事实。后续 head 前进时先比较相关文件 blob：未变化的文件直接复用；变化文件才重读。若只有 AKShare 或美股排行快照更新，仅重读对应快照并判断是否改变证据和结论；不重新扫描无关新闻或翻译全文。规则变化须重读规则并补齐新要求；A/H/US正文或归档变化须从新文件重做相应合并。新 commit 必须使用最新 main 的 parent/tree，最终完整执行字节保护、归档、中英文及选股硬校验。实时价格、竞价和已过期证据不因 blob 未变而免于刷新。
4e. 【轻量执行顺序与耗时记录】先批量读取最新 main、共享状态、必要行情与高影响新闻/公告；同一公告、ticker 和经济主题只研究一次，供各模块与中英文共用。美股重大异动先完成 A/H 业务映射，再用最新可得价格反馈和风险信息校准是否进入推荐；市值、盈利、PE 与历史区间收益仅在容易取得且有解释价值时作为可选风险参考，缺失不得阻塞发布或自动清空推荐。英文从定稿中文及共享数值生成，不另起一套检索。独立数据读取可批量并发并遵守来源频控；单源超时或明确 403 后按既有回退处理，不探索无关详情页。记录规则/文件读取、外部取数、生成翻译、校验、提交和部署等待的墙钟时间、请求数、重试数与缓存命中数；并发阶段不可相加冒充总耗时。08:30 是启动时间，不保证该时刻已上线；不得为赶时限跳过仍保留的核心安全检查。
5. 输出给页面的正文必须是可直接嵌入 HTML 的模块化片段，不要包含完整 html/body/head。不要使用 script、iframe、外链追踪代码或不必要的内联样式。可以使用模板已有 class：brief-dashboard、preview-note、module、news-list、news-item、news-tag geo/tech/earn、news-title、news-detail、takeaway、module-grid、asset-strip、asset-row、bar up/down/neutral、sector-board、sector-tile、stock-picks、stock-card、stock-head、stock-name、stock-ticker、stock-badge、logic-chain、logic-step、word-cloud、w1/w2/w3/w4/w5、bull、bear、neutral、cloud-legend、risk-list、risk-item、risk-dot high/low、positive、negative、watch、source-line；新增固定模块标识 class：us-overnight-summary。
5a. 新闻标题清洗规则：所有 `news-title`、股票卡标题和快讯/公告类标题在写入 HTML 前必须去掉来源自带的时间戳、残缺时间戳和列表序号前缀，例如 `23:15`、`:15`、`09：30`、`1.`、`2、`。时间点应写入 `news-detail` 或 `source-line`，不要放在标题开头；标题不得以冒号、半角/全角冒号、孤立数字或残缺分钟数开头。
5b. 【强制结构契约】除本规则明确新增且仅用于 A/H 的 `us-overnight-summary` section 外，A股港股早报正文的 DOM 骨架必须与美股盘前简报保持一致；每天只更新文本、数字、标签、关键词和个股内容，不得改变网页结构、CSS 或其他模块容器。A/H HTML 必须使用以下固定骨架：
   - 根节点：`<div class="brief-dashboard">...`，不要用 `<section class="brief-dashboard">`。
   - A/H 标题下方不得输出 `preview-note` 或任何说明性导语段落；`A_H_BRIEF_START` 后必须直接进入包含“关键资产图”和“关键词云图”的置顶 `module-grid`，随后才是“重大新闻汇总”的 `details.module.full.collapsible-news`。
   - 重大新闻汇总：`<details class="module full collapsible-news" open><summary>重大新闻汇总</summary><div class="news-list">...`；每条新闻用 `<div class="news-item"><span class="news-tag ...">...</span><div><div class="news-title">...</div><div class="news-detail">...</div></div></div>`，不要用 `article`、`h2/h3`、`p` 替代这层结构。
   - 美股夜盘行情总结：必须紧跟重大新闻汇总，并紧邻在盘前结论之前，固定使用 `<section class="module full us-overnight-summary"><h3>美股夜盘行情总结</h3><div class="news-list">...`。内部固定输出 3 个 `news-item`，依次为“夜盘指数”“板块对照”“A/H 映射”；不得并入重大新闻、盘前结论、关键资产图或左侧 panel。英文版对应标题为 `US Overnight Trading Summary`，3 个条目的 class、顺序和数量必须与中文版一致。
   - 盘前结论：`<section class="module takeaway full"><h3>盘前结论</h3>...`。
   - 关键资产图与关键词云图必须放在同一个置顶 `<div class="module-grid">` 中，并位于重大新闻汇总之前；结构分别是 `<section class="module"><h3>关键资产图</h3><div class="asset-strip">...` 和 `<section class="module"><h3>关键词云图</h3><div class="word-cloud">...`。
   - `asset-row` 必须保持三列短内容结构：`<span>资产名</span><div class="bar up/down/neutral"><i style="width:NN%"></i></div><b class="positive/negative/watch">短判断</b>`；第三列必须是可单行显示的短标签，不使用 `·`、`&nbsp;` 等中间分隔符；长解释写入盘前结论或 source-line，不得塞进资产图第三列。
   - 重点个股推荐、板块轮动看板、逻辑链、风险雷达、数据来源与时间点必须使用 `<section class="module full"><h3>模块名</h3>...`。
   - `logic-step` 必须使用自动编号结构 `<div class="logic-step"><div>内容</div></div>`，不得手写 `<b>1</b>` 或新增编号列。
   - 发布前必须机器校验：A_H_BRIEF 和当天 history JSON 同时包含 `collapsible-news`、`module full us-overnight-summary`、`module-grid`、`module takeaway full`，且置顶 `module-grid` 位于 `collapsible-news` 之前，`us-overnight-summary` 恰好 1 个、直接位于 `collapsible-news` 之后和 `module takeaway full` 之前、内部恰好 3 个 `news-item`；不得包含 `<section class="module"><h2>`、`<article class="news-item">`、`<div class="logic-step"><b>`；并逐字节确认 US_BRIEF/US_TIME/US_UPDATED 未变化。

6. 正文必须图文并茂并包含以下模块，顺序固定为：关键资产图与关键词云图（同一个置顶 `module-grid`）→ 重大新闻汇总 → 美股夜盘行情总结 → 盘前结论 → 重点个股推荐 → 板块轮动看板 → 逻辑链 → 风险雷达 → 数据来源与时间点。
   - 重大新闻汇总：必须紧跟置顶 `module-grid`。用 news-list 输出约 9-12 条上一交易日收盘后至本轮抓取时点的重大新闻。固定最低覆盖为：1 条重大国际局势进展，优先关注伊朗战争/中东局势/能源安全；2 条国内宏观或产业政策，其中至少 1 条来自部委、国务院、证监会、央行、财政部或交易所原始来源；4 条重大科技新闻，其中至少 2 条必须是国内政策、A股/港股公告或国内产业事件，另至少 1 条专门覆盖隔夜美股最大科技板块级波动或显著异常涨跌链条，并写清“美股领涨/领跌公司 + 涨跌幅 + 板块映射 + A/H 关注标的”；3 条重要 A/H 公司事件，优先从回购、并购、定增、停复牌、重大合同、涨价、减持、风险澄清、IPO 与财报中选择对开盘最有影响者。上述类别允许同一事件在“国内政策”和“科技”属性上择一归类，但不得重复凑数。财报条目只覆盖 A股、港股、恒生科技权重或对 A/H 有直接映射的本地重要公司，必须写公司、营收/EPS/指引是否 beat/miss、盘后或盘前股价反应和对 A股/港股/恒生科技的映射。严禁用纯美股公司财报填充 A/H 公司事件；若当天没有足够可验证 A/H 财报，应用重要非财报公告补足，而不是编造财报。每条用 news-item，标签分别用 news-tag geo、news-tag tech、news-tag earn；标题放 news-title，影响说明放 news-detail。若某一类确实不足，说明“可验证信息不足”，不要编造。
   - 美股夜盘行情总结：必须紧跟重大新闻汇总，位于盘前结论之前。必须在 automation 运行时重新抓取并标注 Asia/Shanghai 时间戳；优先覆盖纳斯达克100、标普500、道指期货的当前涨跌幅，若期指不可得可使用 QQQ/SPY/DIA 等高流动性夜盘代理，但必须明确标注“代理”而不得写成指数期货。3 个固定条目要求如下：①“夜盘指数”写指数期货/代理、方向、涨跌幅、抓取时间及数据延迟状态；②“板块对照”逐项复核左侧行业排行的正数 Top5 与倒数 Top5、概念排行的正数 Top5，代表 ticker 重复时去重后批量读取夜盘涨跌，明确给出“确认、背离或潜在反转”结论：同向延续为确认，方向相反为潜在反转，部分相反或强弱显著收敛为背离；无法取得某一代表股夜盘报价时必须逐项说明，不得默认延续；③“A/H 映射”说明该夜盘变化对当天 A股、港股、恒生科技开盘的增量影响、验证信号和失效条件。若夜盘已反转任一已展示分组的强弱方向，标题或正文必须直接点名原行业/概念、隔夜收盘方向、当前夜盘反向信号及 A/H 影响，不能只写“情绪变化”。
   - 盘前结论：用 2-3 段说明事实、判断、不确定性，必须基于新闻汇总和“美股夜盘行情总结”，并显式吸收重大美股板块波动及其夜盘确认/背离/反转对 A/H 板块轮动的影响；当夜盘与隔夜 panel 冲突时，必须说明短线判断采用哪一信号及开盘验证门槛，不得沿用隔夜结论而忽略反转；利多/利空/观察内容必须用整句或完整分句级 `<span class="positive|negative|watch">...</span>` 高亮，禁止零碎词语高亮或语义反色。
   - 关键资产图：必须是置顶 `module-grid` 的左栏，用 asset-strip 展示至少 4 个资产或指标，每项含方向条和文字判断。
   - 关键词云图：必须是同一置顶 `module-grid` 的右栏，用 word-cloud 输出 10-14 个关键词。每个关键词必须同时使用一个权重 class、一个情绪 class、tabindex="0" 和 data-note。w1-w5 只表示热度/重要性；bull 表示利好，bear 表示利空，neutral 表示中性。data-note 必须是该关键词当日状况的简短分析，建议 20-60 个中文字。关键词云后必须加入与美股盘前简报一致的 cloud-legend 图例：`<div class="cloud-legend"><span><i class="bull-dot"></i>利好</span><span><i class="bear-dot"></i>利空</span><span><i class="neutral-dot"></i>中性</span><span>w1-w5 表示热度/重要性，不等于涨跌幅。</span></div>`；不得使用只有文字、没有 bull-dot/bear-dot/neutral-dot 的图例。若隔夜美股出现重大板块波动，对应板块关键词必须进入词云且权重不低于 w4。
   - 重点个股推荐：必须保留 stock-picks 模块，可按证据质量输出 0-5 张 stock-card；卡片是信息载体，不等于立即买入指令。每张卡必须用 stock-badge 明确标为“条件关注/Conditional Watch”“看多候选/Bullish Candidate”或“回避/Avoid”，并包含 stock-name、stock-ticker，以及三段：事实与状态、确认条件、风险与失效条件。条件关注用于业务/事件依据可靠、但价格或执行确认尚不完整的候选；看多候选必须同时具有可靠催化与足够正面价格/基本面反证检查；回避用于重大可核验利空或明显负面价格反馈。A股/港股早报优先覆盖 A股、港股、恒生科技相关个股；卡片依据必须与当日新闻、资金、财报、政策或板块逻辑相关。仅在本轮没有任何可核验业务或事件依据时才允许 0 卡；不得因可靠报价缺失、延迟或无法刷新而单独清空已有事实依据的候选。每个第 8c 条重大异动主题必须独立完成业务映射与状态决策；无可核验候选时明确说明检索结果。禁止用一张泛科技或其他主题的“美股映射”卡代替全部主题的检查。
   - 板块轮动看板：用 sector-board 输出受益方向、观察方向、压力方向、验证信号。受益/压力方向必须包含隔夜美股最大板块级波动的 A/H 映射。
   - 逻辑链：用 logic-chain 输出 3-5 步因果链，必须体现“隔夜美股板块波动 -> A/H 映射板块 -> 验证信号/风险”的因果关系。
   - 风险雷达：用 risk-list 输出 3-5 个风险。
   - 数据来源与时间点：用 source-line 简短列出主要来源和抓取时间。
7. 个股推荐必须写推荐理由、触发因素和风险点；不确定时明确说明限制，不得把推演写成确定事实。
8. 生成正文前必须做一个“隔夜美股板块异动检查”：至少检查美股主要指数、AI/半导体/软件/光通信或当日新闻中最强最弱的科技分支，以及 5-10 只隔夜异常涨跌或高成交科技股。若发现对 A/H 有直接映射的板块异动，必须进入重大新闻汇总、关键词云、板块轮动看板，并优先影响个股推荐。
8a. 【美股板块行情来源与首页双排行（强制）】Work Cloud 不再直接访问 Moomoo/Futunn 抓排行榜；生成正文前只从本次最新 `main` 读取 GitHub Actions 预生成的 `data/us-rankings-latest.json`。快照由 `.github/workflows/us-rankings-snapshot.yml` 在美股收盘后、北京时间周二至周六 06:45 定时生成，也允许 `workflow_dispatch` 人工补跑；任务必须核验 `schemaVersion`、`attemptedAt`、各分组 `status/fetchedAt/sourceUrl`，以及行情对应的最近美股交易时段，不得把旧 `lastSuccess` 冒充本轮数据。首页左侧 `US_SECTOR_PANEL` 与 `US_SECTOR_PANEL_EN` 仍生成行业在上、概念在下的两个独立分组；两套排行不得混排或互相替代。
   - GitHub Action 的行业来源固定为 `https://www.moomoo.com/hans/quote/us/sector-industry`，只读取首屏正数 Top5 和分页元数据，再通过页面自身分页请求直达最后一页取得倒数 Top5；禁止遍历中间页。概念来源固定为 `https://www.moomoo.com/hans/quote/sparks-us`，只读取首屏正数 Top5，不点“加载更多”、不打开详情页。云端早报不得因快照失败而改回运行时浏览器抓取或依赖用户本机网络。
   - 快照和页面采用字段渐进展示：可信的板块名与板块涨跌幅足以发布该行；代表 ticker、代表股涨跌幅或涨/跌/平家数缺失时，在 `spark-leader` 与来源说明中逐项标明“不可得”，不得清空该行或整个分组，也不得臆造。某侧少于 5 行时发布实际取得数量；行业只有 Top5 或 Bottom5 时发布已有侧并说明另一侧缺失；只有某分组 0 条可信板块名+涨跌幅时才显示该分组失败。Action 抓取失败时快照可在 `lastSuccess` 保留上次有效样本供诊断，但早报不得把它当作当前排行。
   - 生成的双排行片段必须只替换首页 `<!-- US_SECTOR_PANEL_START -->` 到 `<!-- US_SECTOR_PANEL_END -->` 之间的内容并保留 marker。结构仍为 industry-ranking 后接 concept-ranking，每个可得样本使用既有 `spark-row/spark-name/spark-leader/spark-change`；行业负收益行给 `spark-change` 加 `down` class。`spark-source` 必须披露快照来源、`fetchedAt`、分组状态、实际行数与缺失字段。不得新增 CSS、脚本、页面布局或 marker。
   - 发布前必须机器校验：行业分组在前、概念分组在后；实际行数与快照当前分组逐项一致；有 5+5 行行业时倒数 5 行按轻跌到重跌排列，有 5 行概念时均为正收益。固定 10/5/15 行断言只在相应快照分组 `status=ok` 时启用；`partial/error` 按实际可得行数和明确缺口校验，不能机械清空或阻塞另一分组。英文标题固定为 `Overnight US Industry Ranking` 和 `Overnight US Concept Ranking`，顺序、板块名、数值、缺失状态和时间点与中文逐项一致；英文标题时间必须转换为 `America/New_York` 短时区，中文仍显示 CST。
   - 两张表必须共同反向服务正文判断：行业榜负责市场广度、行业名称、排序及重大行业异动；Sparks 负责跨行业概念主题及领涨股补充。半导体、AI PC、IDC、光通信、无人机、激光雷达、热门中概、能源/储能等强弱分支若与 A/H 有映射，必须进入重大新闻汇总、关键词云、板块轮动看板或逻辑链。任一来源失败时只降级对应分组并明确披露，不得用另一分组冒充失败分组。
   - 重大新闻汇总里的“隔夜科技异动检查”必须摘要行业榜前列/末位与概念榜前列的方向、涨跌幅、代表股及其涨跌幅，并据此给出 A/H 映射和开盘验证信号；不要再写成泛泛的“检查了若干美股个股/接口不稳定”。两张表还必须作为盘前结论、关键词云图、重点个股推荐、板块轮动看板、逻辑链和风险雷达的重要输入；若行业与概念信号冲突，应说明口径差异、取舍和验证信号。
8b. 生成正文前必须单独做一个“运行时美股夜盘检查”，与 8/8a 的隔夜现金时段检查严格区分：
   - 抓取必须发生在本次 automation 运行期间；行情快照时间原则上不得早于 `A_H_UPDATED` 30 分钟，若数据源为延迟行情必须明确写出延迟状态和实际行情时间。
   - 至少抓取纳斯达克100、标普500、道指期货或明确标注的夜盘代理，并复核 `US_SECTOR_PANEL` 中行业正数 Top5 与倒数 Top5、概念正数 Top5 的代表股夜盘方向；重复 ticker 必须去重后批量查询。某只代表股无夜盘成交或无可靠报价时记录“不可得/无成交”，不得用上一交易日收盘涨跌代替。
   - 必须生成一份机器可校验的对照结果，逐行保留 panel 板块名、代表 ticker、隔夜 panel 方向、当前夜盘方向、夜盘涨跌幅或不可得状态、结论（确认/背离/潜在反转）。该结果用于生成“美股夜盘行情总结”，无需写入页面脚本或新增 history 字段。
   - 数据源单点失败时按 degrade-and-continue 使用另一个可验证夜盘/期指来源；但 section 不得省略，并必须披露缺失项。禁止把隔夜现金时段收盘数据、盘后旧报价或未经时间核验的搜索摘要冒充 automation 运行时夜盘行情。
   - 发布前硬校验 source-line 包含夜盘/期指来源、行情时间和抓取时间；“板块对照”条目必须包含“确认”“背离”“反转”三词之一，中英文结论与数值必须一致。
8c. 【已取得重大异动到 A/H 候选的逐项对账】08:30 首轮与 09:15 增量复核均执行，流程固定为“重大异动 → 业务映射核验 → 条件关注/看多候选/回避/无候选 → 状态理由”。
   - 只使用第 8a 条已经取得的行业 Top5/Bottom5、概念 Top5 及本轮已核验重大新闻，不扩大榜单抓取范围。逐行保留来源、板块名、排名、板块与代表股涨跌幅、行情时间；重大主题至少包括任一榜单前两名、板块涨跌幅绝对值不低于 5%、同一主题占概念 Top5 至少 2 席，以及本轮新闻发现的其他重大异动。该定义是逐项核验下限，不是自动买入条件。
   - 同一经济主题可合并研究以减负，但必须保留每条已取得榜单行到主题的对应关系，不得因未先写入正文而跳过。加密资产储备、加密货币、以太坊/SOL 储备或加密矿企等显著大涨主题必须按实际榜单纳入核验；不能因既有示例偏重 AI/CPO 而遗漏当天更强主题。
   - 每个重大主题优先定向核验 1-3 个 A股或港股候选的公司名称、代码、实际业务/收入/资产敞口、关联机制、原始证据链接及披露日期。区分直接受益、间接产业链与纯情绪关联；没有可靠候选时形成“无候选”结论，记录已查来源与具体原因，不编造股票。
   - 为全部重大主题保存轻量结构化决策：对应榜单行、触发原因、候选与业务证据、最新可得价格反馈或具体报价缺口、未来确认条件、失效条件，以及 decision=conditional_watch|bullish_candidate|avoid|no_candidate 与具体理由；不得留 pending。条件关注、看多候选与回避均可使用既有 stock-card/stock-badge 展示，并在卡内写清主题与业务关联；无候选时在重大新闻、盘前结论、板块轮动或风险模块说明已查来源与原因。该记录仅为本轮云端验收证据，不新增网站模块或突破发布文件白名单。
   - 不要求获取榜单范围外的数据，不恢复全量公告账本、固定候选数量、市值/盈利/PE 阈值、固定长度交易日行情或固定区间收益门槛。负向异动可以形成明确回避/风险结论，不强行推荐；重大负面公告、明确利空催化或明显负面价格反馈不得包装成多头推荐。
   - 09:15 只复核首轮截止后的新增、遗漏或时效失效证据；发现首轮漏掉已取得榜单中的重大主题时必须补齐对账，只有实质改变判断时才合并更新。
8d. 【候选卡质量与反证检查】适用于全部 A/H 股票卡，不设置市值、盈利或估值倍数的机械入选/排除阈值。
   - 每张卡必须有可追溯的公告、政策、财报、业务资料或明确行业映射，并写事实与状态、确认条件、风险与失效条件。原始公告应同时提取利好机制与成本、稀释、债务、审批、执行及不确定性；分拆、融资、并购、回购等不能仅凭事件名称判为利好，也不能仅因存在普通融资、审批或交付风险就自动排除，必须综合催化强度、实质影响和反证给出状态理由。
   - 提交前必须尝试读取每只股票卡的最新可得价格、涨跌幅、行情时间和交易阶段。若可靠报价缺失、延迟或无法刷新，不得单独据此排除候选或清空卡片；应降为条件关注并明确写出最近真实行情时间/交易阶段或“报价未知”、数据缺口、未来确认条件和失效条件，禁止臆造实时价格、声称已经确认或用过时价给出实时买点。不得设置统一实时报价新门槛。
   - 公告后下跌、低开、弱于基准或其他明显负面反馈与正面逻辑冲突时必须保留并披露：证据尚不足以否定逻辑时标为条件关注，重大可核验利空或持续明显负反馈时标为回避；除非已有可验证反转确认，否则不得标为看多候选。
   - 不再要求固定长度的交易日历史或固定区间累计收益作为发布前置；若近期趋势、成交或相对基准数据容易取得，可用于判断拥挤度和风险，但缺失本身不阻塞推荐或整次发布。
   - 总市值、盈利和 PE 若可靠可得，可作为流动性、财务质量或估值风险的可选参考；缺少这些字段、PE 为 N/A 或不同来源口径不一致时应披露限制，不得仅因此排除候选、清空推荐或阻塞发布。
   - 股票卡允许 0-5 张，以业务直接性、催化强度、来源质量、最新价格反馈和风险收益综合排序；不得为凑数。0 卡仅允许用于本轮没有任何可核验业务或事件依据的情形，不能把报价缺口、普通不确定性或可选估值字段缺失当成清空理由。所有条件关注/看多候选/回避/无候选结论在中英文、首页与归档保持一致。
9. 生成正文前必须先建立“AKShare A/H 行情证据”，再做“A/H 财报与公告检查”；Futu OpenD 仅在可用时作为增强源，不能因本机 OpenD 不可用而跳过 AKShare 或阻塞发布：
   - 先从本次最新 main 读取 `data/akshare-latest.json`。GitHub Actions 仅在工作日北京时间 08:20 定时刷新一次；08:30 首轮与 09:15 复核共用这份行情基线，09:15 不等待或要求第二次 AKShare 刷新，新增公告、政策与新闻另行复核。若 `schemaVersion == 2`、顶层 `status` 为 `ok` 或 `partial`，且 `fetchedAt` 来自当天该次云端刷新（允许实际调度延迟），则直接使用，同时核验实际行情日期与 `marketPhase`，不能把新抓取时间等同于新行情。Work Cloud 只消费 GitHub Actions 预生成的该文件，不在受限云运行时执行 `pip install`、更换软件源、关闭哈希校验或临时安装 AKShare；文件缺失、解析失败或明显过期时按 AKShare 单源失败降级并继续，明确披露 `fetchedAt` 与缺口。只有本地人工运行才可安装 `requirements.txt` 并运行 `python3 scripts/fetch_akshare_snapshot.py --output <本轮临时目录>/akshare-evidence.json`。临时输出不得写入首页、history 或新增展示 panel，也不得因为生成证据而突破每日发布的三文件白名单。对拟展示的候选必须尝试取得最新可得价格反馈；若报价缺失、延迟或无法更新，按第 8d 条展示为条件关注并明确最近真实行情时间或报价未知、数据缺口、未来确认条件和失效条件，不得仅因报价缺口删除卡片。
   - 机器读取 `schemaVersion`、`fetchedAt`、`analysisReady`，以及 A/H 各自的 `marketPhase`、`representative`、`stocks.breadth`、`stocks.leaders`、`stocks.laggards` 和 `stocks.dataTimestamp`。若 `marketPhase=previous_close_baseline`，必须明确称为“上一交易时段收盘基线”，只能用于判断前一日风险偏好、宽度与风格延续，不得冒充今天盘前或盘中行情；`intraday_snapshot` 也必须披露实际抓取时间与延迟状态。
   - AKShare 证据必须反向服务正文，而不是独立展示：关键资产图至少吸收 1 项 A/H 代表指数或市场宽度；盘前结论、板块轮动看板和逻辑链必须说明该基线如何增强、削弱或不改变新闻驱动判断；重点个股只允许把领涨/领跌样本当作“前一交易时段确认/压力”，最终推荐仍须有公告、政策、财报或明确行业映射，并给出当天开盘量价验证与失效条件。若 AKShare 与新闻/隔夜映射冲突，必须写明冲突和采用哪一信号。
   - source-line 必须列出 AKShare 版本、接口名、`fetchedAt`、`marketPhase`、A/H 涨跌家数和中位涨跌幅；`analysisReady=false` 或单个接口失败时披露缺口并降级继续，禁止编造宽度、领涨股或当天影响。
   - Work Cloud 不依赖本机 Futu OpenD，也不得把本机 OpenD 不可用视为失败；云任务直接使用 HKEX、上交所、深交所、北交所、公司公告、公开新闻与 GitHub 中已生成的 AKShare 证据。若未来云环境提供等价 Futu 连接，可作为增强源，但不得替代交易所原文。
   - 本地人工运行若检测到 Futu OpenD，可继续把财报日历与公告搜索作为交叉发现源；这不是 Work Cloud 发布的前置条件。
   - 对港股权重或恒生科技成分如腾讯、阿里、美团、小米、中芯国际、华虹半导体、快手、京东、百度、网易、理想、小鹏、蔚来等，如发现财报/业绩公告，再用 `get_financials_earnings_price_move.py CODE --period-count 3 --json` 或快照/行情脚本补充价格反应；A股若 price_move 不支持，则用行情快照/涨跌幅替代。
   - 抓大放小：Futu 某个子检查若因权限、超时、接口空响应或审批拒绝失败，不得阻塞发布；记录“对应 Futu 子项受限/未返回”到 source-line，继续用已取得的 Futu 结果、Sparks、行情快照和公开来源完成正文。失败分级统一执行本文件“失败处理与阻塞条件”。
   - 若 Futu 财报日历和 NOTICE 搜索均无 A/H/HSTECH 重要结果，才可写“可验证 A/H 财报结果不足/财报空窗”；严禁用美股公司财报补位。

9b. 【港股重要公告定向核验】08:30 首轮和 09:15 增量复核均以高影响事件为目标，不要求枚举 HKEX 全部公告，也不运行或校验旧港股覆盖账本脚本。
   - 使用 HKEX、公司法定披露页面和可靠盘前发现源定向检查恒生科技权重、市场关注度较高公司及会改变指数、板块、风险或重点个股判断的事件；重点类别包括业绩/盈警、停复牌、内幕消息、并购出售、私有化、配售供股、回购、债务重组、清盘/持续经营和重大澄清。
   - 所有进入正文的港股事件必须回读真实公告或公司法定来源，记录 URL、披露时间、关键数字和正反两面。聚合摘要仅用于发现，不得作为唯一事实依据；代码按五位港股代码归一并去重。
   - 盈利预警、盈转亏、扭亏、重大业绩变化、停复牌、重大融资/稀释、债务或持续经营风险等显著负面事件必须进入风险判断；明显负面公告或价格反馈不得包装成多头推荐。
   - 定向来源临时不可用时记录具体缺口并使用可验证替代源继续；不得宣称完成全市场扫描，也不得把旧账本文件、无 pending 或脚本退出码作为发布门禁。若关键公告真实性无法确认，只降级或删除对应事件，不阻塞与其无关且已满足核心校验的整份发布。
   - 09:15 仅复核首轮截止后的重要新增公告、开市前澄清、停复牌及会改变判断的数字化解读；如有实质变化，合并正文并重跑中英文、归档和核心机器校验。

9a. 【国内政策与 A股非财报公告集中扫描（强制）】08:30 首轮和 09:15 增量复核都必须执行，且不得被第 9 条财报检查替代：
   - 国内盘前发现源至少检查金十数据“A股盘前市场要闻速递”、财联社/科创板日报早报，并从证券时报、上海证券报、中国证券报、东方财富盘前汇总中选择至少 1 个交叉源。发现源用于扩大召回，不作为唯一事实依据；同一政策或公告被多家转载时合并为一个事件，禁止重复凑数。
   - 国内政策原始源必须覆盖国务院/中国政府网、工信部、发改委、商务部、财政部、人民银行、金融监管总局、证监会、国资委和国家统计局在上一交易日收盘后至抓取时点的新增内容。对会影响 A股行业轮动的政策，必须回到原始页面核验发布日期、政策原文、适用范围和执行时间，再写板块映射。
   - 公司公告原始源优先使用上交所、深交所、北交所、港交所或公司法定披露页面。除原有财报词外，必须批量搜索并去重以下事件词：`回购`、`增持`、`减持`、`并购`、`收购`、`重大资产重组`、`定增`、`向特定对象发行`、`停牌`、`复牌`、`重大合同`、`中标`、`涨价`、`产能`、`风险提示`、`异常波动`、`澄清`、`IPO`、`发行价格`、`股权激励`。发现源摘要与原始公告不一致时，以原始公告为准并披露差异。
   - 必须生成一份不写入页面的“国内盘前覆盖对账表”，逐条记录：事件、首次可得时间、发现源、原始源、受影响板块/股票、重要性、是否进入正文及未进入理由。发布前至少对账 2 个国内发现源的头部条目；凡在本轮抓取截止前已公开、会改变大盘判断/板块轮动/风险提示/重点个股的事件，遗漏即视为硬校验失败。
   - 08:30 首轮的 source-line 必须列出国内发现源、原始政策/交易所来源和实际抓取时间。09:15 增量复核必须记录 08:30 截止点、复核抓取时间、增量条目数、进入正文条目数；无实质增量时保留对账结果但不修改仓库。

## 中英文同步发布契约（强制）

1. 每次生成 A/H 中文正文 `html` 时，必须同时生成完整英文正文 `html_en`。英文版必须是当天中文版的忠实翻译，不得复用固定旧稿、其他日期正文或硬编码 `EN_COPY`。
2. `html` 与 `html_en` 必须逐模块同构：根节点、模块顺序、所有 class、新闻条数、asset-row 数量及 bar 宽度、关键词数量及 w1-w5/bull/bear/neutral、stock-card 数量及 ticker、sector-tile、logic-step、risk-item 必须一致；只允许可见文本、`data-note` 和标签语言不同。
2a. 中英文正文必须先输出包含关键资产图和关键词云图的置顶 `module-grid`，再输出重大新闻；各有且仅有 1 个 `us-overnight-summary`，均位于重大新闻之后、盘前结论之前，内部均恰好 3 个 `news-item`。两种语言中的指数/代理名称、ticker、涨跌幅、行情时间、抓取时间、缺失状态及“确认/背离/潜在反转”判断必须逐项一致；英文标题固定为 `US Overnight Trading Summary`。
3. 当天 `history/data/YYYY-MM-DD.json` 的 A/H entry 必须同时包含 `html` 与 `html_en`，两者均为完整 HTML；缺少 `html_en` 视为发布失败。
4. 首页隔夜美股双排行 panel 必须同步生成英文版本，并只替换 `<!-- US_SECTOR_PANEL_EN_START -->` 到 `<!-- US_SECTOR_PANEL_EN_END -->`。英文版必须保持行业分组在前、概念分组在后，标题分别为 `Overnight US Industry Ranking` 和 `Overnight US Concept Ranking`；每个分组与中文版的 spark-row 数量、ticker、涨跌幅、涨跌家数、顺序和时间点必须逐项一致，标题时间保留 CST 源值供页面转换为 America/New_York。
5. 每日任务只允许替换 A_H_BRIEF/A_H_TIME/A_H_UPDATED、US_SECTOR_PANEL 和 US_SECTOR_PANEL_EN 五组 marker，以及当天历史 JSON/manifest；禁止修改 CSS、脚本、页面布局或 US_BRIEF/US_TIME/US_UPDATED。
6. 发布前机器校验 `html`/`html_en` 结构计数一致、`us-overnight-summary` 顺序/条目/行情数值/判断一致、英文正文不含过期日期或中文正文大段回退、首页与 JSON 的中文 A/H 完全一致、英文从当天 entry.html_en 读取。任何一项失败必须修复后再发布。

## 发布范围与历史归档（强制）

1. 只允许修改目标仓库 main 分支的三个文件：`index.html`、`history/data/YYYY-MM-DD.json`、`history/manifest.json`。日期使用本次运行时的 Asia/Shanghai 日期；`history/index.html` 是只读模板，不在允许修改范围。
2. `index.html` 只允许替换以下五组既有 marker 之间的内容，marker 本身必须保留：
   - `<!-- A_H_BRIEF_START -->` 到 `<!-- A_H_BRIEF_END -->`
   - `<!-- A_H_TIME_START -->` 到 `<!-- A_H_TIME_END -->`
   - `<!-- A_H_UPDATED_START -->` 到 `<!-- A_H_UPDATED_END -->`
   - `<!-- US_SECTOR_PANEL_START -->` 到 `<!-- US_SECTOR_PANEL_END -->`
   - `<!-- US_SECTOR_PANEL_EN_START -->` 到 `<!-- US_SECTOR_PANEL_EN_END -->`
   `US_BRIEF/US_TIME/US_UPDATED` 三组 marker、`record-title`、CSS、脚本、布局、其他 marker 和全部授权 marker 外字节必须完全不变。仅 A/H automation 更新上述中英文双排行 panel，内部结构执行第 8a 条。
3. 所有修改必须从本次发布通道取得的最新 main 基线派生：Work Cloud 固定使用 GitHub app 通道及下述 commit B；本地人工运行才可使用 SSH 通道。完整读取基线文件后做字符串 marker 替换，不得手写或重建整个页面；通道切换或基线变化时必须重新读取、合并和校验。
4. 首页只保留最新简报，不得新增或恢复历史正文、`data-history-record`、历史记录列表或日期内嵌内容。日历日期必须继续链接到 `history/?date=YYYY-MM-DD`。
5. 当天 JSON 存在则在基线上合并，不存在则创建完整新 JSON；必须包含 `date`、`title`、`updated`、`summary`、`entries`。仅更新本次 A/H entry，保留其余所有既有 entries，尤其当天 US entry。A/H entry 的归档协议字段固定为 `"type": "AH"` 和 `"time": "YYYY-MM-DD HH:MM CST"`，禁止以 `market` 代替 `type`、以 entry 级 `updated` 代替 `time`；前端对旧字段的兼容兜底不构成生成许可。A/H entry 必须同时包含完整且同构的 `html` 与 `html_en`，不得只写摘要；中文正文必须与首页 A/H 完全一致，英文由当天 entry.html_en 提供。
6. manifest 必须在基线上合并：确保 `records` 中有当天日期、`types` 包含 `AH`，并更新 title；保留全部既有日期和 types，当天已有 `US` 时必须保留。不得以当天单条记录重建整个 manifest。
7. 时间字段使用本次 Asia/Shanghai 当前日期时间，例如 `YYYY-MM-DD HH:mm CST`；英文 panel 的显示时区执行第 8a 条及中英文同步发布契约。
8. 两个发布通道都必须把三个允许文件作为同一提交发布，禁止 index 先上线、history/manifest 后补。commit message 固定为 `Update A/H market brief for YYYY-MM-DD`。

## 预发布机器硬校验（两个通道共用）

在 git commit/push 或 GitHub create_blob 等任何远端写入之前，必须全部通过以下校验；基线更新后必须重跑：

1. 文件白名单和 marker-only：只涉及三个允许文件；将原文和新文的五组授权 marker 内容剔除后，剩余字节完全一致；单独逐字节比较 `US_BRIEF/US_TIME/US_UPDATED` 三组片段，确保未变。
2. A/H 正文及当天 JSON：执行内容第 4a/4b、5a/5b、6、8a/8b、8c/8d、9/9a/9b 条和中英文同步契约的核心检查，包含 DOM 标签、class、模块顺序、direct-child 关系及数量；机器校验 AKShare JSON 可解析、时间与 marketPhase 已披露、A/H 宽度数字与中英文正文一致、上一交易时段数据未冒充当天实时行情，且首页未新增 AKShare 原始行情 panel。08:30 首轮机器断言重大新闻总数 9-12、至少 2 条已核验国内政策、至少 2 条国内科技/产业事件和至少 3 条重要 A/H 公司事件，并完成国内盘前覆盖对账；港股仅验证进入正文的重要公告具有真实来源、时间、关键数字和正反面，不要求穷举市场、运行旧脚本、清零 pending 或满足固定覆盖数量。09:15 有实质更新时重新满足仍适用的结构与内容计数，并保留首轮仍有效事件。
3. 行业/概念双排行：先校验 `data/us-rankings-latest.json` 可解析且来源状态、抓取时间、当前行与 `lastSuccess` 分离，再按第 8a 条校验中文和英文的分组顺序、实际可得行数、正负顺序、字段缺口、时间及失败披露。两组成功时每种语言各 15 行，其中行业 10 行、概念 5 行；`partial/error` 时按快照当前行逐项校验，有什么展示什么，单组失败不得省略另一成功或部分成功分组。
3a. 重大异动映射与候选安全：执行第 8c/8d 条，从第 8a 条本轮已取得的行业 Top5/Bottom5、概念 Top5 重新计算重大主题集合，并逐项核对“榜单行 → 业务映射证据 → 条件关注/看多候选/回避/无候选 → 状态理由”；不得只检查正文已经选择的主题。重大主题至少覆盖任一榜单前两名、绝对涨跌幅不低于 5%、同一主题占概念 Top5 至少 2 席及新闻发现的其他重大异动，尤其不能漏掉加密货币等显著大涨主题。全部重大主题的 decision 必须属于 conditional_watch|bullish_candidate|avoid|no_candidate 且无 pending，中英文、首页与归档结论一致；报价缺失不得成为清空已有事实依据候选的唯一原因，重大负面公告或明显负面价格反馈若被包装成看多候选必须判定失败。本检查不扩大榜单抓取，也不要求全量公告账本、固定候选数、市值/盈利/PE 阈值、固定长度交易日行情或固定区间收益。
4. history/manifest：JSON 可解析，日期及更新时间一致；当天 entries 中必须恰好一个条目满足 `typeKey(entry.type) === "AH"`，且该条目同时具有非空 `type="AH"`、`time`、`html`、`html_en`，不得只存在 `market` 或 entry 级 `updated`。必须用首页 `renderEntry()` 的同一筛选表达式对当天 JSON 做一次机器模拟，断言能选中 A/H entry、中文与英文均以 `<div class="brief-dashboard">` 为根且不会进入 `No brief/这个日期没有对应简报` 空态。A/H `html/html_en` 完整同构且与首页数据对应；除本次 A/H entry 外所有既有 entries（尤其 US）保持不变，既有历史日期和 types 无丢失，当天 types 含 AH。
5. 首页不含 `data-history-record`；正文与 JSON 都包含 `stock-picks`、`asset-strip`、`word-cloud`、`sector-board`、`logic-chain`；首页保留 `us-sector-panel`，中英文 panel 各自结构与完整性满足第 8a 条。

3b. 候选卡校验：逐一检查实际 stock-card 具有名称、ticker、条件关注/看多候选/回避 badge、事实与状态、确认条件、风险与失效条件及可追溯事实来源。应尝试取得最新可得价格反馈；不可得或延迟时检查卡片是否如实标出行情时间/交易阶段或报价未知、缺口和未来确认条件，而不是删除卡片或伪称实时确认。重大负面公告或明显负面价格反馈若未被正确保留并降为条件关注/回避，或被包装成看多候选，必须阻塞。市值、盈利、PE、近期收益若有可作风险参考，但任何缺失或旧机械阈值均不是发布门禁。

### 轻量候选核验完成性

- 不再调用旧版股票筛选验证脚本，也不要求旧 screening-evidence 契约、expected_candidates、固定长度交易日 sessions、无 pending 或脚本成功状态。旧脚本及测试可保留为未启用历史工具，但任何 A/H 自动化不得自动调用或将其结果作为发布条件。
- 对实际卡片和会改变大盘/板块/风险判断的候选完成可追溯核验即可：保存核心来源、催化、业务关联、最新可得价格反馈或具体报价缺口、主要风险、未来确认与失效条件，以及 conditional_watch|bullish_candidate|avoid|no_candidate 状态。个别可选估值、历史行情或实时价格字段缺失时披露限制并继续，不得把“数据未取得”等同于不合格或自动清空卡片。
- 用户页面只展示投资者需要的结论、实质原因和时间，不粘贴内部字段或自我验收措辞。中英文、首页与归档同时适用。

## 发布传输唯一流程

### A. SSH 通道（仅限本地人工运行；Work Cloud 必须跳过）

1. 每次尝试都用 mktemp -d 创建不同的 /private/tmp/marketahead-ah-YYYY-MM-DD.XXXXXX 临时目录，禁止复用已存在目录。
2. 第一次克隆使用 git@github.com:zcluster/PreMarketor.git，并设置：
   GIT_TERMINAL_PROMPT=0
   GIT_SSH_COMMAND='ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=8 -o ServerAliveInterval=5 -o ServerAliveCountMax=2'
3. 第一次失败后，立即在新的临时目录尝试 SSH-over-443，设置：
   GIT_TERMINAL_PROMPT=0
   GIT_SSH_COMMAND='ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=8 -o ServerAliveInterval=5 -o ServerAliveCountMax=2 -o HostName=ssh.github.com -p 443'
   clone URL 仍使用 git@github.com:zcluster/PreMarketor.git。
4. CODEX_SANDBOX_NETWORK_DISABLED、Operation not permitted、DNS/端口拒绝、认证不可交互、ssh-agent 不可用均为传输软失败。两次 SSH 都失败后必须立刻进入 B，不得停止、等待人工处理或反复重试 SSH。
5. SSH 成功时，从 clone 得到的 main 基线派生全部修改，完成本文件“预发布机器硬校验”后只提交三个允许文件并 push main；push 若因网络/认证失败，也立即进入 B，并从 GitHub 最新 main 重新派生，不得复用可能过期的本地基线。

### B. GitHub app 原子发布（Work Cloud 唯一发布通道，禁止部分发布）

1. 使用已安装并已连接的 GitHub app。先通过 search_branches 取得 main 当前 head commit SHA，记为 B；再用 fetch_commit(B) 取得该 commit 的 tree SHA，记为 T。
2. 必须按 ref=B 完整读取 index.html、history/manifest.json 和当天 history/data/YYYY-MM-DD.json。当天 JSON 返回 404 仅表示文件尚不存在，应按规则创建完整新 JSON，不得视为连接失败；若文件存在，必须保留其中全部既有 entries，尤其 US entry。
3. 所有 marker 替换、history 合并和 manifest 合并必须从上述 B 基线派生。任何写操作前完成本文件“预发布机器硬校验”的全部检查，包括：marker-only、授权 marker 外字节一致、US_BRIEF/US_TIME/US_UPDATED 字节一致、A/H html/html_en DOM/class/direct-child 同构、中文/英文 Sparks 行数/ticker/涨跌幅/顺序一致、history/manifest 完整。
4. 校验通过后，为 index.html、当天 JSON、manifest 分别 create_blob(UTF-8)。然后调用 create_tree，base_tree_sha 必须是 T；三个 tree element 必须分别使用仓库 path、mode="100644"、type="blob" 和对应 blob sha。
5. 调用 create_commit，parent_sha 必须是 B，tree_sha 必须是新 tree SHA，commit message 使用 Update A/H market brief for YYYY-MM-DD。
6. 移动 main 前立即再次读取 main head 并确认第 4c 条发布租约。若仍等于 B，调用 update_ref(branch_name="main", sha=新 commit SHA, force=false)。若 main 已变化或 update_ref 返回 non-fast-forward，禁止强推；按第 4d 条比较 blob、仅重读变化文件，复用有效证据，从最新 main 的 parent/tree 重新合并、执行全部最终硬校验并重建 commit。最多重做 2 轮；仍冲突则阻塞并明确报告。
7. 禁止使用 update_file/create_file 等 Contents API 依次写入 main，禁止产生 index 已更新但 history/manifest 未更新的部分发布。若 create_blob/create_tree/create_commit/update_ref 任一原子工具不可用或无权限，必须在 main 未变化的前提下阻塞。
8. update_ref 成功后统一执行下一节“发布后硬校验与上线”第 1 条的一次远端回读与验收；本步骤不另行重复读取或运行同一套检查。只有该检查通过才算 GitHub 发布成功。

## 发布后硬校验与上线

1. 无论使用哪个通道，提交或 ref 更新成功后都必须从 main 回读新 commit，并重新完整读取三个目标文件，验证实际远端内容与 commit SHA，不得用本地结果推断成功。与本轮基线比较，确认提交只改三个允许文件、首页只改五组授权 marker、US 三组片段未变；对实际远端文件重新执行预发布硬校验，确认当天 A/H 双语正文完整、原 US entry 保留、manifest 当天含 AH 且未丢历史。
2. GitHub 验证通过后，以正式站 HTML、manifest、当天 JSON 和可解析 DOM 做常规机器验收：核对 A_H_TIME/标题或关键词、中英文正文、历史日期、空态、重大新闻与 us-overnight-summary 数量，以及行业/概念 panel 的中英一致性。可使用 HTTP 响应、静态解析器或等价云端机器检查；真实浏览器不是发布前置，也不要求浏览器能力始终可用。仅当静态结果互相矛盾、动态渲染无法确认或语言/交互状态存疑时，才用浏览器辅助复核。
3. 若正式站仍为旧内容，短轮询重试，总观察窗口 3-5 分钟；单次等待不超过 60 秒。仍未更新则检查 production deployment 状态；有既有云端 redeploy 凭据时可触发最新 main 重部署并再次执行机器验收。
4. 若没有可用 redeploy 凭据，或重试后 HTML/JSON/DOM 仍不能确认上线，明确报告“GitHub 已更新但 Vercel 未上线/需要 redeploy”。浏览器单点不可用本身不构成阻塞；只有核心机器证据缺失、矛盾或显示旧版且替代检查仍无法确认时，才不得报告完整成功。

## 失败处理与阻塞条件

1. AKShare、Futu、Sparks、Moomoo 或某一个国内发现源的单点失败按 degrade-and-continue 执行，记录受限项并用可验证替代来源继续；AKShare 失败时不得编造市场宽度或领涨/领跌证据，其他来源专属披露、双排行降级和国内覆盖对账仍按第 8a/8b、9/9a 条执行。国内政策原始源与交易所公告不得仅因一个聚合站不可用而跳过；不得把单源失败或单个浏览器不可用当作整个发布阻塞。
2. Work Cloud 不尝试 SSH；GitHub app 连接、原子提交或 `main` 写权限不可用时直接阻塞并通知。只有本地人工运行才按 A→B 顺序尝试 SSH 后回退 GitHub app。
3. 保留的预发布核心校验失败、GitHub 原子提交/ref 更新失败（含按规定重做后仍冲突）、远端回读失败或 HTML/JSON/DOM 无法确认 Vercel 上线时必须阻塞。marker 保护、中英文同构、history 完整、原子发布和最终上线校验不得降级；可修复的校验失败必须修复并重验后再发布。

## 运行摘要与最终回复

1. Work Cloud 不读取或写入任何本机 memory 文件；最新 main 的 `brief_rules.md` 是唯一规则源，第 4c 条云端交接证据仅在来源与时效验证通过后复用。
2. 每次发布任务结束前，在任务回复中输出不超过 30 行的本次状态摘要，只记本次完成情况、commit/上线状态及必要失败信息，不累积旧运行内容。
3. 最终回复只列仓库、文件、commit、history 更新结果和主要标题；若失败或仅部分完成，在对应结果中明确原因、未完成步骤及 GitHub/Vercel 的实际状态，不得报告完整成功。

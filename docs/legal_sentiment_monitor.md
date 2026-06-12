# legal-sentiment-monitor MVP 操作说明

## 启动

在项目根目录运行：

```powershell
.\start_webui.bat
```

管理后台地址：

```text
http://127.0.0.1:8080/monitor
```

第一版调度器运行在 FastAPI 单进程内，部署时不要给 `uvicorn` 开多 worker。检测到多 worker 时，系统会自动停用内置调度器；如需多 worker，请设置 `MONITOR_DISABLE_SCHEDULER=true`，再用服务器 cron / Windows 计划任务定时调用 `monitor_cli.bat run-due`。

## 服务器持久化目录

默认情况下，监控数据写在项目目录：

```text
monitor_data/
browser_data/
```

服务器部署时建议显式指定持久化目录，方便备份、迁移和代码升级：

```powershell
$env:MONITOR_DATA_DIR = "D:\legal-sentiment-monitor\data"
$env:MONITOR_BROWSER_DATA_DIR = "D:\legal-sentiment-monitor\browser_data"
```

- `MONITOR_DATA_DIR`：保存 SQLite、加密密钥 `secret.key`、运行日志、HTML/Excel/Markdown 报告。
- `MONITOR_BROWSER_DATA_DIR`：保存抖音、快手、小红书浏览器 profile；平台状态检查和真实采集启动浏览器都会使用这个目录。

如果不配置这两个环境变量，系统仍使用项目内默认目录。

系统会在保存运行摘要、错误信息、采集日志和后台日志接口返回前，对常见的 `api_key`、`password`、`cookie`、`token`、`Authorization` 等敏感片段做脱敏。实际使用时仍不要把真实密钥、Cookie 或短信验证码写入律所名称、关键词、Prompt 等业务字段。

## 脚本化运行

不想打开 WebUI 时，可以使用根目录的命令行脚本：

```powershell
.\monitor_cli.bat readiness
.\monitor_cli.bat doctor
.\monitor_cli.bat list-jobs
.\monitor_cli.bat selftest-report
.\monitor_cli.bat run-job 1
.\monitor_cli.bat run-due
```

命令说明：

- `readiness`：输出当前上线验收状态。
- `doctor`：检查项目文件、依赖命令、数据目录、SQLite、浏览器 profile、AI/邮件配置、任务和报告链路。
- `list-jobs`：列出后台已配置的监控任务。
- `selftest-report`：生成一份本地自测报告，不调用平台、不发邮件。
- `run-job 1`：立即运行 ID 为 `1` 的监控任务。
- `run-due`：按任务频率检查当前到期任务并执行，适合接服务器 cron、Windows 计划任务或外部调度器。

脚本输出统一是 JSON，方便后续写日志、接告警或被其他系统调用。

同一个监控任务会使用 `MONITOR_DATA_DIR/locks` 下的轻量锁文件做防重复保护。即使 WebUI、内置调度器和 `monitor_cli.bat run-due` 同时触发同一任务，也只会有一个采集进程真正运行；其他入口会返回 `already_running`。如果上一次进程异常退出残留锁文件，系统默认会在 6 小时后自动回收；可通过 `MONITOR_JOB_LOCK_TTL_SECONDS` 调整。

如果部署环境必须使用多个 Web worker，内置调度器不会启动。此时页面仍可手动运行任务，但定时采集需要由外部定时器调用 `monitor_cli.bat run-due`。

## 页面配置

- 账号登录：分平台打开登录窗口，维护抖音、快手、小红书浏览器 Profile 和登录态。
- 任务管理：配置律所名称、别名、关键词、排除词、抖音/快手/小红书、评论、采集范围、频率、收件邮箱。
- 验收状态：查看平台 Profile、AI、邮件、自测报告、真实报告是否具备。
- AI 配置：支持 OpenAI Compatible 和 Anthropic，填写 Base URL、API Key、模型、温度和负面判断 Prompt。
- 邮件配置：填写 SMTP、发件人、账号密码、默认收件人和标题模板。
- 运行记录：查看每次任务状态、耗时、采集量、新增量、排除量、负面数和采集日志。
- 报告中心：预览 HTML，下载 HTML、Excel 和 Markdown，并按律所、平台、风险、日期筛选；风险筛选支持高风险、疑似负面、待人工复核、无风险，其中无风险不包含待人工复核内容。下方会展示线索明细，方便运营逐条查看标题、链接、封面、AI 理由、证据和待人工复核状态；也可以生成本地自测报告，检查报告链路是否正常。

任务列表会显示“上次运行”和“下次运行”。启用任务保存后会立即计算下次运行时间；暂停任务会显示“已暂停”；手动立即运行时，下次运行会先清空，任务结束后重新计算。

点击“立即运行”前，后台会先做运行前检查：同一任务是否正在运行、关键词和平台是否完整、所选平台 Profile 是否存在、AI 和邮件是否测试通过。硬性问题会阻止启动；AI、邮件、登录态等非硬性问题会先提示，由运营确认后仍可继续运行。

HTML 邮件和 Markdown 报告会包含“平台采集状态”表，展示每个平台的成功/失败、采集数、新增数和失败原因。某个平台失败时，其他平台的内容仍会进入报告，失败原因用于后续重新登录或排障。

采集输出默认使用 MediaCrawler JSON 文件；监控层同时兼容 JSONL 输出，避免后续切换保存格式后出现“文件已生成但报告为空”的问题。

邮件正文使用 HTML 日报，附件包含 Excel 明细和 Markdown 报告；附件会使用明确文件类型，方便邮箱客户端识别和下载。

任务保存时会做基础校验：

- 律所名称、关键词、平台必填。
- 收件邮箱如果填写，必须是邮箱格式。
- 自定义日期范围必须同时填写开始日期和结束日期，且开始日期不能晚于结束日期。
- 自定义 cron 必须符合 5 段 crontab 格式，例如 `0 9 * * *`。
- 邮件发送时间必须是 `HH:MM` 格式，例如 `09:00`。

排除词会在采集结果入库前生效：标题、正文、关键词、作者命中任一排除词时，该内容不会进入 AI 评估和报告。AI 判断时必须同时满足“与目标律所相关”和“疑似负面”，才会计入疑似负面线索；无关内容不会因为文本本身负面而进入风险线索。

去重按“任务 + 平台 + 内容 ID”生效：同一个监控任务重复采集同一条内容不会重复进入报告，但不同律所任务可以分别评估同一条视频或笔记，避免多家律所监控时互相吞数据。

AI 配置保存时会校验 Provider 和 Temperature：Provider 仅支持 OpenAI Compatible / Anthropic，Temperature 范围为 `0` 到 `2`。邮件配置保存时会校验 SMTP 端口、加密方式和默认收件人邮箱格式。

AI 配置页会默认展示系统内置的负面舆情判断 Prompt，运营可以直接修改并保存；如果改乱了，可以点击“恢复默认 Prompt”再保存。

AI 和邮件配置保存后会自动标记为“待重新测试”。验收状态只认最近一次测试成功：

- AI：点击“测试 AI”后，系统会保存当前配置，调用一次真实模型接口，并记录成功或失败原因。
- AI 测试会校验固定 JSON 字段：`is_related`、`is_negative`、`risk_level`、`reason`、`evidence_quotes`、`recommended_action`。接口能通但输出结构不符合要求时，仍会判定为测试失败。
- 邮件：点击“发送测试邮件”后，系统会保存当前配置，发送一封真实测试邮件，并记录成功或失败原因。
- 只填写配置但没有测试通过时，验收状态仍然显示“待完成”。

## 本地自测报告

报告中心的“生成自测报告”不会调用真实平台，也不会发送邮件。它会写入一条样例运行记录，并生成 HTML、Excel、Markdown 三个报告文件，用于验证入库、AI 兜底、报告预览和下载链路。真实交付前仍需使用正式关键词跑一次抖音、快手、小红书采集，并配置真实 AI 和 SMTP 进行验收。

## 平台登录态

服务器运行前，需要分别准备三个平台的浏览器 Profile。第一版推荐直接在后台完成登录：

1. 打开“账号登录”页。
2. 分别点击抖音、快手、小红书的“打开登录窗口”。
3. 在弹出的浏览器里完成扫码、手机号或平台安全验证。
4. 确认网页已登录后关闭该窗口。
5. 回后台点击“刷新登录状态”，再运行采集任务。

后台不在每个任务里暴露 `qrcode`、`phone`、`cookie` 选择。MediaCrawler 底层仍支持这些登录模式，但监控系统把它们统一沉淀为可复用的浏览器 Profile：运营只维护平台登录态，定时任务自动复用。

默认 Profile 路径：

```text
{MONITOR_BROWSER_DATA_DIR 或 browser_data}/cdp_dy_user_data_dir
{MONITOR_BROWSER_DATA_DIR 或 browser_data}/cdp_ks_user_data_dir
{MONITOR_BROWSER_DATA_DIR 或 browser_data}/cdp_xhs_user_data_dir
```

如果后台无法打开浏览器，或需要排查底层登录问题，可用 MediaCrawler CLI 备用命令分别登录一次：

```powershell
uv run python main.py --platform dy --lt qrcode --type search --keywords 登录测试 --headless false --cdp_connect_existing false --cdp_debug_port 9223 --save_data_option json --save_data_path monitor_data/login_probe
uv run python main.py --platform ks --lt qrcode --type search --keywords 登录测试 --headless false --cdp_connect_existing false --cdp_debug_port 9224 --save_data_option json --save_data_path monitor_data/login_probe
uv run python main.py --platform xhs --lt qrcode --type search --keywords 登录测试 --headless false --cdp_connect_existing false --cdp_debug_port 9225 --save_data_option json --save_data_path monitor_data/login_probe
```

扫码登录成功后关闭命令，再启动后台。定时任务默认使用无头模式复用这些 Profile。

## 浏览器环境变量

```powershell
$env:MONITOR_CRAWLER_HEADLESS = "true"
$env:MONITOR_CDP_CONNECT_EXISTING = "false"
```

如果要连接一个已经打开的调试浏览器：

```powershell
$env:MONITOR_CDP_CONNECT_EXISTING = "true"
$env:MONITOR_CDP_DEBUG_PORT = "9222"
```

也可以按平台指定端口：

```powershell
$env:MONITOR_CDP_DEBUG_PORT_DY = "9223"
$env:MONITOR_CDP_DEBUG_PORT_KS = "9224"
$env:MONITOR_CDP_DEBUG_PORT_XHS = "9225"
```

## 验证项

- `GET /api/monitor/health` 返回 `{"status":"ok"}`。
- `GET /api/monitor/readiness` 返回平台、AI、邮件、报告链路和真实报告的当前验收状态。
- 页面可以保存任务、暂停、恢复、立即运行。
- AI 和邮件必须完成真实测试并记录通过，才会在验收状态里显示已就绪。
- “三平台真实采集”必须看到抖音、快手、小红书都至少有一次成功采集且采到内容；如果平台进程成功但采集数为 0，验收状态会提示“已运行但未采到内容”，不算真实验收通过。
- AI 未配置或调用失败时，报告仍生成，并把内容标记为“待人工复核”。
- 重复采集同一 `platform + content_id` 时不会重复新增。
- 不同监控任务采到同一条内容时，会分别进入各自任务的 AI 评估和报告。
- 某个平台失败时，其他平台继续运行；日志中出现未登录时，运行摘要会提示需要重新登录。

## 真实验收顺序

1. 在“账号登录”页完成抖音、快手、小红书登录，并确认 Profile 都已发现且不提示重新登录。
2. 在 AI 配置页保存配置并点击“测试 AI”，直到验收状态显示 AI 已就绪。
3. 在邮件配置页保存配置并点击“发送测试邮件”，确认收件箱收到测试邮件。
4. 创建一个只勾选抖音的任务并立即运行，确认能生成真实报告。
5. 依次用快手、小红书完成同样验证，或创建三平台任务一次性运行。
6. 回到任务管理页刷新验收状态，确认“三平台真实采集”不再提示缺口或空结果。

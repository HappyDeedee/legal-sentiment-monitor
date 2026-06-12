# legal-sentiment-monitor

基于 MediaCrawler 的律所舆情监控 MVP。

本项目面向内部运营人员使用：在管理后台配置律所、关键词、平台、AI 接口和邮件规则后，系统会定时采集抖音、快手、小红书的公开搜索结果，做去重、时间范围过滤和 AI 初筛，生成 HTML 邮件、Excel 明细和 Markdown 报告。

> 说明：AI 判断只用于“疑似负面线索筛查”，不代表事实认定。采集和使用数据时应遵守目标平台规则、法律法规和项目许可证约束。

## 当前能力

- 管理后台：任务管理、AI 配置、邮件配置、运行记录、报告中心、验收状态。
- 支持平台：抖音、快手、小红书。
- 采集方式：通过子进程调用 MediaCrawler CLI。
- 调度方式：FastAPI 单进程内置 APScheduler。
- 存储方式：SQLite，本地文件持久化。
- AI 评估：支持 OpenAI Compatible 和 Anthropic。
- 报告输出：HTML 邮件正文、Excel 附件、Markdown 附件、后台预览和下载。
- 并发控制：全局默认并发 2，同平台默认并发 1，同一任务防重复运行。
- 增量控制：按任务、平台、内容 ID 去重，并按发布时间过滤。

## 快速启动

在项目根目录运行：

```powershell
.\start_webui.bat
```

打开后台：

```text
http://127.0.0.1:8080/monitor
```

命令行自检：

```powershell
.\monitor_cli.bat readiness
```

部署诊断：

```powershell
.\monitor_cli.bat doctor
```

生成本地自测报告：

```powershell
.\monitor_cli.bat selftest-report
```

立即运行指定任务：

```powershell
.\monitor_cli.bat run-job 1
```

按频率运行到期任务：

```powershell
.\monitor_cli.bat run-due
```

## 服务器部署

Windows 服务器建议使用不自动打开浏览器的服务脚本：

```powershell
.\start_monitor_service.bat
```

Linux 服务器可参考 systemd 示例：

```text
deploy/systemd/
```

完整部署、验收、部署诊断、排障、备份恢复流程见：

```text
docs/deployment_runbook.md
```

## 后台页面

任务管理页支持配置：

- 律所名称、别名、关键词、排除词
- 平台：抖音、快手、小红书
- 是否抓评论
- 采集范围：最近 1 天、7 天、30 天、自定义日期
- 抓取频率：每天、每 12 小时、每 6 小时、自定义 cron
- 邮件发送时间和收件邮箱
- 保存、立即运行、暂停、删除

AI 配置页支持：

- Provider：OpenAI Compatible / Anthropic
- Base URL、API Key、Model、Temperature
- 负面判断 Prompt
- 测试 AI

邮件配置页支持：

- SMTP Host、Port、SSL/STARTTLS
- 发件人、用户名、密码
- 邮件标题模板
- 默认收件人
- 测试邮件

报告中心支持：

- HTML 预览
- Excel / Markdown / HTML 下载
- 按律所、平台、风险等级、日期筛选

## 环境变量

可在服务器上显式指定持久化目录：

```powershell
$env:MONITOR_DATA_DIR = "D:\legal-sentiment-monitor\data"
$env:MONITOR_BROWSER_DATA_DIR = "D:\legal-sentiment-monitor\browser_data"
```

常用配置见 `.env.example`：

```text
MONITOR_DATA_DIR=
MONITOR_BROWSER_DATA_DIR=
MONITOR_CRAWLER_HEADLESS=true
MONITOR_CDP_CONNECT_EXISTING=false
MONITOR_CDP_DEBUG_PORT_DY=9223
MONITOR_CDP_DEBUG_PORT_KS=9224
MONITOR_CDP_DEBUG_PORT_XHS=9225
MONITOR_CRAWLER_TIMEOUT_SECONDS=900
MONITOR_JOB_LOCK_TTL_SECONDS=21600
```

## 平台登录态

服务器运行前，需要分别准备三个平台的浏览器 profile。默认路径：

```text
browser_data/cdp_dy_user_data_dir
browser_data/cdp_ks_user_data_dir
browser_data/cdp_xhs_user_data_dir
```

可以用可视化模式分别登录一次，再让定时任务复用 profile。具体命令和排障说明见：

```text
docs/legal_sentiment_monitor.md
```

## 验收标准

- 页面可以创建、保存、暂停、删除任务。
- AI 配置测试成功。
- 邮件配置测试成功。
- 抖音、快手、小红书均能完成一次真实采集。
- 能生成 HTML、Excel、Markdown 报告。
- 重复运行不会重复发送同一条内容。
- 指定最近 1 天时，不发送时间范围外内容。
- 某个平台失败时，其他平台继续运行。
- AI 失败时，报告仍生成，内容标记为“待人工复核”。
- 无风险时也发送正常日报。

## 开发验证

```powershell
uv run pytest tests/test_monitoring_mvp.py -q
```

当前 MVP 测试覆盖任务校验、去重、时间过滤、AI 输出契约、邮件附件类型、报告生成、调度、平台状态、敏感信息脱敏和任务锁恢复。

## 项目边界

第一版只做内部运营可用的轻量业务系统，不做：

- 多租户
- 复杂账号池
- 高并发采集平台
- 平台级反验证能力
- 商业化权限系统

后续可逐步增强账号池、代理池、PostgreSQL、多 Worker、权限管理和部署自动化。

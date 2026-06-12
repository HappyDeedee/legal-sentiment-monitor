# legal-sentiment-monitor 部署与验收 Runbook

本文件用于第一版 MVP 的服务器交付。目标是先把单机版本稳定跑通：一个 FastAPI 后台、一个 SQLite 数据目录、三平台浏览器 profile、一个内置调度器或外部 `run-due` 定时器。

## 1. 部署边界

第一版推荐单服务器部署：

- Web 后台：`uvicorn api.main:app`
- 调度：优先使用 Web 后台内置 APScheduler；如需更稳的外部兜底，可启用 `run-due` timer
- 数据：SQLite 文件
- 报告：本地 HTML / Excel / Markdown 文件
- 浏览器登录态：本机 profile 目录

第一版不建议同时运行多个 Web 进程，也不要给 `uvicorn` 开多 worker。系统检测到多 worker 环境变量时会自动停用内置调度器，避免重复触发任务；如果确实需要多 worker，请显式设置 `MONITOR_DISABLE_SCHEDULER=true`，并用外部 cron 或 systemd timer 调用 `monitor_cli.bat run-due` / `python -m api.monitoring.cli run-due`。

## 2. 目录规划

建议服务器目录：

```text
/opt/legal-sentiment-monitor/app
/opt/legal-sentiment-monitor/data
/opt/legal-sentiment-monitor/browser_data
```

说明：

- `app`：项目代码。
- `data`：SQLite、加密密钥、运行日志、报告、任务锁。
- `browser_data`：抖音、快手、小红书的浏览器 profile。

必须备份：

```text
/opt/legal-sentiment-monitor/data/monitor.sqlite
/opt/legal-sentiment-monitor/data/secret.key
/opt/legal-sentiment-monitor/browser_data/
```

`secret.key` 用于解密后台保存的 AI Key 和 SMTP 密码，丢失后旧密钥无法解密。

## 3. 环境变量

复制示例文件：

```bash
sudo cp /opt/legal-sentiment-monitor/app/deploy/systemd/legal-sentiment-monitor.env.example /etc/legal-sentiment-monitor.env
sudo nano /etc/legal-sentiment-monitor.env
```

推荐内容：

```text
MONITOR_HOST=0.0.0.0
MONITOR_PORT=8080
MONITOR_DATA_DIR=/opt/legal-sentiment-monitor/data
MONITOR_BROWSER_DATA_DIR=/opt/legal-sentiment-monitor/browser_data
MONITOR_CRAWLER_HEADLESS=true
MONITOR_CDP_CONNECT_EXISTING=false
MONITOR_CRAWLER_TIMEOUT_SECONDS=900
MONITOR_CRAWLER_MAX_RETRIES=1
MONITOR_CRAWLER_RETRY_DELAY_SECONDS=3
MONITOR_JOB_LOCK_TTL_SECONDS=21600
MONITOR_DISABLE_SCHEDULER=false
```

按平台固定 CDP 端口：

```text
MONITOR_CDP_DEBUG_PORT_DY=9223
MONITOR_CDP_DEBUG_PORT_KS=9224
MONITOR_CDP_DEBUG_PORT_XHS=9225
```

## 4. 启动方式

### Windows 服务器

前台启动后台服务：

```powershell
.\start_monitor_service.bat
```

默认监听：

```text
0.0.0.0:8080
```

如需指定地址和端口：

```powershell
$env:MONITOR_HOST="127.0.0.1"
$env:MONITOR_PORT="8080"
.\start_monitor_service.bat
```

本地开发时也可以继续使用：

```powershell
.\start_webui.bat
```

区别是 `start_webui.bat` 会自动打开浏览器，`start_monitor_service.bat` 不会。

### Linux systemd

安装服务示例：

```bash
sudo cp deploy/systemd/legal-sentiment-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now legal-sentiment-monitor
sudo systemctl status legal-sentiment-monitor
```

查看日志：

```bash
journalctl -u legal-sentiment-monitor -f
```

如需外部定时兜底：

```bash
sudo cp deploy/systemd/legal-sentiment-run-due.service /etc/systemd/system/
sudo cp deploy/systemd/legal-sentiment-run-due.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now legal-sentiment-run-due.timer
systemctl list-timers | grep legal-sentiment
```

注意：如果 Web 内置调度器已经运行，`run-due` timer 只作为兜底；同一任务有锁保护，不会同时跑两份。

## 5. 首次上线流程

1. 安装依赖：

```bash
uv sync
```

2. 启动后台：

```bash
uv run uvicorn api.main:app --host 0.0.0.0 --port 8080
```

3. 打开后台：

```text
http://服务器IP:8080/monitor
```

4. 生成本地自测报告：

```bash
uv run python -m api.monitoring.cli selftest-report
```

5. 查看验收状态：

```bash
uv run python -m api.monitoring.cli readiness
```

6. 运行本机部署诊断：

```bash
uv run python -m api.monitoring.cli doctor
```

`doctor` 会检查项目文件、uv 命令、数据目录写入权限、SQLite 表结构、三平台登录配置、AI/邮件配置、任务、报告链路和单进程调度环境。它不会调用真实平台、AI 或 SMTP，只用于发现部署基础问题。

## 6. 三平台登录态准备

第一版后台不要求运营人员在每个任务里选择 `qrcode`、`phone` 或 `cookie`。登录方式放在“账号登录”页，按平台统一配置：

- 抖音：浏览器 Profile / 扫码、手机号、Cookie。
- 快手：浏览器 Profile / 扫码、Cookie。MediaCrawler 当前快手手机号分支未实现，所以后台不开放快手手机号模式。
- 小红书：浏览器 Profile / 扫码、手机号、Cookie。

推荐流程是：

1. 打开后台“账号登录”页。
2. 不确定时保留默认的“浏览器 Profile / 扫码”。
3. 分别点击抖音、快手、小红书的“打开登录窗口”。
4. 在弹出的浏览器中按平台提示完成扫码、手机号或安全验证。
5. 确认网页已登录后关闭该登录窗口。
6. 回后台刷新登录状态，再执行真实采集。

这样做的目的，是把 MediaCrawler 的登录模式从“单次命令参数”变成可复用的平台账号配置。定时任务运行时只按平台配置调用 MediaCrawler，不需要运营在每个任务里重复选择登录方式。

默认 profile 目录：

```text
{MONITOR_BROWSER_DATA_DIR}/cdp_dy_user_data_dir
{MONITOR_BROWSER_DATA_DIR}/cdp_ks_user_data_dir
{MONITOR_BROWSER_DATA_DIR}/cdp_xhs_user_data_dir
```

如果后台无法打开浏览器，或需要排障，可使用 MediaCrawler CLI 的原始登录方式作为备用。可视化登录命令：

```bash
uv run python main.py --platform dy --lt qrcode --type search --keywords 登录测试 --headless false --cdp_connect_existing false --cdp_debug_port 9223 --save_data_option json --save_data_path /opt/legal-sentiment-monitor/data/login_probe
uv run python main.py --platform ks --lt qrcode --type search --keywords 登录测试 --headless false --cdp_connect_existing false --cdp_debug_port 9224 --save_data_option json --save_data_path /opt/legal-sentiment-monitor/data/login_probe
uv run python main.py --platform xhs --lt qrcode --type search --keywords 登录测试 --headless false --cdp_connect_existing false --cdp_debug_port 9225 --save_data_option json --save_data_path /opt/legal-sentiment-monitor/data/login_probe
```

登录完成后，在后台“平台状态”里应看到三平台登录配置可用。

如果 Linux 服务器没有桌面环境，可选择以下方式之一：

- 使用带桌面环境的服务器或远程桌面完成扫码登录。
- 在同系统环境的机器上准备好 `browser_data`，再整体同步到服务器的 `MONITOR_BROWSER_DATA_DIR`。
- 临时使用 Xvfb / VNC 完成一次可视化登录，再切回无头模式运行定时任务。
- 在“账号登录”页切换为 Cookie 登录，保存对应平台 Cookie。Cookie 会加密保存，页面只显示是否已保存。

不要把 `browser_data` 提交到 Git 仓库；它包含登录态和 Cookie。

## 7. 业务验收

按顺序完成：

1. 后台创建一个测试任务，只勾选抖音，关键词用真实可搜到的低风险词。
2. 配置 AI，点击“测试 AI”，直到显示最近测试通过。
3. 配置邮件，点击“发送测试邮件”，确认收件箱收到邮件。
4. 运行抖音任务，确认生成报告。
5. 分别勾选快手、小红书运行一次，确认三平台均有真实报告记录。
6. 回到“上线验收状态”，确认只剩业务允许的外部限制项；正式交付前应全部通过。

验收命令：

```bash
uv run python -m api.monitoring.cli readiness
```

## 8. 日常运维

查看任务：

```bash
uv run python -m api.monitoring.cli list-jobs
```

部署诊断：

```bash
uv run python -m api.monitoring.cli doctor
```

手动运行：

```bash
uv run python -m api.monitoring.cli run-job 1
```

执行到期任务：

```bash
uv run python -m api.monitoring.cli run-due
```

清理异常残留锁：

```bash
ls /opt/legal-sentiment-monitor/data/locks
```

通常不需要手动删除；超过 `MONITOR_JOB_LOCK_TTL_SECONDS` 后系统会自动回收。只有确认没有采集进程仍在运行时，才可以删除对应锁文件。

## 9. 常见问题

### readiness 显示 AI 未就绪

原因通常是：

- Base URL 填错。
- API Key 没权限。
- Model 名称不正确。
- 模型输出不是固定 JSON。

处理方式：在后台 AI 配置页点击“测试 AI”，查看失败原因。测试通过后 readiness 才会变为已就绪。

### readiness 显示邮件未就绪

原因通常是：

- SMTP Host / Port 不正确。
- SSL 和 STARTTLS 选错。
- 邮箱服务商要求授权码，不是登录密码。
- 默认收件人为空。

处理方式：在后台邮件配置页点击“发送测试邮件”，确认真实收到邮件。

### 平台显示需重新登录

原因通常是 profile 失效、平台要求验证、扫码登录过期。

处理方式：用第 6 节的可视化命令重新登录对应平台，再运行一次测试任务。

### 报告为空但手动搜索有结果

先检查：

- 采集范围是否过窄，例如最近 1 天。
- 关键词是否被排除词过滤。
- 平台搜索排序是否返回旧内容。
- 运行日志里是否有登录态失效或风控提示。

第一版会在外层做时间过滤和去重，时间范围外内容不会进入报告。

## 10. 备份与恢复

备份：

```bash
tar -czf legal-sentiment-backup-$(date +%F).tar.gz \
  /opt/legal-sentiment-monitor/data \
  /opt/legal-sentiment-monitor/browser_data
```

恢复：

```bash
sudo systemctl stop legal-sentiment-monitor
tar -xzf legal-sentiment-backup-YYYY-MM-DD.tar.gz -C /
sudo systemctl start legal-sentiment-monitor
```

恢复后执行：

```bash
uv run python -m api.monitoring.cli readiness
```

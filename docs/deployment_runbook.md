# legal-sentiment-monitor 部署 Runbook

本文用于第一版服务器交付。目标是先把单机版本稳定跑通：一个后台服务、一个数据目录、一个网页登录态目录、一个内置调度器或外部到期任务定时器。

## 1. 部署边界

第一版推荐单服务器部署：

- Web 后台：FastAPI 后台服务
- 调度：优先使用后台内置调度器；如需更稳的外部兜底，可启用到期任务定时器
- 数据：SQLite 文件
- 报告：本地 HTML / Excel / Markdown 文件
- 登录态：平台网页登录态目录

第一版不建议同时运行多个 Web 进程。系统检测到多进程环境时会自动停用内置调度器，避免重复触发任务；如果确实需要多进程，请显式关闭内置调度器，并由外部定时器触发到期任务执行。

## 2. 目录规划

建议服务器目录：

```text
/opt/legal-sentiment-monitor/app
/opt/legal-sentiment-monitor/data
/opt/legal-sentiment-monitor/browser_data
```

说明：

- `app`：项目代码。
- `data`：数据库、加密密钥、运行日志、报告、任务锁。
- `browser_data`：抖音、快手、小红书网页登录态。

必须备份：

```text
/opt/legal-sentiment-monitor/data/monitor.sqlite
/opt/legal-sentiment-monitor/data/secret.key
/opt/legal-sentiment-monitor/browser_data/
```

`secret.key` 用于解密后台保存的 AI Key、SMTP 密码、Cookie 和代理 URL，丢失后旧密钥无法解密。

## 3. 环境配置

复制示例配置文件：

```bash
sudo cp /opt/legal-sentiment-monitor/app/deploy/systemd/legal-sentiment-monitor.env.example /etc/legal-sentiment-monitor.env
sudo nano /etc/legal-sentiment-monitor.env
```

推荐配置：

```text
MONITOR_HOST=0.0.0.0
MONITOR_PORT=8080
MONITOR_DATA_DIR=/opt/legal-sentiment-monitor/data
MONITOR_BROWSER_DATA_DIR=/opt/legal-sentiment-monitor/browser_data
MONITOR_CRAWLER_HEADLESS=true
MONITOR_CDP_CONNECT_EXISTING=false
MONITOR_LOGIN_QR_HEADLESS=true
MONITOR_LOGIN_QR_TIMEOUT_MS=20000
MONITOR_LOGIN_QR_TTL_SECONDS=600
MONITOR_CRAWLER_TIMEOUT_SECONDS=900
MONITOR_CRAWLER_MAX_RETRIES=1
MONITOR_CRAWLER_RETRY_DELAY_SECONDS=3
MONITOR_JOB_LOCK_TTL_SECONDS=21600
MONITOR_DISABLE_SCHEDULER=false
```

AI 是增强能力，不是采集前置条件。未配置或未启用 AI 时，采集和报告仍会继续，内容会进入待人工复核。

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

本地开发也可以继续使用：

```powershell
.\start_webui.bat
```

区别是服务脚本不会自动打开浏览器。

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

同一任务有锁保护，不会同时跑两份。

## 5. 首次上线流程

1. 安装依赖。
2. 启动后台服务。
3. 打开后台：

```text
http://服务器IP:8080/monitor
```

4. 进入“系统配置 -> 系统诊断”，确认基础环境、数据目录、数据库、调度器状态正常。
5. 进入“资源管理 -> 平台账号”，为目标平台准备登录态。
6. 进入“资源管理 -> AI 接入”，配置模型连接；再进入“系统配置 -> AI 评估规则”，配置 Prompt。
7. 进入“系统配置 -> 邮件配置 / 邮件模板”，配置 SMTP 和报告模板。
8. 进入“舆情监控”，创建测试任务并立即运行。
9. 进入“运行中心”，查看运行状态和日志。
10. 进入“报告中心”，确认 HTML 预览、线索明细和附件下载正常。

测试数据建议统一使用：

- 律所：海安律所
- 关键词：海安律所避雷、海安律所退费、海安律所投诉

## 6. 平台登录态准备

第一版后台不要求运营人员在每个任务里选择底层登录参数。登录方式放在“资源管理 -> 平台账号”中维护：

- 抖音：二维码、手机号、Cookie、已有网页登录态。
- 快手：二维码、Cookie、已有网页登录态；手机号登录入口暂不开放。
- 小红书：二维码、手机号、Cookie、已有网页登录态。

推荐流程：

1. 打开后台“资源管理 -> 平台账号”。
2. 添加对应平台账号。
3. 选择登录方式。
4. 二维码方式下点击“发起登录”，前端展示二维码、登录状态或验证提示。
5. 运营人员扫码或按平台提示处理。
6. 系统轮询登录状态并保存网页登录态。
7. 回到账号列表刷新状态，再执行真实采集。

如果平台先出现滑块、验证码或短信验证，系统只回传验证状态、截图或提示，不做绕过。人工处理后保持会话打开，继续轮询登录状态。

“本地窗口登录”只作为兜底方案，适合本地开发、远程桌面或二维码回传不稳定时使用。

账号池是轻量调度预留，不做复杂轮换。任务可以绑定账号资源；未绑定时系统使用平台默认登录材料。

默认网页登录态目录：

```text
{MONITOR_BROWSER_DATA_DIR}/cdp_dy_user_data_dir
{MONITOR_BROWSER_DATA_DIR}/cdp_ks_user_data_dir
{MONITOR_BROWSER_DATA_DIR}/cdp_xhs_user_data_dir
```

如果 Linux 服务器没有桌面环境，可选择：

- 使用带桌面环境的服务器或远程桌面完成扫码登录。
- 在同系统环境的机器上准备好 `browser_data`，再整体同步到服务器。
- 临时使用 Xvfb / VNC 完成一次可视化登录，再切回无头模式运行定时任务。
- 在账号页面切换为 Cookie 登录并保存 Cookie。

不要把 `browser_data` 提交到 Git 仓库；它包含登录态和 Cookie。

## 7. 业务验证顺序

按顺序完成：

1. 在“平台账号”页完成抖音登录，并确认状态可用。
2. 配置 AI 接入并完成连接测试；如暂不配置，采集仍可运行，线索进入待人工复核。
3. 配置邮件和模板，发送一封测试邮件。
4. 创建一个只勾选抖音的任务，关键词使用“海安律所避雷、海安律所退费、海安律所投诉”。
5. 立即运行任务。
6. 在运行中心确认运行记录、日志、采集数、新增数、失败原因显示正常。
7. 在报告中心确认报告预览、线索明细和下载正常。
8. 抖音闭环稳定后，再按同样流程扩展快手和小红书。

## 8. 日常运维

建议每天关注：

- 总览页的调度器状态。
- 最近失败任务。
- 平台登录状态。
- 待复核线索。
- 报告发送记录。

任务失败时，优先查看运行中心日志。常见原因包括登录态失效、平台验证、关键词无结果、采集范围过窄、邮件配置错误或 AI 服务异常。

## 9. 常见问题

### AI 显示未就绪

常见原因：

- Base URL 填错。
- API Key 没权限。
- Model 名称不正确。
- 模型输出不是固定 JSON。

处理方式：在“资源管理 -> AI 接入”页面做连接测试；在“系统配置 -> AI 评估规则”页面测试 Prompt 输出结构。

### 邮件发送失败

常见原因：

- SMTP Host / Port 不正确。
- SSL 和 STARTTLS 选错。
- 邮箱服务商要求授权码，不是登录密码。
- 默认收件人为空。

处理方式：在邮件配置页发送测试邮件，确认收件箱收到邮件。

### 平台显示需重新登录

常见原因是网页登录态失效、平台要求验证或扫码登录过期。

处理方式：进入平台账号页重新发起登录；如果二维码不可用，可使用本地窗口登录兜底。

### 报告为空但手动搜索有结果

先检查：

- 采集范围是否过窄，例如最近 1 天。
- 关键词是否被排除词过滤。
- 平台搜索排序是否返回旧内容。
- 运行日志里是否有登录态失效或验证提示。

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

恢复后进入后台“系统配置 -> 系统诊断”确认状态。

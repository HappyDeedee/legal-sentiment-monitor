# Docker Deployment Notes

This Docker path is for server-like validation and small single-server pilot
deployment. It keeps the browser inside the container and does not rely on the
operator's desktop Chrome or Edge.

## First Run

From the repository root:

```bash
cp deploy/docker/monitor.env.example deploy/docker/monitor.env
docker compose build
docker compose up -d
docker compose logs -f legal-sentiment-monitor
```

Open:

```text
http://127.0.0.1:8080/monitor
```

Replace `MONITOR_ADMIN_EMAIL` and `MONITOR_ADMIN_PASSWORD` in
`deploy/docker/monitor.env` before using a shared machine or public network.

## Persistent Data

The compose file mounts:

```text
deploy/docker/data -> /app/monitor_data
deploy/docker/browser_data -> /app/browser_data
```

These folders hold the SQLite database, secret key, reports, run logs, account
profiles, and browser login state. They are intentionally ignored by Git.

## Server-Like Defaults

The default env keeps conservative first-run behavior:

```text
MONITOR_LOGIN_QR_HEADLESS=true
MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=false
MONITOR_DISABLE_SCHEDULER=true
MONITOR_SKIP_AI_API=true
```

Real pilot operation should enable scheduler, AI, and mail only after account
resources, profile persistence, and operator approval are verified.

## Host Health Boundary

A passing `docker compose config` check proves only that the project packaging
is structurally valid. Docker Desktop, WSL, Hyper-V, `vmcompute`, and network
health remain host responsibilities.

Useful non-destructive Windows host checks:

```powershell
docker info
wsl.exe --status
wsl.exe --list --all --verbose
Get-Service -Name LxssManager,vmcompute,hns
```

If Docker Desktop cannot connect to `dockerDesktopLinuxEngine`, or if
`vmcompute` fails with `0x80070005` / `Access is denied`, repair the host
Docker/WSL/Hyper-V environment before treating build failures as project
packaging failures.

# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/api/main.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#
# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

"""
MediaCrawler WebUI API Server
Start command: uvicorn api.main:app --port 8080 --reload
Or: python -m api.main
"""
import asyncio
import os
import subprocess
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

from .monitoring.database import init_db
from .monitoring.scheduler import start_scheduler
from .routers import crawler_router, data_router, monitor_router, websocket_router

app = FastAPI(
    title="律所舆情监控系统",
    description="面向运营人员的律所舆情监控后台",
    version="1.0.0"
)

# Get webui static files directory
WEBUI_DIR = os.path.join(os.path.dirname(__file__), "webui")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# CORS configuration - allow frontend dev server access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Backup port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(crawler_router, prefix="/api")
app.include_router(data_router, prefix="/api")
app.include_router(monitor_router, prefix="/api")
app.include_router(websocket_router, prefix="/api")


@app.on_event("startup")
async def startup_monitoring():
    init_db()
    await start_scheduler()


@app.get("/")
async def serve_frontend():
    return RedirectResponse(url="/monitor")


@app.get("/monitor")
async def serve_monitor_frontend():
    """Return monitoring admin page"""
    page_path = os.path.join(os.path.dirname(__file__), "monitor_web", "index.html")
    if os.path.exists(page_path):
        return FileResponse(page_path)
    return {"message": "monitor admin page not found"}


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/env/check")
async def check_environment():
    """Check if the collection runtime is ready."""
    try:
        # Use a thread-backed subprocess call so the check works on Windows
        # when uvicorn reload uses an event loop without async subprocess support.
        process = await asyncio.to_thread(
            subprocess.run,
            ["uv", "run", "main.py", "--help"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=30.0,
        )

        if process.returncode == 0:
            return {
                "success": True,
                "message": "采集运行环境可用",
                "output": "运行环境检查通过",
            }
        else:
            return {
                "success": False,
                "message": "采集运行环境检查未通过",
                "error": "请联系技术人员检查服务依赖",
            }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": "采集运行环境检查超时",
            "error": "请稍后重试或联系技术人员",
        }
    except FileNotFoundError:
        return {
            "success": False,
            "message": "运行环境未就绪",
            "error": "请联系技术人员完成服务依赖安装",
        }
    except Exception as e:
        return {
            "success": False,
            "message": "采集运行环境检查异常",
            "error": f"{type(e).__name__}",
        }


@app.get("/api/config/platforms")
async def get_platforms():
    """Get list of supported platforms"""
    return {
        "platforms": [
            {"value": "xhs", "label": "Xiaohongshu", "icon": "book-open"},
            {"value": "dy", "label": "Douyin", "icon": "music"},
            {"value": "ks", "label": "Kuaishou", "icon": "video"},
            {"value": "bili", "label": "Bilibili", "icon": "tv"},
            {"value": "wb", "label": "Weibo", "icon": "message-circle"},
            {"value": "tieba", "label": "Baidu Tieba", "icon": "messages-square"},
            {"value": "zhihu", "label": "Zhihu", "icon": "help-circle"},
        ]
    }


@app.get("/api/config/options")
async def get_config_options():
    """Get all configuration options"""
    return {
        "login_types": [
            {"value": "qrcode", "label": "QR Code Login"},
            {"value": "cookie", "label": "Cookie Login"},
        ],
        "crawler_types": [
            {"value": "search", "label": "Search Mode"},
            {"value": "detail", "label": "Detail Mode"},
            {"value": "creator", "label": "Creator Mode"},
        ],
        "save_options": [
            {"value": "jsonl", "label": "JSONL File"},
            {"value": "json", "label": "JSON File"},
            {"value": "csv", "label": "CSV File"},
            {"value": "excel", "label": "Excel File"},
            {"value": "sqlite", "label": "SQLite Database"},
            {"value": "db", "label": "MySQL Database"},
            {"value": "mongodb", "label": "MongoDB Database"},
        ],
    }


# Mount static resources - must be placed after all routes
if os.path.exists(WEBUI_DIR):
    assets_dir = os.path.join(WEBUI_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    # Mount logos directory
    logos_dir = os.path.join(WEBUI_DIR, "logos")
    if os.path.exists(logos_dir):
        app.mount("/logos", StaticFiles(directory=logos_dir), name="logos")
    # Mount other static files (e.g., vite.svg)
    app.mount("/static", StaticFiles(directory=WEBUI_DIR), name="webui-static")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

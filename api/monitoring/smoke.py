from __future__ import annotations

from pathlib import Path
from typing import Any

from .doctor import run_doctor
from .readiness import get_readiness_status
from .selftest import create_sample_report


async def run_smoke_check() -> dict[str, Any]:
    """Run local non-external checks that prove the internal report pipeline works."""

    selftest = await create_sample_report()
    report = selftest["report"]
    artifacts = _artifact_summary(report)
    doctor = run_doctor()
    readiness = get_readiness_status()
    return {
        "ok": all(item["exists"] for item in artifacts.values()),
        "selftest": {
            "job_id": selftest["job"]["id"],
            "run_id": selftest["run_id"],
            "report_id": report["id"],
            "summary": selftest["summary"],
            "artifacts": artifacts,
        },
        "doctor": {
            "ok": doctor.get("ok"),
            "failed_checks": [
                {"key": item.get("key"), "label": item.get("label"), "message": item.get("message")}
                for item in doctor.get("checks", [])
                if not item.get("ok")
            ],
            "recommendations": doctor.get("recommendations") or [],
        },
        "readiness": {
            "ready": readiness.get("ready"),
            "failed_checks": [
                {"key": item.get("key"), "label": item.get("label"), "message": item.get("message")}
                for item in readiness.get("checks", [])
                if not item.get("ok")
            ],
            "next_actions": readiness.get("next_actions") or [],
        },
        "note": "本地 smoke 不调用真实平台、AI 或 SMTP；它只验证数据库、报告生成、HTML/Excel/Markdown 产物和诊断汇总链路。",
    }


def _artifact_summary(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "html": _artifact_item(report, "html_path", "html"),
        "excel": _artifact_item(report, "excel_path", "excel"),
        "markdown": _artifact_item(report, "markdown_path", "markdown"),
    }


def _artifact_item(report: dict[str, Any], key: str, download_type: str) -> dict[str, Any]:
    path = Path(str(report.get(key) or ""))
    exists = path.exists()
    return {
        "exists": exists,
        "path": str(path),
        "size": path.stat().st_size if exists else 0,
        "download_url": f"/api/monitor/reports/{report['id']}/download?type={download_type}",
    }

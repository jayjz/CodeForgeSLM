"""AgentForge PM orchestration."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, MutableMapping, Optional

from core.agents import (
    AgentContext,
    LeadArchitect,
    ReportGeneratorAgent,
    RequirementsAgent,
    RiskForecasterAgent,
    SchedulerOptimizerAgent,
)

logger = logging.getLogger("agentforge_pm.orchestrator")


async def run_pm_job(
    *,
    job_id: str,
    goals: List[str],
    project_path: Optional[str] = None,
    jobs: Optional[MutableMapping[str, Any]] = None,
    config_path: str | Path = "config.yaml",
) -> Dict[str, Any]:
    """Run the PM multi-agent workflow and update the API jobs store."""

    memory: Dict[str, Any] = {}

    async def progress_callback(callback_job_id: str, progress: float, detail: str) -> None:
        if jobs is None or callback_job_id not in jobs:
            return
        job = jobs[callback_job_id]
        if hasattr(job, "progress"):
            job.progress = progress
        if hasattr(job, "details"):
            job.details = detail

    def scoped_progress(start: float, end: float):
        async def callback(callback_job_id: str, progress: float, detail: str) -> None:
            overall = start + ((end - start) * max(0.0, min(1.0, progress)))
            await progress_callback(callback_job_id, overall, detail)

        return callback

    context = AgentContext(job_id=job_id, project_path=project_path, goals=goals)
    base_common = {"config_path": config_path, "memory": memory}

    try:
        _set_job(jobs, job_id, status="RUNNING", progress=0.02, details="AgentForge PM job started.")

        architect = LeadArchitect(**base_common, progress_callback=scoped_progress(0.02, 0.25))
        architect_result = await architect.run(context)
        if not architect_result.success:
            raise RuntimeError("; ".join(architect_result.errors))

        project_data = architect_result.data["project_data"]
        execution_plan = architect_result.data["execution_plan"]

        requirements = RequirementsAgent(**base_common, progress_callback=scoped_progress(0.25, 0.42))
        req_result = await requirements.run(context, {"project_data": project_data, "execution_plan": execution_plan})
        if not req_result.success:
            raise RuntimeError("; ".join(req_result.errors))

        risk = RiskForecasterAgent(**base_common, progress_callback=scoped_progress(0.42, 0.62))
        risk_result = await risk.run(context, {**req_result.data, "project_data": project_data})
        if not risk_result.success:
            raise RuntimeError("; ".join(risk_result.errors))

        scheduler = SchedulerOptimizerAgent(**base_common, progress_callback=scoped_progress(0.62, 0.82))
        schedule_result = await scheduler.run(context, {**req_result.data, **risk_result.data, "project_data": project_data})
        if not schedule_result.success:
            raise RuntimeError("; ".join(schedule_result.errors))

        reporter = ReportGeneratorAgent(**base_common, progress_callback=scoped_progress(0.82, 0.98))
        report_result = await reporter.run(context, {**req_result.data, **risk_result.data, **schedule_result.data})
        if not report_result.success:
            raise RuntimeError("; ".join(report_result.errors))

        result = {
            "execution_plan": execution_plan,
            **req_result.data,
            **risk_result.data,
            **schedule_result.data,
            **report_result.data,
        }
        _set_job(jobs, job_id, status="COMPLETED", progress=1.0, details="AgentForge PM job complete.", result=result)
        return result
    except Exception as exc:
        logger.exception("PM job failed: %s", job_id)
        _set_job(jobs, job_id, status="FAILED", progress=1.0, details=f"AgentForge PM job failed: {exc}")
        raise


def _set_job(
    jobs: Optional[MutableMapping[str, Any]],
    job_id: str,
    *,
    status: Optional[str] = None,
    progress: Optional[float] = None,
    details: Optional[str] = None,
    result: Optional[Dict[str, Any]] = None,
) -> None:
    if jobs is None or job_id not in jobs:
        return
    job = jobs[job_id]
    for key, value in {"status": status, "progress": progress, "details": details, "result": result}.items():
        if value is not None and hasattr(job, key):
            setattr(job, key, value)

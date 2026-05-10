from __future__ import annotations

import asyncio
from io import BytesIO
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from core.orchestrator import run_pm_job


DEFAULT_GOALS = [
    "Build an HVAC retrofit PM baseline.",
    "Identify procurement, controls, construction, and budget risks.",
    "Create an executive-ready schedule and action summary.",
]


def main() -> None:
    st.set_page_config(page_title="AgentForge PM", layout="wide")
    inject_styles()

    st.title("AgentForge PM")
    st.caption("Multi-agent project management baseline for HVAC, construction, and automation work.")

    source_mode, project_path, goals = render_sidebar()

    left, right = st.columns([0.72, 0.28], vertical_alignment="bottom")
    with left:
        st.subheader("Run PM Analysis")
        st.write("Review the source and goals, then run the orchestrator.")
    with right:
        run_clicked = st.button("Run AgentForge PM", type="primary", use_container_width=True)

    if run_clicked:
        effective_path = None if source_mode == "synthetic" else project_path
        if source_mode == "upload" and not effective_path:
            st.warning("Upload at least one project file or switch to synthetic HVAC data.")
            return

        with st.status("Starting AgentForge PM agents...", expanded=True) as status:
            progress = st.progress(0, text="Queued.")
            try:
                result = run_job_with_live_progress(effective_path, goals, progress, status)
            except Exception as exc:
                status.update(label="AgentForge PM failed.", state="error", expanded=True)
                st.exception(exc)
                return
            status.update(label="AgentForge PM complete.", state="complete", expanded=False)

        st.session_state["pm_result"] = result

    result = st.session_state.get("pm_result")
    if result:
        render_results(result)
    else:
        st.info("Run the dashboard with uploaded PM artifacts or the built-in synthetic HVAC data.")


def render_sidebar() -> tuple[str, str | None, list[str]]:
    with st.sidebar:
        st.header("Project Source")

        if st.button("Use Synthetic HVAC Data", use_container_width=True):
            st.session_state["source_mode"] = "synthetic"
            st.session_state.pop("upload_dir", None)

        uploaded_files = st.file_uploader(
            "Upload folder files",
            type=["txt", "md", "csv", "xlsx", "xlsm", "pdf"],
            accept_multiple_files=True,
            help="Select the files from a project folder. Supported: TXT, MD, CSV, Excel, PDF.",
        )

        if uploaded_files:
            st.session_state["source_mode"] = "upload"
            st.session_state["upload_dir"] = save_uploaded_files(uploaded_files)

        source_mode = st.session_state.get("source_mode", "synthetic")
        project_path = st.session_state.get("upload_dir")

        if source_mode == "synthetic":
            st.success("Using synthetic HVAC retrofit data.")
        else:
            st.success(f"Using uploaded files in {project_path}.")

        st.divider()
        st.header("Goals")
        goal_text = st.text_area(
            "One goal per line",
            value="\n".join(st.session_state.get("goals", DEFAULT_GOALS)),
            height=140,
        )
        goals = [line.strip() for line in goal_text.splitlines() if line.strip()]
        st.session_state["goals"] = goals or DEFAULT_GOALS

        return source_mode, project_path, st.session_state["goals"]


def save_uploaded_files(uploaded_files: list[Any]) -> str:
    upload_dir = Path(tempfile.mkdtemp(prefix="agentforge_pm_upload_"))
    for uploaded in uploaded_files:
        safe_name = Path(uploaded.name).name
        destination = upload_dir / safe_name
        destination.write_bytes(uploaded.getbuffer())
    return str(upload_dir)


def run_job_with_live_progress(project_path: str | None, goals: list[str], progress: Any, status: Any) -> dict[str, Any]:
    job_id = f"streamlit-pm-{uuid4().hex[:10]}"
    jobs = {
        job_id: SimpleNamespace(
            job_id=job_id,
            status="PENDING",
            progress=0.0,
            details="Queued.",
            result=None,
        )
    }

    async def runner() -> dict[str, Any]:
        task = asyncio.create_task(
            run_pm_job(
                job_id=job_id,
                goals=goals,
                project_path=project_path,
                jobs=jobs,
            )
        )
        while not task.done():
            job = jobs[job_id]
            progress.progress(min(float(job.progress), 1.0), text=job.details)
            status.write(job.details)
            await asyncio.sleep(0.35)

        result = await task
        job = jobs[job_id]
        progress.progress(min(float(job.progress), 1.0), text=job.details)
        return result

    return asyncio.run(runner())


def render_results(result: dict[str, Any]) -> None:
    report = result.get("pm_report", {})
    requirements_df = pd.DataFrame(result.get("requirements_register", []))
    risks_df = pd.DataFrame(result.get("risk_register", []))
    schedule_df = pd.DataFrame(result.get("optimized_schedule", {}).get("tasks", []))

    st.divider()
    metric_cols = st.columns(4)
    metric_cols[0].metric("Requirements", report.get("requirements_count", len(requirements_df)))
    metric_cols[1].metric("High Risks", report.get("high_risk_count", 0))
    metric_cols[2].metric("Planned Days", report.get("planned_duration_days", "n/a"))
    metric_cols[3].metric("Schedule Method", result.get("optimized_schedule", {}).get("method", "n/a"))

    st.subheader("Requirements Register")
    st.dataframe(requirements_df, hide_index=True, use_container_width=True)
    download_csv("Download Requirements CSV", requirements_df, "agentforge_requirements.csv")

    st.subheader("Risk Register")
    risk_table, risk_chart = st.columns([0.62, 0.38])
    with risk_table:
        st.dataframe(risks_df, hide_index=True, use_container_width=True)
        download_csv("Download Risk CSV", risks_df, "agentforge_risks.csv")
    with risk_chart:
        chart_path = report.get("risk_chart_path")
        if chart_path and Path(chart_path).exists():
            st.image(chart_path, caption="Top PM risks", use_container_width=True)
            st.download_button(
                "Download Risk Chart PNG",
                data=Path(chart_path).read_bytes(),
                file_name="agentforge_risk_chart.png",
                mime="image/png",
                use_container_width=True,
            )
        elif not risks_df.empty:
            png = build_risk_chart_png(risks_df)
            st.image(png, caption="Top PM risks", use_container_width=True)
            st.download_button(
                "Download Risk Chart PNG",
                data=png,
                file_name="agentforge_risk_chart.png",
                mime="image/png",
                use_container_width=True,
            )

    st.subheader("Schedule Baseline")
    if not schedule_df.empty:
        st.pyplot(build_gantt_figure(schedule_df), use_container_width=True)
        st.dataframe(schedule_df, hide_index=True, use_container_width=True)
        download_csv("Download Schedule CSV", schedule_df, "agentforge_schedule.csv")
    else:
        st.info("No schedule tasks were returned.")

    st.subheader("Executive Summary")
    st.markdown(f"**Summary:** {report.get('summary', 'No summary returned.')}")
    critical_path = report.get("critical_path") or result.get("optimized_schedule", {}).get("critical_path", [])
    if critical_path:
        st.markdown(f"**Critical path:** {' -> '.join(str(item) for item in critical_path)}")
    actions = report.get("recommended_actions", [])
    if actions:
        st.markdown("**Recommended actions**")
        for action in actions:
            st.write(f"- {action}")


def download_csv(label: str, frame: pd.DataFrame, file_name: str) -> None:
    if frame.empty:
        return
    st.download_button(
        label,
        data=frame.to_csv(index=False).encode("utf-8"),
        file_name=file_name,
        mime="text/csv",
        use_container_width=True,
    )


def build_risk_chart_png(risks_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(8, 4))
    plot_df = risks_df.sort_values("score", ascending=True)
    ax.barh(plot_df["risk"].astype(str), plot_df["score"].astype(float), color="#256d7b")
    ax.set_xlabel("Risk score")
    ax.set_title("Top PM Risks")
    fig.tight_layout()
    output = BytesIO()
    fig.savefig(output, format="png", dpi=160)
    plt.close(fig)
    return output.getvalue()


def build_gantt_figure(schedule_df: pd.DataFrame) -> plt.Figure:
    frame = schedule_df.sort_values("start_day", ascending=True).copy()
    frame["start_day"] = pd.to_numeric(frame["start_day"], errors="coerce").fillna(0)
    frame["duration_days"] = pd.to_numeric(frame["duration_days"], errors="coerce").fillna(1)

    fig, ax = plt.subplots(figsize=(10, max(3, len(frame) * 0.55)))
    ax.barh(
        frame["task"].astype(str),
        frame["duration_days"],
        left=frame["start_day"],
        color="#2f6f73",
        edgecolor="#16383d",
    )
    ax.set_xlabel("Project day")
    ax.set_ylabel("")
    ax.set_title("Optimized Schedule")
    ax.grid(axis="x", alpha=0.18)
    ax.invert_yaxis()
    fig.tight_layout()
    return fig


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: #f7f8f6;
        }
        [data-testid="stSidebar"] {
            background: #eef2ef;
        }
        h1, h2, h3 {
            color: #16383d;
            letter-spacing: 0;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #d9e1dc;
            border-radius: 8px;
            padding: 14px 16px;
        }
        .stButton > button, .stDownloadButton > button {
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

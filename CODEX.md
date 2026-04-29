# AgentForge PM - Project Rules

## Stack
- Python/FastAPI backend
- Multi-agent orchestration (Lead Architect + specialists)
- PyTorch/NumPy for risk forecasting, PuLP/OR-Tools for scheduling
- Streamlit/Gradio frontend for PM dashboard

## Conventions (enforce these)
- All new agents follow existing CodeForgeSLM pattern
- Use type hints everywhere
- Comprehensive error handling + logging
- Tests before any core change
- Domain: HVAC/Construction/Automation PM (scope, risk, schedule, stakeholders)

## Tools & Commands
- pytest for tests
- docker compose up for local
- git workflow: feature branches → PRs
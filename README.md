# genai-data-insights (mini WW-FBA) — Build 1

This repository is a local reproducible prototype for a GenAI-powered Data Insights Assistant.
Build 1: infra + dev app (Postgres + Chroma + Streamlit).

## Quickstart (one line)
```bash
cp .env.sample .env && # edit .env to set POSTGRES_PASSWORD (and optionally OPENAI_API_KEY)
docker compose up --build

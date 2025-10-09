# genai-data-insights (mini WW-FBA) — Build 2

This repository is a local reproducible prototype for a GenAI-powered Data Insights Assistant.
Build 1: infra + dev app (Postgres + Chroma + Streamlit).
Build 2: Added airflow + elt process + basic unit test

## Quickstart (one line)
```bash
cp .env.sample .env && # edit .env to set POSTGRES_PASSWORD (and optionally OPENAI_API_KEY)
docker compose up --build

# 🧠 GenAI Data Insights Assistant (mini WW-FBA)

> A full-stack GenAI-powered analytics assistant — combining ETL (Airflow + dbt + Postgres) with a semantic layer (Chroma + LangChain) and an interactive Streamlit UI for text-to-SQL insights.

---

## 🚀 Overview
This prototype lets you ask questions such as:
> “Show total revenue by order month”  
<!-- > “Top 5 products by average shipment delay” -->

and automatically:
1. Retrieves schema context from Chroma (vector DB)  
2. Generates SQL using LangChain + OpenAI (or local Llama fallback)  
3. Executes queries on Postgres  
4. Displays results and charts in Streamlit  

---

## 🧩 Architecture
            ┌──────────────────────────────────────┐
            │           Streamlit UI               │
            │  (User Query + SQL + Visualization)  │
            └──────────────────────────────────────┘
                              │
                              ▼
             ┌────────────────────────────────┐
             │   LangChain Text-to-SQL Agent  │
             │  (Prompting + Validation + Run)│
             └────────────────────────────────┘
                              │
       ┌──────────────────────┼────────────────────────┐
       ▼                      ▼                        ▼
┌────────────┐        ┌─────────────┐          ┌────────────────┐
│  Postgres  │        │   ChromaDB  │          │   dbt Models   │
│  Warehouse │        │ Vector Store│          │  Semantic Layer│
└────────────┘        └─────────────┘          └────────────────┘
       ▲                                               │
       │                                               ▼
       └─────────────── Apache Airflow ────────────────┘
                  (ETL orchestration)


## 🧰 Tech Stack
| Layer | Tool | Purpose |
|-------------------|---------------------------|----------|
| Language          | Python 3.11 + Poetry      | Dependency management |
| Data Warehouse    | PostgreSQL 15             | Raw + transformed data |
| Orchestration     | Apache Airflow 2.7        | ETL DAGs |
| Transformations   | dbt                       | SQL models & tests |
| Vector DB         | Chroma 1.1.1              | Semantic schema store |
| LLM Orchestration | LangChain + OpenAI GPT-4  | Text-to-SQL |
| UI                | Streamlit + Plotly        | Visualization |
| Data Quality      | Great Expectations        | Validation |
| Containerization  | Docker Compose            | Reproducible stack |


## ⚡ Quickstart
```bash
git clone https://github.com/gauraang01/genai-insights-assistant.git
cd genai-insights-assistant

cp .env.sample .env
# Edit .env → set POSTGRES_PASSWORD (and optionally OPENAI_API_KEY)

# Setup infra
docker compose up -d
poetry install


# Airflow
URL: http://localhost:8080
Login: admin / admin

Enable and trigger genai_data_etl_dag → loads sample CSVs into Postgres.

# Dbt
export DBT_PROFILES_DIR=./dbt
poetry run dbt compile     # Build manifest.json for semantic layer
poetry run dbt run         # Create tables/views in Postgres


# Semantic layer
poetry run python semantic/semantic_builder.py
poetry run python semantic/build_semantic_index.py


# Run agent
poetry run python -m agent.text_to_sql_agent

# Run streamlit UI from docker:
http://localhost:8501/
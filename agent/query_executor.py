# agent/query_executor.py
from sqlalchemy import create_engine, text
import os
import pandas as pd


def run_query(sql: str) -> pd.DataFrame:
    """Execute SQL against Postgres using env vars (works both locally & in Docker)."""
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "genai")
    password = os.getenv("POSTGRES_PASSWORD", "changeme")
    database = os.getenv("POSTGRES_DB", "genai_db")

    engine_url = (
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    )

    engine = create_engine(engine_url)

    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)
        return df
    except Exception as e:
        raise RuntimeError(f"Database query failed: {e}")

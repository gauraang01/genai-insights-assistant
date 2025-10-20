from sqlalchemy import create_engine, text
import os, pandas as pd

def run_query(sql: str) -> pd.DataFrame:
    engine = create_engine(
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@localhost:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    )
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)
    return df

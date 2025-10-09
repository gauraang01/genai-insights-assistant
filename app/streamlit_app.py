import os
import time
import streamlit as st
import requests
import psycopg2
from psycopg2.extras import RealDictCursor

st.set_page_config(page_title="GenAI Data Insights", layout="wide")


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB", "genai_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "genai")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "changeme")
CHROMA_HTTP_URL = os.getenv("CHROMA_HTTP_URL", "http://localhost:8000")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Postgres check")
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            connect_timeout=5,
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT 1 as ok;")
        row = cur.fetchone()
        st.success(f"Connected to Postgres `{POSTGRES_DB}` as `{POSTGRES_USER}` — query returned: {row['ok']}")
        # show tables (may be empty)
        cur.execute("""SELECT table_schema, table_name FROM information_schema.tables
                       WHERE table_schema NOT IN ('pg_catalog','information_schema') LIMIT 10;""")
        rows = cur.fetchall()
        st.write("Sample tables (may be empty):", rows or "No user tables yet")
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Postgres connection failed: {e}")

with col2:
    st.subheader("Chroma check")
    try:
        resp = requests.get(f"{CHROMA_HTTP_URL}/docs", timeout=5)
        if resp.status_code == 200:
            st.success(f"Chroma server OK at `{CHROMA_HTTP_URL}` — /docs reachable.")
        else:
            st.warning(f"Chroma responded with status {resp.status_code}")
    except Exception as e:
        st.error(f"Chroma connection failed: {e}")

st.markdown("---")
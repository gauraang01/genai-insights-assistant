# app/streamlit_app.py
import os
import sys
import time
import socket
import requests
import psycopg2
from psycopg2.extras import RealDictCursor

import streamlit as st
import pandas as pd
import plotly.express as px
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils import run_user_query, load_query_logs


# ------------------------------------------------------------------------------
# Config
# ------------------------------------------------------------------------------
st.set_page_config(page_title="GenAI Data Insights Assistant", layout="wide")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB", "genai_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "genai")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "changeme")
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_HTTP_URL = f"http://{CHROMA_HOST}:8000"

# ------------------------------------------------------------------------------
# Helper: Port-level connectivity test
# ------------------------------------------------------------------------------
def wait_for_port(host: str, port: int, timeout: int = 20):
    """Wait until a TCP port is reachable (Postgres, Chroma, etc.)."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except OSError:
            time.sleep(1)
    return False


# ------------------------------------------------------------------------------
# Section 1: Health Checks (Postgres + Chroma)
# ------------------------------------------------------------------------------
st.title("Environment Connectivity Check")

col1, col2 = st.columns(2)

# Postgres check
with col1:
    st.subheader("Postgres connectivity")
    if not wait_for_port(POSTGRES_HOST, POSTGRES_PORT):
        st.error(f"Could not connect to {POSTGRES_HOST}:{POSTGRES_PORT}. Is Postgres running?")
    else:
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
            st.success(
                f"Connected to `{POSTGRES_DB}` as `{POSTGRES_USER}` — query returned: {row['ok']}"
            )

            cur.execute(
                """SELECT table_schema, table_name 
                   FROM information_schema.tables 
                   WHERE table_schema NOT IN ('pg_catalog','information_schema') 
                   LIMIT 10;"""
            )
            tables = cur.fetchall()
            st.write("📋 Sample tables:", tables or "No user tables yet.")
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Postgres connection failed: {e}")

# Chroma check
with col2:
    st.subheader("Chroma connectivity")
    chroma_host = CHROMA_HTTP_URL.replace("http://", "").split(":")[0]
    chroma_port = int(CHROMA_HTTP_URL.split(":")[-1])

    if not wait_for_port(chroma_host, chroma_port):
        st.error(f"Could not reach {CHROMA_HTTP_URL}. Is Chroma running?")
    else:
        try:
            resp = requests.get(f"{CHROMA_HTTP_URL}/api/v2/heartbeat", timeout=5)
            if resp.status_code == 200:
                st.success(f"Chroma heartbeat OK at `{CHROMA_HTTP_URL}`.")
            else:
                st.warning(f"⚠️ Chroma responded with {resp.status_code}: {resp.text}")
        except Exception as e:
            st.error(f"Chroma connection failed: {e}")

st.markdown("---")

# ------------------------------------------------------------------------------
# Section 2: App — Query Assistant & History
# ------------------------------------------------------------------------------
st.title("🤖 GenAI-Powered Data Insights Assistant")

st.sidebar.header("Options")
view_mode = st.sidebar.radio("Select view", ["Query Assistant", "Query History"])

# -------------------------------------------------------------------
# Query Assistant
# -------------------------------------------------------------------
if view_mode == "Query Assistant":
    st.subheader("Ask a question about your data")

    question = st.text_area("Your question", placeholder="e.g., show total revenue by order month")
    run_button = st.button("Run Query", type="primary")

    if run_button and question.strip():
        with st.spinner("Running query..."):
            try:
                df = run_user_query(question)
                st.success("Query executed successfully!")

                # Display last generated SQL
                with open("logs/query_log.jsonl") as f:
                    last_line = list(f)[-1]
                    last_entry = json.loads(last_line)
                    sql = last_entry.get("sql", "")

                with st.expander("Generated SQL Query", expanded=True):
                    st.code(sql, language="sql")

                # Display results
                st.dataframe(df.head(20))

                # Chart suggestion
                numeric_cols = df.select_dtypes(include="number").columns
                if len(numeric_cols) >= 1:
                    fig = px.bar(df, x=df.columns[0], y=numeric_cols[0], title="Data Visualization")
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Error: {e}")

# -------------------------------------------------------------------
# Query History
# -------------------------------------------------------------------
elif view_mode == "Query History":
    st.subheader("📜 Recent Queries Log")
    logs_df = load_query_logs(20)
    if not logs_df.empty:
        st.dataframe(logs_df)
    else:
        st.info("ℹ️ No queries logged yet. Run some queries first!")

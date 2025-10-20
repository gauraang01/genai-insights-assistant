# app/streamlit_app.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px
from app.utils import run_user_query, load_query_logs
import json

st.set_page_config(page_title="GenAI Data Insights Assistant", layout="wide")

st.title("GenAI-Powered Data Insights Assistant")

st.sidebar.header("⚙️ Options")
view_mode = st.sidebar.radio("Select view", ["Query Assistant", "Query History"])

# -------------------------------------------------------------------
# Query Assistant
# -------------------------------------------------------------------
if view_mode == "Query Assistant":
    st.subheader("💬 Ask a question about your data")

    question = st.text_area("Your question", placeholder="e.g., show total revenue by order month")
    run_button = st.button("Run Query", type="primary")

    if run_button and question.strip():
        with st.spinner("Running query..."):
            try:
                df = run_user_query(question)
                st.success("Query executed successfully!")

                # Display SQL
                with open("logs/query_log.jsonl") as f:
                    last_line = list(f)[-1]
                    last_entry = json.loads(last_line)
                    sql = last_entry.get("sql", "")

                with st.expander("Generated SQL Query", expanded=True):
                    st.code(sql, language="sql")

                # Display Data
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
        st.info("No queries logged yet. Run some queries first!")

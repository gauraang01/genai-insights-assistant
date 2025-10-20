# app/utils.py

import json
import pandas as pd
from agent.text_to_sql_agent import query_agent

def run_user_query(question: str):
    """Run query through the agent and return results + SQL."""
    df = query_agent(question)
    return df

def load_query_logs(limit: int = 10):
    """Load recent query logs from logs/query_log.jsonl."""
    try:
        with open("logs/query_log.jsonl", "r") as f:
            lines = f.readlines()
        logs = [json.loads(line) for line in lines[-limit:]]
        return pd.DataFrame(logs)
    except FileNotFoundError:
        return pd.DataFrame(columns=["question", "sql", "rows"])

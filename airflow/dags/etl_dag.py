# airflow/dags/etl_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import os
import sys
import logging

# Ensure scripts path is in PYTHONPATH in the Airflow container or DAG env
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "..", "scripts")
SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

logger = logging.getLogger("airflow.etl.dag")

def run_ge_checks():
    from scripts import ge_checks
    ge_checks.run_checks()

def run_etl():
    from scripts import etl
    res = etl.run_etl()
    logger.info("ETL returned: %s", res)
    return res

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="genai_etl_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["genai", "sprint1"],
) as dag:

    t1 = PythonOperator(
        task_id="ge_checks",
        python_callable=run_ge_checks,
    )

    t2 = PythonOperator(
        task_id="run_etl",
        python_callable=run_etl,
    )

    t1 >> t2

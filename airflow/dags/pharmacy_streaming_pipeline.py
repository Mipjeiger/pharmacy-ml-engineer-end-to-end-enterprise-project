"""Airflow DAG Environment for Bronze -> Silver -> Gold Kafka streaming pipeline for pharmacy project."""

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PIPELINES_DIR = os.path.join(PROJECT_ROOT, "pipelines")

default_args = {
    "owner": "ml_engineer",
    "retries": 1,
}

with DAG(
    dag_id="pharmacy_streaming_pipeline",
    default_args=default_args,
    description="Bronze -> Silver -> Gold Kafka streaming pipeline for pharmacy project",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,  # Manual trigger with Airflow UI and Optional can change to automated schedule later
    catchup=False,
    tags=["kafka", "bronze", "silver", "gold"],
) as dag:

    start = EmptyOperator(task_id="start")

    bronze = BashOperator(
        task_id="bronze_ingestion",
        bash_command=f"cd {PROJECT_ROOT} && source .venv/bin/activate && python3 {PIPELINES_DIR}/bronze.py",
    )

    silver = BashOperator(
        task_id="silver_transformation",
        bash_command=f"cd {PROJECT_ROOT} && source .venv/bin/activate && python3 {PIPELINES_DIR}/silver.py",
    )

    gold = BashOperator(
        task_id="gold_aggregation",
        bash_command=f"cd {PROJECT_ROOT} && source .venv/bin/activate && python3 {PIPELINES_DIR}/gold.py",
    )

    end = EmptyOperator(task_id="end")

    start >> bronze >> silver >> gold >> end

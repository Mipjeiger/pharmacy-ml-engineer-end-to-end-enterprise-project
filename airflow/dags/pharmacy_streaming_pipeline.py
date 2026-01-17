"""Airflow DAG Environment for Bronze -> Silver -> Gold Kafka streaming pipeline for pharmacy project."""

import os
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from datetime import datetime, timedelta
from pipelines.utils.kafka_utils import get_kafka_consumer
from pipelines.utils.minio_utils import write_json
from pipelines.config import TOPIC_BRONZE, TOPIC_SILVER, TOPIC_GOLD


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PIPELINES_DIR = os.path.join(PROJECT_ROOT, "pipelines")
VENV_DIR = os.path.join(PROJECT_ROOT, ".venv/bin/python3")

# Define default arguments for the DAG
default_args = {
    "owner": "ml_engineer",
    "retries": 1,
    "retry_delay": timedelta(seconds=10),
}


def kafka_to_minio(topic, prefix, max_messages=2000):
    """Generic function to consume from Kafka topic and write to MinIO."""
    consumer = get_kafka_consumer(
        topic=topic,
        group_id=f"airflow-{prefix}-group",
        earliest=True,
    )

    count = 0

    # Consume messages and write to MinIO
    for msg in consumer:
        write_json(prefix=prefix, data=msg.value)
        count += 1

        if count >= max_messages:
            break

    # Close consumer connection
    consumer.close()


with DAG(
    dag_id="pharmacy_streaming_pipeline",
    default_args=default_args,
    description="Bronze -> Silver -> Gold Kafka streaming pipeline for pharmacy project",
    start_date=datetime(2026, 1, 1),
    schedule=None,  # Manual trigger with Airflow UI and Optional can change to automated schedule later
    catchup=False,
    tags=["kafka", "minio", "streaming", "pharmacy"],
) as dag:

    start = EmptyOperator(task_id="start")

    bronze = PythonOperator(
        task_id="bronze_to_minio",
        python_callable=kafka_to_minio,
        op_args=[TOPIC_BRONZE, "bronze"],
    )

    silver = PythonOperator(
        task_id="silver_to_minio",
        python_callable=kafka_to_minio,
        op_args=[TOPIC_SILVER, "silver"],
    )

    gold = PythonOperator(
        task_id="gold_to_minio",
        python_callable=kafka_to_minio,
        op_args=[TOPIC_GOLD, "gold"],
    )

    end = EmptyOperator(task_id="end")

    start >> bronze >> silver >> gold >> end

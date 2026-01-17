"""Airflow DAG Environment for Bronze -> Silver -> Gold Kafka streaming pipeline for pharmacy project."""

import os
import sys
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from datetime import datetime, timedelta

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

# Import pipeline functions
from pipelines.bronze import run_bronze_pipeline
from pipelines.silver import run_silver_pipeline
from pipelines.gold import run_gold_pipeline
from pipelines.utils.kafka_utils import get_kafka_consumer
from pipelines.utils.minio_utils import write_json
from pipelines.config import TOPIC_BRONZE, TOPIC_SILVER, TOPIC_GOLD

# Define default arguments for the DAG
default_args = {
    "owner": "ml_engineer",
    "retries": 1,
    "retry_delay": timedelta(seconds=10),
}


def bronze_task():
    """Run Bronze pipeline: DB -> Kafka Bronze topic."""
    run_bronze_pipeline(batch_limit=1000)


def silver_task():
    """Run Silver pipeline: Kafka Bronze -> Transform -> Kafka Silver topic."""
    run_silver_pipeline(max_messages=1000)


def gold_task():
    """Run Gold pipeline: Kafka Silver -> Aggregate -> Kafka Gold topic."""
    run_gold_pipeline(max_messages=2000)


def save_to_minio(topic, prefix, max_messages=2000):
    """Consume from Kafka topic and save to MinIO."""
    consumer = get_kafka_consumer(
        topic=topic,
        group_id=f"airflow-minio-{prefix}-group",
        earliest=True,
    )

    count = 0
    for msg in consumer:
        write_json(prefix=prefix, data=msg.value)
        count += 1

        if count >= max_messages:
            break

    consumer.close()


with DAG(
    dag_id="pharmacy_streaming_pipeline",
    default_args=default_args,
    description="Bronze -> Silver -> Gold Kafka streaming pipeline for pharmacy project",
    start_date=datetime(2025, 1, 1),
    schedule=None,  # Manual trigger with Airflow UI and Optional can change to automated schedule later
    catchup=False,
    tags=["kafka", "minio", "streaming", "pharmacy"],
) as dag:

    start = EmptyOperator(task_id="start")

    # Step 1: Bronze layer - DB to Kafka
    bronze_ingestion = PythonOperator(
        task_id="bronze_ingestion",
        python_callable=bronze_task,
    )

    # Step 2: Silver layer - Transform and clean
    silver_transformation = PythonOperator(
        task_id="silver_transformation",
        python_callable=silver_task,
    )

    # Step 3: Gold layer - Aggregate
    gold_aggregation = PythonOperator(
        task_id="gold_aggregation",
        python_callable=gold_task,
    )

    # Step 4: Save Bronze data to MinIO
    save_bronze_to_minio = PythonOperator(
        task_id="save_bronze_to_minio",
        python_callable=save_to_minio,
        op_args=[TOPIC_BRONZE, "bronze", 1000],
    )

    # Step 5: Save Silver data to MinIO
    save_silver_to_minio = PythonOperator(
        task_id="save_silver_to_minio",
        python_callable=save_to_minio,
        op_args=[TOPIC_SILVER, "silver", 1000],
    )

    # Step 6: Save Gold data to MinIO
    save_gold_to_minio = PythonOperator(
        task_id="save_gold_to_minio",
        python_callable=save_to_minio,
        op_args=[TOPIC_GOLD, "gold", 2000],
    )

    end = EmptyOperator(task_id="end")

    # Pipeline flow:
    # 1. Bronze: DB -> Kafka
    # 2. Silver: Kafka Bronze -> Transform -> Kafka Silver
    # 3. Gold: Kafka Silver -> Aggregate -> Kafka Gold
    # 4. Save all layers to MinIO in parallel
    start >> bronze_ingestion >> silver_transformation >> gold_aggregation
    (
        gold_aggregation
        >> [save_bronze_to_minio, save_silver_to_minio, save_gold_to_minio]
        >> end
    )

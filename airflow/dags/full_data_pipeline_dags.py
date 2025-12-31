from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import requests

# ============================
# Slack Notification Function
# ============================

# Definre the path to the .env file
env_path = os.path.join(os.path.dirname(__file__), "../.env")
load_dotenv(dotenv_path=env_path)

SLACK_WEBHOOK_URL = os.getenv(
    "SLACK_WEBHOOK_URL"
)  # Make sure this variable is set in your .env file


# Create a function to send notifications to Slack
def notify_slack(context):
    webhook_url = SLACK_WEBHOOK_URL
    dag_id = context["dag"].dag_id
    task_id = context["task_instance"].task_id
    state = context["task_instance"].state

    message = {""}

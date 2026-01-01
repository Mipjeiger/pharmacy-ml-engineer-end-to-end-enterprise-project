import requests
import os

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def slack_alert(context):
    dag_id = context["dag"].dag_id
    task_id = context["task_instance"].task_id
    execution_date = context["execution_date"]
    log_url = context["task_instance"].log_url

    message = f"""
    ❌ *Airflow Alert*
    DAG: {dag_id}
    Task: {task_id}
    Execution Date: {execution_date}
    Logs: {log_url}
    """

    requests.post(SLACK_WEBHOOK_URL, json={"text": message})

import os
import requests
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)


def send_slack_notification(message: str):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    payload = {"text": message}

    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()


def main():
    try:
        send_slack_notification(
            "ETL Pharmacy Feature Store Pipeline Completed Successfully"
        )
    except Exception as e:
        print(f"Failed to send Slack notification: {e}")


if __name__ == "__main__":
    main()

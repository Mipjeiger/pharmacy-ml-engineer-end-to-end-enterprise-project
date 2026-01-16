import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

# Kafka Configuration
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP")

# Kafka Topics
TOPIC_BRONZE = os.getenv("TOPIC_BRONZE")
TOPIC_SILVER = os.getenv("TOPIC_SILVER")
TOPIC_GOLD = os.getenv("TOPIC_GOLD")

# MinIO Configuration
MINIO_BUCKET = os.getenv("MINIO_BUCKET")

# PostgreSQL Configuration
POSTGRES_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

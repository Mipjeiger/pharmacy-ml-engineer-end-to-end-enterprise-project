import json
from kafka import KafkaProducer, KafkaConsumer
from pipelines.config import KAFKA_BOOTSTRAP


def get_kafka_producer():
    """Create and return a Kafka producer."""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        linger_ms=10,  # Small delay to batch messages
        retries=3,  # Retry sending messages on failure
    )


def get_kafka_consumer(topic, group_id=None, earliest=True):
    """
    Create Kafka consumer with group support (important for Airflow + streaming).
    """

    return KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=group_id,  # offset management for multiple consumers stored in Kafka
        enable_auto_commit=True,  # automatically commit offsets
        auto_offset_reset="earliest" if earliest else "latest",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        consumer_timeout_ms=15000,  # Stop iteration (loop) if no message after 15 seconds (was 1000ms - too short!)
        max_poll_interval_ms=300000,  # 5 minutes - max time between polls before consumer is considered dead
        session_timeout_ms=60000,  # 60 seconds - max time for heartbeat before rebalance
        request_timeout_ms=70000,  # 70 seconds - slightly higher than session timeout
    )

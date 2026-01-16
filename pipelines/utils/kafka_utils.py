import json
from kafka import KafkaProducer, KafkaConsumer
from config import KAFKA_BOOTSTRAP


def get_kafka_producer():
    """Create and return a Kafka producer."""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )


def get_kafka_consumer(topic, earliest=True):
    """Create and return a Kafka consumer for a topic."""
    return KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest" if earliest else "latest",
    )

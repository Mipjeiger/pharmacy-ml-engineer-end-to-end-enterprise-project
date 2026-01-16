"""Streaming pipeline - Silver layer processing."""

import logging
from utils.kafka_utils import get_kafka_consumer, get_kafka_producer
from utils.minio_utils import write_json
from config import TOPIC_BRONZE, TOPIC_SILVER

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_record(data):
    """Clean and transform the raw record."""
    try:
        if data["price"] <= 0 or data["quantity"] is None:
            return None  # Invalid record

        data["sales_clean"] = data["price"] * data["quantity"]
        data["product_name"] = str(data["product_name"].strip().lower())
        return data
    except Exception as e:
        logger.error(f"Error cleaning record {data}: {e}")
        return None


def run_silver_pipeline(max_messages=1000):
    """Run the Silver layer pipeline: consume data from Bronze, clean it, and produce to Silver."""
    logger.info(
        f"Starting Silver layer pipeline, processing up to {max_messages} messages."
    )

    consumer = get_kafka_consumer(TOPIC_BRONZE)
    producer = get_kafka_producer()

    count = 0
    try:
        for msg in consumer:
            cleaned = clean_record(msg.value)

            if cleaned:
                # Send to kafka Silver topic
                producer.send(TOPIC_SILVER, value=cleaned)
                write_json("silver", cleaned)

                count += 1
                if count % 100 == 0:
                    logger.info(f"Processed {count} messages.")

            # Close logic after reaching max_messages
            if count >= max_messages:
                logger.info(f"Reached max messages limit: {max_messages}. Stopping.")
                break

    except Exception as e:
        logger.error(f"Error in Silver layer pipeline: {e}")
    finally:
        # Close resources for the messages not sent yet
        producer.flush()
        consumer.close()
        logger.info(f"Silver pipeline completed. Total records processed: {count}.")


# usage
if __name__ == "__main__":
    # Can be adjusted number of messages to process as needed
    run_silver_pipeline(max_messages=1000)

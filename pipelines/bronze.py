"""Bronze layer pipeline for pharmacy data (DB -> Kafka)."""

import logging
from utils.kafka_utils import get_kafka_producer
from utils.db_utils import fetch_pharmacy_sales
from config import TOPIC_BRONZE

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_bronze_pipeline(batch_limit=1000):
    """Run the Bronze layer pipeline: extract data and send to Kafka & MinIO."""
    producer = get_kafka_producer()
    count = 0

    logger.info(
        f"Starting Bronze layer pipeline, processing up to {batch_limit} (DB -> Kafka)."
    )

    # Ensure fetching can handle large datasets by limiting the number of records processed
    for record in fetch_pharmacy_sales():
        # Send to Kafka
        producer.send(TOPIC_BRONZE, value=record)

        count += 1
        if count >= batch_limit:
            logger.info(
                f"Processed {count} records, reaching batch limit of {batch_limit}. Stopping."
            )
            break

    # Ensure all messages are sent
    producer.flush()
    producer.close()
    logger.info(
        f"Bronze pipeline completed. Total records processed: {count} record sent."
    )


# usage
if __name__ == "__main__":
    run_bronze_pipeline(batch_limit=1000)

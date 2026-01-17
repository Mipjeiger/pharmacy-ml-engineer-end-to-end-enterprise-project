"""Streaming pipeline - Gold layer processing."""

import logging
from collections import defaultdict
from utils.kafka_utils import get_kafka_consumer, get_kafka_producer
from utils.minio_utils import write_json
from config import TOPIC_SILVER, TOPIC_GOLD

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Aggregation
agg = defaultdict(float)


def run_gold_pipeline(max_messages=2000):

    logger.info("Initializing aggregation dictionary.")

    consumer = get_kafka_consumer(
        TOPIC_SILVER, group_id="gold_pipeline_group", earliest=True
    )

    producer = get_kafka_producer()
    count = 0

    logger.info(
        f"Starting Gold layer pipeline, processing up to {max_messages} messages."
    )

    for msg in consumer:

        data = msg.value

        # Use 'get' to get security in case keys are data missing
        product = data.get("product_name")
        year = data.get("year")
        month = data.get("month")
        sales = data.get("sales_clean", 0)

        if not all([product, year, month]):
            logger.warning(f"Skipping record with missing fields: {data}")
            continue

        key = f"{product}_{year}_{month}"
        agg[key] += sales

        record = {
            "product_name": product,
            "year": year,
            "month": month,
            "total_sales": agg[key],
        }

        producer.send(TOPIC_GOLD, value=record)

        count += 1

        # Set checkpoint in every 100 messages received and break if max reached
        if count % 100 == 0:
            logger.info(f"Processed {count} messages.")
            if count >= max_messages:
                logger.info(f"Reached max messages limit: {max_messages}. Stopping.")
                break

    # Close resources connection for the messages not sent yet
    producer.flush()
    producer.close()
    consumer.close()
    logger.info(f"Gold pipeline completed. Total records processed: {count} records.")


# usage
if __name__ == "__main__":
    run_gold_pipeline(max_messages=1000)

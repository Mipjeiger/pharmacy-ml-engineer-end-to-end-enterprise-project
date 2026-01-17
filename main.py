import logging
import pandas as pd
import numpy as np
import os
from minio import Minio
from io import BytesIO
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 1.  Load environment variables from .env file
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    return load_dotenv(dotenv_path=env_path)


# 2. Initialize MinIO client
def init_minio():
    minio_client = Minio(
        f"{os.getenv('MINIO_HOST')}:{os.getenv('MINIO_PORT')}",
        access_key=os.getenv("MINIO_ROOT_USER"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
        secure=False,
    )
    return minio_client


# 3. Load data from MinIO (Gold Layer)
def load_gold_data(minio_client, bucket_name: str) -> pd.DataFrame:
    objects = list(minio_client.list_objects(bucket_name, prefix="gold/2018/April"))

    if not objects:
        logger.warning(
            f"No objects found in bucket '{bucket_name}' with prefix 'gold/2018/April'"
        )
        return None

    # Get the latest file based on the last modified timestamp
    latest_object = sorted(objects, key=lambda obj: obj.last_modified, reverse=True)[0]

    # Read the object data
    response = minio_client.get_object(bucket_name, latest_object.object_name)
    df = pd.read_parquet(BytesIO(response.read()))

    # Close the response
    response.close()
    response.release_conn()
    logger.info(
        f"Loaded data from {latest_object.object_name} in bucket '{bucket_name}'"
    )

    return df


# Create main function to execute the steps
def main():
    load_env()
    minio_client = init_minio()
    bucket_name = os.getenv("MINIO_BUCKET")
    gold_path = "gold/2018/April"
    try:
        gold_data = load_gold_data(minio_client, bucket_name)
        if gold_data is not None:
            logger.info(f"Data shape: {gold_data.shape}")
            logger.info(gold_data.head(10))

    except Exception as e:
        logger.error(f"Error loading gold data: {e}")


# Execute main function
if __name__ == "__main__":
    main()

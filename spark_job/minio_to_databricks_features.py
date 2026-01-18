import os
from pyspark.sql import SparkSession
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)


# Initialize Spark session function
def create_spark_session(app_name: str) -> SparkSession:
    return SparkSession.builder.appName(app_name).getOrCreate()


# Configure MinIO access for Spark
def configure_minio(spark: SparkSession) -> None:
    hadoop_conf = spark._jsc.hadoopConfiguration()

    hadoop_conf.set("fs.s3a.endpoint", os.getenv("MINIO_ENDPOINT"))
    hadoop_conf.set("fs.s3a.access.key", os.getenv("MINIO_ROOT_USER"))
    hadoop_conf.set("fs.s3a.secret.key", os.getenv("MINIO_ROOT_PASSWORD"))
    hadoop_conf.set("fs.s3a.path.style.access", "true")
    hadoop_conf.set("fs.s3a.connection.ssl.enabled", "false")


# Extract features from Gold layer data and save to Databricks feature store
def extract_gold_features(spark: SparkSession):
    path = os.getenv("MINIO_GOLD_PATH")
    return spark.read.parquet(path)


# Load features into Databricks feature store
def load_to_databricks(df):
    target_path = os.getenv("DATABRICKS_FEATURE_PATH")

    (df.write.format("delta").mode("overwrite").save(target_path))


def main():
    spark = create_spark_session("Pharmacy Features ETL offline store pipeline")
    configure_minio(spark=spark)

    df = extract_gold_features(spark=spark)
    load_to_databricks(df=df)

    print("ETL feature offline store process completed successfully.")
    spark.stop()  # Close the Spark session


if __name__ == "__main__":
    main()

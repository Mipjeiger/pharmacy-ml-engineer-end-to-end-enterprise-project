import subprocess
import sys


def run_spark_job():
    try:
        cmd = ["spark-submit", "spark_job/minio_to_databricks_features.py"]

        subprocess.run(cmd, check=True)
        print("Spark job executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing Spark job: {e}")
        sys.exit(1)


def main():
    run_spark_job()
    print("Offline feature extraction process completed.")


if __name__ == "__main__":
    main()

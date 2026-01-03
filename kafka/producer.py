from kafka import KafkaProducer
import json
import pandas as pd
import os


# Load dataset for pharmacy sales integration with Kafka
def load_data(file_path):
    return pd.read_csv(file_path)


df = load_data("../data/pharma-data.csv")

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

producer.send(
    "pharmacy_sales_topic",
    {
        "distributor": df["distributor"].tolist(),
        "product_name": df["product_name"].tolist(),
        "quantity": df["quantity"].tolist(),
        "price": df["price"].tolist(),
        "sales": df["sales"].tolist(),
        "city": df["city"].tolist(),
    },
)

producer.flush()

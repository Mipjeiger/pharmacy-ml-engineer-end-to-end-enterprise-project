from kafka import KafkaConsumer
import json
import psycopg2
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

consumer = KafkaConsumer(
    "pharmacy_sales_topic",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

with engine.connect() as conn:
    for msg in consumer:
        data = msg.value

        # Use conn.excute to insert data into the database if using SQLAlchemy
        conn.execute(
            text(
                """
                          INSERT INTO raw.pharmacy_sales
                          (distributor, quantity, price, sales, city)
                          VALUES (:distributor, :product_name, :quantity, :price, :sales, :city)
                            """
            ),
            {
                "distributor": data["distributor"],
                "product_name": data["product_name"],
                "quantity": data["quantity"],
                "price": data["price"],
                "sales": data["sales"],
                "city": data["city"],
            },
        )
        conn.commit()

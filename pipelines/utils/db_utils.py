import psycopg2
from pipelines.config import POSTGRES_CONFIG


def fetch_pharmacy_sales():
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cur = conn.cursor()

    cur.execute("SELECT * FROM raw.pharmacy_sales")
    cols = [desc[0] for desc in cur.description]

    # iterable of dicts
    for row in cur.fetchall():
        yield dict(zip(cols, row))

    # Close connections
    cur.close()
    conn.close()

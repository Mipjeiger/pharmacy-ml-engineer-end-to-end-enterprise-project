import json
import os
from datetime import datetime
from minio import Minio
from config import MINIO_BUCKET

# Initialize MinIO client
minio = Minio(
    os.getenv("MINIO_ENDPOINT", "localhost:9000"),
    access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
    secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
    secure=False,
)


def ensure_bucket():
    if not minio.bucket_exists(MINIO_BUCKET):
        minio.make_bucket(MINIO_BUCKET)


def write_json(prefix, data, path_suffix=None):
    ensure_bucket()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    path = f"{prefix}/{path_suffix}.json" if path_suffix else f"{prefix}/{ts}.json"

    payload = json.dumps(data).encode()
    minio.put_object(
        MINIO_BUCKET,
        path,
        data=payload,
        length=len(payload),
    )

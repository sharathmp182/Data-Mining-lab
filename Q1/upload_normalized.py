import boto3
from pathlib import Path

s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin"
)

bucket = "sales-data"
root = Path("lake/sales")

files = list(root.rglob("*.parquet"))

print("Parquet files:", len(files))

for path in files:
    key = path.relative_to(root).as_posix()
    s3.upload_file(str(path), bucket, key)

print("Upload completed:", len(files))
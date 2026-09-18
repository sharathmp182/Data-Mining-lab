import boto3
from pathlib import Path
import re

# MinIO connection
s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin",
    region_name="us-east-1"
)

bucket = "sales-data"
sales_dir = Path("./data/sales")

files = list(sales_dir.glob("SALES_*.csv"))

print(f"Found {len(files)} sales files.")
print("Starting upload...\n")

uploaded = 0
skipped = 0
failed = 0

for i, file in enumerate(files, 1):

    # Extract store and business date from filename
    match = re.match(r"SALES_(S\d+)_(\d{4})(\d{2})(\d{2})(?:__R\d+)?\.csv$", file.name)

    if not match:
        print(f"SKIP - filename format not recognized: {file.name}")
        skipped += 1
        continue

    store = match.group(1)
    year = match.group(2)
    month = match.group(3)

    key = f"year={year}/month={month}/store={store}/{file.name}"

    try:
        # Check whether this exact object already exists
        try:
            s3.head_object(Bucket=bucket, Key=key)
            skipped += 1
            print(f"[{i}/{len(files)}] EXISTS: {file.name}")
            continue
        except Exception:
            pass

        s3.upload_file(str(file), bucket, key)
        uploaded += 1
        print(f"[{i}/{len(files)}] UPLOADED: {key}")

    except Exception as e:
        failed += 1
        print(f"[{i}/{len(files)}] FAILED: {file.name} -> {e}")

print("\n========== UPLOAD SUMMARY ==========")
print(f"Total files : {len(files)}")
print(f"Uploaded    : {uploaded}")
print(f"Skipped     : {skipped}")
print(f"Failed      : {failed}")
print("====================================")
import csv
import re
import shutil
from pathlib import Path
from datetime import datetime
import pandas as pd

BASE = Path(__file__).resolve().parent
INPUT = BASE / "data" / "sales"
OUTPUT = BASE / "lake" / "sales"

seen = set()
rows = []

files_processed = 0
files_failed = 0

filename_pattern = re.compile(
    r"SALES_(S\d+)_(\d{4})(\d{2})(\d{2})(?:__R\d+)?\.csv$",
    re.IGNORECASE
)


def parse_file(path):

    match = filename_pattern.match(path.name)

    if not match:
        raise ValueError(f"Invalid filename: {path.name}")

    store_id = match.group(1)
    year = int(match.group(2))
    month = int(match.group(3))
    day = int(match.group(4))

    business_date = datetime(year, month, day).date()

    # Read header and detect delimiter
    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        first_line = f.readline().strip()

    delimiter = ";" if ";" in first_line else ","

    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(
            f,
            delimiter=delimiter
        )

        for raw in reader:

            # =====================================
            # S06-S09
            # =====================================
            if "item_code" in raw:

                bill_no = raw["bill_no"]
                line_no = int(raw["line_no"])
                product_code = raw["item_code"]
                qty = float(raw["quantity"])
                unit_price = float(raw["rate"])
                line_type = raw["type"].strip().upper()

                ts = datetime.strptime(
                    raw["txn_time"],
                    "%d-%m-%Y %H:%M:%S"
                )

            # =====================================
            # S10-S12
            # =====================================
            elif store_id in ["S10", "S11", "S12"]:

                bill_no = raw["bill_no"]
                line_no = int(raw["line_no"])
                product_code = raw["product_code"]
                qty = float(raw["qty"])
                unit_price = float(raw["unit_price"])
                line_type = raw["line_type"].strip().upper()

                # Unix epoch seconds, UTC
                ts = pd.to_datetime(
                    int(raw["ts"]),
                    unit="s",
                    utc=True
                ).tz_convert(None)

            # =====================================
            # S01-S05
            # =====================================
            elif store_id in ["S01", "S02", "S03", "S04", "S05"]:

                bill_no = raw["bill_no"]
                line_no = int(raw["line_no"])
                product_code = raw["product_code"]
                qty = float(raw["qty"])
                unit_price = float(raw["unit_price"])
                line_type = raw["line_type"].strip().upper()

                ts = pd.to_datetime(
                    raw["ts"]
                )

            else:
                raise ValueError(
                    f"Unknown CSV format: {path.name}"
                )

            # =====================================
            # LINE-LEVEL DEDUPLICATION
            # =====================================
            key = (bill_no, line_no)

            if key in seen:
                continue

            seen.add(key)

            # =====================================
            # REVENUE DEFINITION
            # =====================================
            #
            # INCLUDE:
            # SALE
            # RETURN
            # DISCOUNT
            # VOID
            #
            # EXCLUDE:
            # TAX
            # TENDER

            if line_type in {
                "SALE",
                "RETURN",
                "DISCOUNT",
                "VOID"
            }:
                revenue = qty * unit_price
            else:
                revenue = 0.0

            rows.append({
                "bill_no": bill_no,
                "line_no": line_no,
                "store_id": store_id,
                "business_date": business_date,
                "product_code": product_code,
                "qty": qty,
                "unit_price": unit_price,
                "line_type": line_type,
                "ts": ts,
                "revenue": revenue
            })


# ==========================================
# PROCESS ALL SALES FILES
# ==========================================

for path in sorted(INPUT.glob("SALES_*.csv")):

    try:

        parse_file(path)
        files_processed += 1

    except Exception as e:

        files_failed += 1

        print(
            f"FAILED: {path.name} -> {e}"
        )


# ==========================================
# SUMMARY
# ==========================================

print()
print("=" * 60)
print("NORMALIZATION COMPLETE")
print("=" * 60)

print(
    f"Files processed : {files_processed}"
)

print(
    f"Files failed    : {files_failed}"
)

print(
    f"Unique lines    : {len(rows)}"
)


if not rows:
    raise RuntimeError(
        "No sales rows were loaded."
    )


# ==========================================
# CREATE DATAFRAME
# ==========================================

df = pd.DataFrame(rows)

df["business_date"] = pd.to_datetime(
    df["business_date"]
)

df["year"] = df["business_date"].dt.year
df["month"] = df["business_date"].dt.month


# ==========================================
# REMOVE OLD PARQUET
# ==========================================

if OUTPUT.exists():
    shutil.rmtree(OUTPUT)

OUTPUT.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================
# WRITE PARTITIONED PARQUET
# ==========================================

df.to_parquet(
    OUTPUT,
    engine="pyarrow",
    partition_cols=[
        "year",
        "month",
        "store_id"
    ],
    index=False
)


# ==========================================
# FINAL OUTPUT
# ==========================================

print()
print("=" * 60)
print("PARQUET CREATED SUCCESSFULLY")
print("=" * 60)

print(
    f"Output folder : {OUTPUT}"
)

print(
    f"Rows written  : {len(df)}"
)

print(
    f"Columns       : {len(df.columns)}"
)

print("=" * 60)
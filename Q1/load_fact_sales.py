import duckdb
import psycopg2

PARQUET = r"lake/sales/**/*.parquet"

# Connect to PostgreSQL
pg = psycopg2.connect(
    host="localhost",
    port=5432,
    database="salesdb",
    user="labuser",
    password="labpass"
)

pg_cur = pg.cursor()

# Read normalized Parquet using DuckDB
duck = duckdb.connect()

query = f"""
SELECT
    bill_no,
    line_no,
    store_id,
    product_code,
    business_date,
    line_type,
    qty,
    unit_price,
    revenue
FROM read_parquet(
    '{PARQUET}',
    hive_partitioning=true
)
"""

rows = duck.execute(query).fetchall()

print("Parquet rows:", len(rows))

insert_sql = """
INSERT INTO fact_sales
(
    bill_no,
    line_no,
    store_key,
    product_key,
    date_key,
    line_type,
    quantity,
    unit_price,
    revenue
)
SELECT
    %s,
    %s,
    ds.store_key,
    dp.product_key,
    dd.date_key,
    %s,
    %s,
    %s,
    %s
FROM dim_store ds
LEFT JOIN dim_product dp
    ON dp.product_code = %s
    AND %s::date BETWEEN dp.valid_from AND dp.valid_to
JOIN dim_date dd
    ON dd.full_date = %s::date
WHERE ds.store_id = %s
ON CONFLICT (bill_no, line_no) DO NOTHING
"""

inserted = 0

for row in rows:
    bill_no, line_no, store_id, product_code, business_date, line_type, qty, unit_price, revenue = row

    pg_cur.execute(
        insert_sql,
        (
            bill_no,
            line_no,
            line_type,
            qty,
            unit_price,
            revenue,
            product_code,
            business_date,
            business_date,
            store_id
        )
    )

    if pg_cur.rowcount == 1:
        inserted += 1

    if inserted % 10000 == 0 and inserted > 0:
        pg.commit()
        print("Inserted:", inserted)

pg.commit()

pg_cur.execute("SELECT COUNT(*) FROM fact_sales")
total = pg_cur.fetchone()[0]

print("=" * 50)
print("FACT LOAD COMPLETE")
print("=" * 50)
print("Parquet rows :", len(rows))
print("Inserted     :", inserted)
print("Fact rows    :", total)

pg_cur.close()
pg.close()
duck.close()
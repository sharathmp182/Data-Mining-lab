import duckdb

con = duckdb.connect()

con.execute("INSTALL httpfs")
con.execute("LOAD httpfs")

con.execute("SET s3_endpoint='localhost:9000'")
con.execute("SET s3_access_key_id='minioadmin'")
con.execute("SET s3_secret_access_key='minioadmin'")
con.execute("SET s3_use_ssl=false")
con.execute("SET s3_url_style='path'")

con.execute("""
ATTACH 'host=localhost port=5432 dbname=salesdb user=labuser password=labpass'
AS pg (TYPE POSTGRES, READ_ONLY)
""")

query = """
SELECT
    p.category_id,
    pc.category_name,
    ROUND(SUM(s.revenue), 2) AS revenue
FROM read_parquet(
    's3://sales-data/year=2024/month=3/store_id=*/*.parquet',
    hive_partitioning=true
) s
JOIN pg.public.products p
    ON s.product_code = p.product_code
    AND CAST(s.business_date AS DATE)
        BETWEEN p.valid_from AND p.valid_to
JOIN pg.public.product_categories pc
    ON p.category_id = pc.category_id
WHERE CAST(s.business_date AS DATE)
      BETWEEN DATE '2024-03-01' AND DATE '2024-03-31'
GROUP BY
    p.category_id,
    pc.category_name
ORDER BY revenue DESC;
"""

print("EXPLAIN ANALYZE - MINIO + POSTGRESQL")
print("=" * 70)

plan = con.execute("EXPLAIN ANALYZE " + query).fetchall()

for row in plan:
    print(row[1])

print("=" * 70)
print("EXPLAIN ANALYZE completed successfully.")
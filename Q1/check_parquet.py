import duckdb

con = duckdb.connect()

result = con.execute("""
SELECT
    COUNT(*) AS rows,
    MIN(business_date) AS first_date,
    MAX(business_date) AS last_date
FROM read_parquet(
    'lake/sales/**/*.parquet',
    hive_partitioning=true
)
""").fetchdf()

print(result)
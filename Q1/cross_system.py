import duckdb

con = duckdb.connect()

# Connect DuckDB directly to PostgreSQL
con.execute("""
ATTACH 'host=localhost port=5432 dbname=salesdb user=labuser password=labpass'
AS pg (TYPE POSTGRES, READ_ONLY)
""")

query = """
SELECT
    p.category_id,
    pc.category_name,
    ROUND(SUM(s.revenue), 2) AS revenue
FROM read_parquet('lake/sales/**/*.parquet') s
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

result = con.execute(query).fetchall()

print("\nCross-system query result:")
print("--------------------------------")

for row in result:
    print(row)

print("\nSUCCESS: DuckDB queried Parquet + PostgreSQL directly.")
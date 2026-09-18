import duckdb

con = duckdb.connect()

con.execute("""
ATTACH 'host=localhost port=5432 dbname=salesdb user=labuser password=labpass'
AS pg (TYPE POSTGRES, READ_ONLY)
""")

result = con.execute("""
SELECT COUNT(*)
FROM pg.public.products
""").fetchone()

print("Products:", result[0])
print("DuckDB connected to PostgreSQL successfully")
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="salesdb",
    user="labuser",
    password="labpass"
)

cur = conn.cursor()

query = """
WITH params AS (
    SELECT
        DATE '2024-03-01' AS start_date,
        DATE '2024-04-01' AS end_date
)
SELECT
    ds.store_id,
    ds.store_name,
    ROUND(
        SUM(
            CASE
                WHEN f.line_type IN ('SALE','RETURN','VOID')
                    THEN f.quantity * pr.selling_price
                WHEN f.line_type = 'DISCOUNT'
                    THEN f.revenue
                ELSE 0
            END
        ), 2
    ) AS historical_revenue
FROM fact_sales f
JOIN dim_store ds
    ON f.store_key = ds.store_key
JOIN dim_product dp
    ON f.product_key = dp.product_key
JOIN price_revisions pr
    ON pr.product_sk = dp.product_sk
JOIN dim_date dd
    ON f.date_key = dd.date_key
CROSS JOIN params p
WHERE dd.full_date >= p.start_date
  AND dd.full_date < p.end_date
  AND dd.full_date >= pr.effective_from
  AND dd.full_date <= pr.effective_to
GROUP BY ds.store_id, ds.store_name
ORDER BY ds.store_id;
"""

cur.execute(query)

print("\n===== MARCH 2024 HISTORICAL PRICE =====")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
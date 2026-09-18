import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="salesdb",
    user="labuser",
    password="labpass"
)

cur = conn.cursor()

start_date = "2024-02-01"
end_date = "2024-03-01"

query = f"""
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
WHERE dd.full_date >= DATE '{start_date}'
  AND dd.full_date < DATE '{end_date}'
  AND dd.full_date >= pr.effective_from
  AND dd.full_date <= pr.effective_to
GROUP BY
    ds.store_id,
    ds.store_name
ORDER BY
    ds.store_id;
"""

cur.execute(query)

print("Historical revenue using February 2024 prices")
print("-" * 50)

for row in cur.fetchall():
    print(row[0], row[1], f"{row[2]:.2f}")

cur.close()
conn.close()
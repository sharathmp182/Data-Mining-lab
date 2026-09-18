import pandas as pd
import psycopg2

finance = pd.read_csv(r"data\finance_monthly.csv")

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="salesdb",
    user="labuser",
    password="labpass"
)

query = """
SELECT
    TO_CHAR(dd.full_date, 'YYYY-MM') AS month,
    ROUND(SUM(f.revenue), 2) AS pipeline_revenue
FROM fact_sales f
JOIN dim_date dd
    ON f.date_key = dd.date_key
GROUP BY TO_CHAR(dd.full_date, 'YYYY-MM')
ORDER BY month;
"""

pipeline = pd.read_sql_query(query, conn)
conn.close()

finance["month"] = finance["month"].astype(str)
pipeline["month"] = pipeline["month"].astype(str)

result = pipeline.merge(
    finance[["month", "revenue_inr"]],
    on="month",
    how="left"
)

result["difference"] = (
    result["pipeline_revenue"] - result["revenue_inr"]
).round(2)

print("\n================ FINANCE RECONCILIATION ================")
print(
    result.to_string(
        index=False,
        formatters={
            "pipeline_revenue": "{:.2f}".format,
            "revenue_inr": "{:.2f}".format,
            "difference": "{:.2f}".format
        }
    )
)
print("=========================================================")
import psycopg2
import hashlib

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="salesdb",
    user="labuser",
    password="labpass"
)

cur = conn.cursor()

cur.execute("""
    SELECT
        COUNT(*),
        COALESCE(SUM(row_count), 0),
        COALESCE(STRING_AGG(file_checksum, '' ORDER BY file_checksum), '')
    FROM loaded_files
""")

manifest_rows, total_rows, checksum_text = cur.fetchone()

checksum = hashlib.sha256(
    checksum_text.encode()
).hexdigest().upper()

print("=" * 50)
print("IDEMPOTENCY VERIFICATION")
print("=" * 50)
print("Manifest rows:", manifest_rows)
print("Total loaded source rows:", total_rows)
print("Manifest checksum:", checksum)

cur.close()
conn.close()
import os
import hashlib
import psycopg2

DATA_DIR = r"data\sales"

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="salesdb",
    user="labuser",
    password="labpass"
)

cur = conn.cursor()

files = []
for root, dirs, filenames in os.walk(DATA_DIR):
    for filename in filenames:
        if filename.lower().endswith(".csv"):
            files.append(os.path.join(root, filename))

files.sort()

loaded = 0
skipped = 0

for path in files:
    with open(path, "rb") as f:
        checksum = hashlib.sha256(f.read()).hexdigest()

    cur.execute(
        """
        SELECT 1
        FROM loaded_files
        WHERE file_checksum = %s
        """,
        (checksum,)
    )

    if cur.fetchone():
        skipped += 1
        continue

    row_count = 0

    with open(path, "rb") as f:
        for line in f:
            row_count += 1

    row_count -= 1

    cur.execute(
        """
        INSERT INTO loaded_files
            (source_path, file_checksum, row_count)
        VALUES
            (%s, %s, %s)
        """,
        (path, checksum, row_count)
    )

    loaded += 1

conn.commit()

print("=" * 50)
print("IDEMPOTENT LOAD COMPLETE")
print("=" * 50)
print("Total files :", len(files))
print("Loaded      :", loaded)
print("Skipped     :", skipped)

cur.execute("SELECT COUNT(*) FROM loaded_files")
print("Manifest rows:", cur.fetchone()[0])

cur.close()
conn.close()
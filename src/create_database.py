import sqlite3

DB_PATH = "db/nifty100.db"
SCHEMA_PATH = "db/schema.sql"

conn = sqlite3.connect(DB_PATH)

with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    schema = f.read()

conn.executescript(schema)

conn.commit()
conn.close()

print("Database created successfully!")

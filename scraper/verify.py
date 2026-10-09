import sqlite3

conn = sqlite3.connect("books.db")
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM books")
print("Total rows:", cur.fetchone()[0])

for col in ["title", "author", "year", "publisher", "pages", "language", "subject"]:
    cur.execute(f"SELECT COUNT(*) FROM books WHERE {col} IS NULL")
    print(f"NULL {col}: {cur.fetchone()[0]}")

print("\n--- Sample 3 rows ---")
cur.execute("SELECT id, title, author, year, pages FROM books LIMIT 3")
for row in cur.fetchall():
    print(row)

conn.close()
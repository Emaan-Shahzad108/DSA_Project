import json
import sqlite3

with open("books.json", encoding="utf-8") as f:
    books = json.load(f)

print(f"Loaded {len(books)} books from JSON.")

conn = sqlite3.connect("books.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    year INTEGER,
    publisher TEXT,
    isbn TEXT,
    pages INTEGER,
    language TEXT,
    subject TEXT,
    edition_count INTEGER,
    ol_key TEXT UNIQUE
)
""")

inserted = 0
for b in books:
    try:
        cur.execute("""
            INSERT OR IGNORE INTO books
            (title, author, year, publisher, isbn, pages,
             language, subject, edition_count, ol_key)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            b.get("title"),
            ", ".join(b.get("author_name", [])) if b.get("author_name") else None,
            b.get("first_publish_year"),
            ", ".join(b.get("publisher", [])[:3]) if b.get("publisher") else None,
            b.get("isbn", [None])[0] if b.get("isbn") else None,
            b.get("number_of_pages_median"),
            ", ".join(b.get("language", [])) if b.get("language") else None,
            ", ".join(b.get("subject", [])[:5]) if b.get("subject") else None,
            b.get("edition_count"),
            b.get("key")
        ))
        inserted += 1
    except Exception as e:
        print("Insert error:", e)

conn.commit()
conn.close()
print(f"Inserted {inserted} rows into books.db")
import requests
import time
import json
import threading

class BookScraper:
    def __init__(self):
        self.base_url = "https://openlibrary.org/search.json"
        self.headers = {
            "User-Agent": "DSA_Project/1.0 (emaanshahzad108@gmail.com)"
        }
        self.books = []
        self.seen_keys = set()
        self.paused = False
        self.stopped = False
        self.progress = 0
        self.target = 15000
        self.limit_per_page = 100

    def scrape(self, queries):
        for q in queries:
            if self.stopped or len(self.books) >= self.target:
                break
            print(f"\n=== Query: {q} ===")
            offset = 0
            while offset < 10000 and len(self.books) < self.target:
                while self.paused:
                    time.sleep(1)
                if self.stopped:
                    print("Stopped by user.")
                    return

                params = {
                    "q": q,
                    "limit": self.limit_per_page,
                    "offset": offset,
                    "fields": "title,author_name,first_publish_year,publisher,"
                              "isbn,number_of_pages_median,language,subject,"
                              "edition_count,key"
                }
                try:
                    r = requests.get(self.base_url, params=params,
                                     headers=self.headers, timeout=15)
                    if r.status_code != 200:
                        print(f"HTTP {r.status_code}, skipping...")
                        break

                    docs = r.json().get("docs", [])
                    if not docs:
                        break

                    for doc in docs:
                        key = doc.get("key")
                        if key and key not in self.seen_keys:
                            self.seen_keys.add(key)
                            self.books.append(doc)
                            self.progress = len(self.books)

                    offset += self.limit_per_page
                    print(f"Progress: {self.progress} / {self.target}")
                except Exception as e:
                    print("Error:", e)
                    time.sleep(3)

                time.sleep(0.5)

        print(f"\nScrape finished. Total unique books: {len(self.books)}")

    def pause(self):
        self.paused = True
        print("Paused.")

    def resume(self):
        self.paused = False
        print("Resumed.")

    def stop(self):
        self.stopped = True
        print("Stopping...")

    def save_json(self, filename="books.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.books, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(self.books)} books → {filename}")


if __name__ == "__main__":
    scraper = BookScraper()

    queries = [
        "subject:fiction",
        "subject:science",
        "subject:history",
        "subject:fantasy",
        "subject:romance",
        "subject:biography",
        "subject:philosophy",
        "subject:poetry",
        "subject:adventure",
        "subject:mystery"
    ]

    t = threading.Thread(target=scraper.scrape, args=(queries,))
    t.start()
    t.join()

    scraper.save_json("books.json")
    print("DONE.")
import asyncio
import aiohttp
import csv
import json
import time
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from typing import List, Optional


# ============================================================
# Configuration
# ============================================================

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

START_PAGE = 1
END_PAGE = 5

OUTPUT_JSON = "books_async.json"
OUTPUT_CSV = "books_async.csv"

MAX_CONCURRENT_REQUESTS = 5
REQUEST_TIMEOUT = 10


# ============================================================
# Data Model
# ============================================================

@dataclass
class Book:
    title: str
    price: str
    rating: str
    availability: str
    page: int


# ============================================================
# Async HTTP Client
# ============================================================

class AsyncScraper:

    def __init__(self, max_concurrent_requests: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def fetch(
        self,
        session: aiohttp.ClientSession,
        url: str,
        page_number: int
    ) -> Optional[str]:

        async with self.semaphore:

            print(f"[START] Fetching page {page_number}")

            try:
                async with session.get(url) as response:

                    if response.status != 200:
                        print(
                            f"[ERROR] Page {page_number} "
                            f"returned status {response.status}"
                        )
                        return None

                    html = await response.text()

                    print(f"[DONE] Page {page_number}")

                    return html

            except asyncio.TimeoutError:
                print(f"[TIMEOUT] Page {page_number}")

            except aiohttp.ClientError as error:
                print(
                    f"[HTTP ERROR] Page {page_number}: {error}"
                )

            except Exception as error:
                print(
                    f"[UNKNOWN ERROR] Page {page_number}: {error}"
                )

            return None


# ============================================================
# HTML Parser
# ============================================================

def parse_books(html: str, page_number: int) -> List[Book]:

    soup = BeautifulSoup(html, "html.parser")

    books = []

    products = soup.select("article.product_pod")

    for product in products:

        # ----------------------------------------------------
        # Title
        # ----------------------------------------------------

        title_element = product.select_one("h3 a")

        if title_element:
            title = title_element.get("title", "Unknown")
        else:
            title = "Unknown"

        # ----------------------------------------------------
        # Price
        # ----------------------------------------------------

        price_element = product.select_one(
            "p.price_color"
        )

        price = (
            price_element.get_text(strip=True)
            if price_element
            else "Unknown"
        )

        # ----------------------------------------------------
        # Rating
        # ----------------------------------------------------

        rating_element = product.select_one(
            "p.star-rating"
        )

        if rating_element:
            rating_classes = rating_element.get("class", [])

            rating = next(
                (
                    item
                    for item in rating_classes
                    if item != "star-rating"
                ),
                "Unknown"
            )
        else:
            rating = "Unknown"

        # ----------------------------------------------------
        # Availability
        # ----------------------------------------------------

        availability_element = product.select_one(
            "p.instock"
        )

        availability = (
            availability_element.get_text(
                " ",
                strip=True
            )
            if availability_element
            else "Unknown"
        )

        # ----------------------------------------------------
        # Create Book Object
        # ----------------------------------------------------

        book = Book(
            title=title,
            price=price,
            rating=rating,
            availability=availability,
            page=page_number
        )

        books.append(book)

    return books


# ============================================================
# Scrape Single Page
# ============================================================

async def scrape_page(
    scraper: AsyncScraper,
    session: aiohttp.ClientSession,
    page_number: int
) -> List[Book]:

    url = BASE_URL.format(page_number)

    html = await scraper.fetch(
        session,
        url,
        page_number
    )

    if html is None:
        return []

    books = parse_books(
        html,
        page_number
    )

    print(
        f"[PARSED] Page {page_number}: "
        f"{len(books)} books"
    )

    return books


# ============================================================
# Scrape All Pages Concurrently
# ============================================================

async def scrape_all_pages() -> List[Book]:

    scraper = AsyncScraper(
        MAX_CONCURRENT_REQUESTS
    )

    timeout = aiohttp.ClientTimeout(
        total=REQUEST_TIMEOUT
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/151.0 Safari/537.36"
        )
    }

    connector = aiohttp.TCPConnector(
        limit=MAX_CONCURRENT_REQUESTS
    )

    async with aiohttp.ClientSession(
        timeout=timeout,
        headers=headers,
        connector=connector
    ) as session:

        tasks = []

        for page_number in range(
            START_PAGE,
            END_PAGE + 1
        ):

            task = asyncio.create_task(
                scrape_page(
                    scraper,
                    session,
                    page_number
                )
            )

            tasks.append(task)

        print(
            f"\nCreated {len(tasks)} "
            f"asynchronous scraping tasks.\n"
        )

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True
        )

    all_books = []

    for result in results:

        if isinstance(result, Exception):

            print(
                f"[TASK ERROR] {result}"
            )

            continue

        all_books.extend(result)

    return all_books


# ============================================================
# Save JSON
# ============================================================

def save_json(books: List[Book]) -> None:

    data = [
        asdict(book)
        for book in books
    ]

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"\nJSON saved to: {OUTPUT_JSON}"
    )


# ============================================================
# Save CSV
# ============================================================

def save_csv(books: List[Book]) -> None:

    if not books:
        print("No data available for CSV.")
        return

    fieldnames = [
        "title",
        "price",
        "rating",
        "availability",
        "page"
    ]

    with open(
        OUTPUT_CSV,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for book in books:

            writer.writerow(
                asdict(book)
            )

    print(
        f"CSV saved to: {OUTPUT_CSV}"
    )


# ============================================================
# Display Statistics
# ============================================================

def display_statistics(
    books: List[Book]
) -> None:

    print("\n" + "=" * 60)
    print("SCRAPING STATISTICS")
    print("=" * 60)

    print(
        f"Total books scraped: {len(books)}"
    )

    if not books:
        return

    pages = set(
        book.page
        for book in books
    )

    print(
        f"Pages processed: {len(pages)}"
    )

    ratings = {}

    for book in books:

        ratings[book.rating] = (
            ratings.get(book.rating, 0) + 1
        )

    print("\nRating distribution:")

    for rating, count in sorted(
        ratings.items()
    ):

        print(
            f"  {rating}: {count}"
        )


# ============================================================
# Display Sample Results
# ============================================================

def display_sample(
    books: List[Book],
    amount: int = 10
) -> None:

    print("\n" + "=" * 60)
    print("SAMPLE RESULTS")
    print("=" * 60)

    for index, book in enumerate(
        books[:amount],
        start=1
    ):

        print(
            f"\n{index}. {book.title}"
        )

        print(
            f"   Price: {book.price}"
        )

        print(
            f"   Rating: {book.rating}"
        )

        print(
            f"   Availability: "
            f"{book.availability}"
        )

        print(
            f"   Page: {book.page}"
        )


# ============================================================
# Main Async Function
# ============================================================

async def main():

    print("=" * 60)
    print("ASYNC WEB SCRAPER")
    print("=" * 60)

    print(
        f"Pages: {START_PAGE} - {END_PAGE}"
    )

    print(
        f"Max concurrent requests: "
        f"{MAX_CONCURRENT_REQUESTS}"
    )

    print()

    start_time = time.perf_counter()

    books = await scrape_all_pages()

    elapsed_time = (
        time.perf_counter() - start_time
    )

    print(
        f"\nScraping completed in "
        f"{elapsed_time:.2f} seconds."
    )

    # --------------------------------------------------------
    # Display Results
    # --------------------------------------------------------

    display_sample(books)

    display_statistics(books)

    # --------------------------------------------------------
    # Save Results
    # --------------------------------------------------------

    save_json(books)
    save_csv(books)

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)


# ============================================================
# Program Entry Point
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())

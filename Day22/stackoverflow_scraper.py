import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://stackoverflow.com/questions/tagged/python"

PAGES_TO_SCRAPE = 3
OUTPUT_FILE = "stackoverflow_python_questions.csv"
REPORT_FILE = "stackoverflow_report.txt"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    )
}


# ============================================================
# FETCH PAGE
# ============================================================

def fetch_page(url):
    """Download a web page and return its HTML."""

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()

        return response.text

    except requests.exceptions.RequestException as error:
        print(f"Request error: {error}")
        return None


# ============================================================
# SCRAPE QUESTIONS
# ============================================================

def scrape_questions(html):
    """Extract question information from Stack Overflow HTML."""

    soup = BeautifulSoup(html, "html.parser")

    questions = soup.select("div.s-post-summary")

    results = []

    for question in questions:

        # ----------------------------------------------------
        # TITLE AND URL
        # ----------------------------------------------------

        title_element = question.select_one(
            "h3.s-post-summary--content-title a"
        )

        if not title_element:
            continue

        title = title_element.get_text(strip=True)

        url = "https://stackoverflow.com" + title_element.get("href")


        # ----------------------------------------------------
        # VOTES
        # ----------------------------------------------------

        votes_element = question.select_one(
            "span.s-post-summary--stats-item-number"
        )

        votes = 0

        if votes_element:
            try:
                votes = int(votes_element.get_text(strip=True))
            except ValueError:
                votes = 0


        # ----------------------------------------------------
        # ANSWERS
        # ----------------------------------------------------

        stats = question.select(
            "div.s-post-summary--stats-item"
        )

        answers = 0

        if len(stats) > 1:

            answer_element = stats[1].select_one(
                "span.s-post-summary--stats-item-number"
            )

            if answer_element:
                try:
                    answers = int(
                        answer_element.get_text(strip=True)
                    )
                except ValueError:
                    answers = 0


        # ----------------------------------------------------
        # VIEWS
        # ----------------------------------------------------

        views = 0

        if len(stats) > 2:

            view_element = stats[2].select_one(
                "span.s-post-summary--stats-item-number"
            )

            if view_element:

                view_text = view_element.get_text(strip=True)

                try:

                    if "k" in view_text.lower():
                        views = int(
                            float(
                                view_text.lower()
                                .replace("k", "")
                            ) * 1000
                        )

                    else:
                        views = int(view_text)

                except ValueError:
                    views = 0


        # ----------------------------------------------------
        # TAGS
        # ----------------------------------------------------

        tag_elements = question.select(
            "a.s-post-tag"
        )

        tags = [
            tag.get_text(strip=True)
            for tag in tag_elements
        ]


        # ----------------------------------------------------
        # ACTIVITY
        # ----------------------------------------------------

        date_element = question.select_one(
            "time"
        )

        activity_date = "Unknown"

        if date_element:
            activity_date = (
                date_element.get("datetime")
                or date_element.get_text(strip=True)
            )


        # ----------------------------------------------------
        # SAVE RESULT
        # ----------------------------------------------------

        results.append({
            "title": title,
            "url": url,
            "votes": votes,
            "answers": answers,
            "views": views,
            "tags": ", ".join(tags),
            "activity_date": activity_date
        })

    return results


# ============================================================
# SCRAPE MULTIPLE PAGES
# ============================================================

def scrape_stackoverflow():

    all_questions = []

    for page in range(1, PAGES_TO_SCRAPE + 1):

        print(f"\nScraping page {page}...")

        url = (
            f"{BASE_URL}?tab=newest"
            f"&page={page}"
        )

        html = fetch_page(url)

        if not html:
            print("Skipping page...")
            continue

        questions = scrape_questions(html)

        print(
            f"Found {len(questions)} questions."
        )

        all_questions.extend(questions)

        # Be polite to the server
        time.sleep(2)

    return all_questions


# ============================================================
# DATA ANALYSIS
# ============================================================

def analyze_data(df):

    print("\n" + "=" * 60)
    print("STACK OVERFLOW ANALYSIS")
    print("=" * 60)

    print(f"\nTotal questions: {len(df)}")

    print(
        f"Average votes: "
        f"{df['votes'].mean():.2f}"
    )

    print(
        f"Average answers: "
        f"{df['answers'].mean():.2f}"
    )

    print(
        f"Average views: "
        f"{df['views'].mean():.2f}"
    )


    # --------------------------------------------------------
    # MOST VOTED QUESTIONS
    # --------------------------------------------------------

    print("\nTop 5 Most Voted Questions:")

    top_votes = df.sort_values(
        by="votes",
        ascending=False
    ).head(5)

    for index, row in top_votes.iterrows():

        print(
            f"{row['votes']} votes | "
            f"{row['title']}"
        )


    # --------------------------------------------------------
    # MOST ANSWERED QUESTIONS
    # --------------------------------------------------------

    print("\nTop 5 Most Answered Questions:")

    top_answers = df.sort_values(
        by="answers",
        ascending=False
    ).head(5)

    for index, row in top_answers.iterrows():

        print(
            f"{row['answers']} answers | "
            f"{row['title']}"
        )


    # --------------------------------------------------------
    # TAG ANALYSIS
    # --------------------------------------------------------

    print("\nMost Common Tags:")

    tag_counter = {}

    for tag_string in df["tags"]:

        tags = tag_string.split(", ")

        for tag in tags:

            if not tag:
                continue

            tag_counter[tag] = (
                tag_counter.get(tag, 0) + 1
            )

    sorted_tags = sorted(
        tag_counter.items(),
        key=lambda item: item[1],
        reverse=True
    )

    for tag, count in sorted_tags[:10]:

        print(
            f"{tag}: {count} questions"
        )


# ============================================================
# CREATE REPORT
# ============================================================

def create_report(df):

    report_lines = []

    report_lines.append(
        "STACK OVERFLOW PYTHON SCRAPING REPORT"
    )

    report_lines.append("=" * 50)

    report_lines.append(
        f"Generated: {datetime.now()}"
    )

    report_lines.append(
        f"Questions scraped: {len(df)}"
    )

    report_lines.append(
        f"Average votes: {df['votes'].mean():.2f}"
    )

    report_lines.append(
        f"Average answers: {df['answers'].mean():.2f}"
    )

    report_lines.append(
        f"Average views: {df['views'].mean():.2f}"
    )

    report_lines.append("\nTop Questions:")

    top_questions = df.sort_values(
        by="votes",
        ascending=False
    ).head(10)

    for _, row in top_questions.iterrows():

        report_lines.append(
            f"\n{row['votes']} votes"
        )

        report_lines.append(
            row["title"]
        )

        report_lines.append(
            row["url"]
        )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "\n".join(report_lines)
        )

    print(
        f"\nReport saved to {REPORT_FILE}"
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 60)
    print("STACK OVERFLOW PYTHON SCRAPER")
    print("=" * 60)

    questions = scrape_stackoverflow()

    if not questions:

        print(
            "\nNo questions were scraped."
        )

        return


    # --------------------------------------------------------
    # CREATE DATAFRAME
    # --------------------------------------------------------

    df = pd.DataFrame(questions)


    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    df.drop_duplicates(
        subset=["url"],
        inplace=True
    )


    # --------------------------------------------------------
    # SAVE CSV
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8"
    )

    print(
        f"\nData saved to {OUTPUT_FILE}"
    )


    # --------------------------------------------------------
    # ANALYZE
    # --------------------------------------------------------

    analyze_data(df)


    # --------------------------------------------------------
    # CREATE REPORT
    # --------------------------------------------------------

    create_report(df)


    print("\nScraping completed successfully!")


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()

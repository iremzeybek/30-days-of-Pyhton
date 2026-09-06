import re
from collections import Counter


# ============================================================
# PYTHON REGULAR EXPRESSIONS
# TEXT & DATA ANALYZER
# ============================================================

APP_NAME = "Regex Text & Data Analyzer"
VERSION = "1.0"


# ============================================================
# SAMPLE TEXT
# ============================================================

SAMPLE_TEXT = """
Hello! My name is Irem Zeybek.

You can contact me at:
irem.zeybek@example.com
python.student@example.org

My phone numbers are:
+90 555 123 4567
+90 532 987 6543
0212-555-1234

Visit my websites:
https://www.example.com
https://github.com/example
http://www.python.org

Important dates:
05/09/2026
15-10-2026
2026-12-31

I am learning Python, Regular Expressions, APIs, Web Scraping,
Data Science, and Automation.

#Python #Programming #Regex #ComputerEngineering

My username is @irem_dev.

This is an example of sensitive information:
Credit Card: 1234-5678-9012-3456
"""


# ============================================================
# REGEX PATTERNS
# ============================================================

EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

PHONE_PATTERN = (
    r"(?:\+90\s?)?"
    r"(?:\(?0?\d{3}\)?[\s.-]?)"
    r"\d{3}[\s.-]?\d{2,4}"
)

URL_PATTERN = r"https?://(?:www\.)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[^\s]*)?"

DATE_PATTERN = (
    r"\b(?:"
    r"\d{2}[/-]\d{2}[/-]\d{4}"
    r"|"
    r"\d{4}-\d{2}-\d{2}"
    r")\b"
)

HASHTAG_PATTERN = r"#[A-Za-z0-9_]+"

USERNAME_PATTERN = r"@[A-Za-z0-9_]+"

CREDIT_CARD_PATTERN = r"\b\d{4}[- ]\d{4}[- ]\d{4}[- ]\d{4}\b"

WORD_PATTERN = r"\b[A-Za-z]+\b"

NUMBER_PATTERN = r"\b\d+(?:\.\d+)?\b"


# ============================================================
# DISPLAY FUNCTIONS
# ============================================================

def print_header(title):
    """Display a formatted section header."""

    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def display_results(title, results):
    """Display a list of regex results."""

    print_header(title)

    if not results:
        print("No matches found.")
        return

    for index, result in enumerate(results, start=1):
        print(f"{index:>3}. {result}")


# ============================================================
# BASIC REGEX DEMONSTRATIONS
# ============================================================

def demonstrate_search(text):
    """Demonstrate re.search()."""

    print_header("re.search()")

    pattern = r"Python"

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        print("Found:", match.group())
        print("Start position:", match.start())
        print("End position:", match.end())
    else:
        print("Pattern was not found.")


def demonstrate_match(text):
    """Demonstrate re.match()."""

    print_header("re.match()")

    pattern = r"Hello"

    match = re.match(pattern, text.strip())

    if match:
        print("The text starts with:", match.group())
    else:
        print("The text does not start with 'Hello'.")


def demonstrate_findall(text):
    """Demonstrate re.findall()."""

    print_header("re.findall()")

    pattern = r"\bPython\b"

    matches = re.findall(pattern, text, re.IGNORECASE)

    print("Number of matches:", len(matches))

    for match in matches:
        print("-", match)


def demonstrate_finditer(text):
    """Demonstrate re.finditer()."""

    print_header("re.finditer()")

    pattern = EMAIL_PATTERN

    matches = re.finditer(pattern, text)

    for match in matches:
        print("Email:", match.group())
        print("Position:", match.start(), "-", match.end())
        print()


# ============================================================
# EMAIL EXTRACTION
# ============================================================

def extract_emails(text):
    """Extract email addresses."""

    emails = re.findall(EMAIL_PATTERN, text)

    display_results("EMAIL ADDRESSES", emails)

    return emails


# ============================================================
# PHONE EXTRACTION
# ============================================================

def extract_phones(text):
    """Extract phone numbers."""

    phones = re.findall(PHONE_PATTERN, text)

    display_results("PHONE NUMBERS", phones)

    return phones


# ============================================================
# URL EXTRACTION
# ============================================================

def extract_urls(text):
    """Extract URLs."""

    urls = re.findall(URL_PATTERN, text)

    display_results("URLS", urls)

    return urls


# ============================================================
# DATE EXTRACTION
# ============================================================

def extract_dates(text):
    """Extract dates."""

    dates = re.findall(DATE_PATTERN, text)

    display_results("DATES", dates)

    return dates


# ============================================================
# HASHTAG EXTRACTION
# ============================================================

def extract_hashtags(text):
    """Extract hashtags."""

    hashtags = re.findall(HASHTAG_PATTERN, text)

    display_results("HASHTAGS", hashtags)

    return hashtags


# ============================================================
# USERNAME EXTRACTION
# ============================================================

def extract_usernames(text):
    """Extract @ usernames."""

    usernames = re.findall(USERNAME_PATTERN, text)

    display_results("USERNAMES", usernames)

    return usernames


# ============================================================
# CREDIT CARD MASKING
# ============================================================

def mask_credit_cards(text):
    """Mask credit card numbers."""

    masked_text = re.sub(
        CREDIT_CARD_PATTERN,
        "****-****-****-****",
        text
    )

    print_header("CREDIT CARD MASKING")
    print(masked_text)

    return masked_text


# ============================================================
# EMAIL MASKING
# ============================================================

def mask_emails(text):
    """Mask email addresses."""

    def mask_email(match):
        email = match.group()

        username, domain = email.split("@", 1)

        if len(username) <= 2:
            masked_username = "*" * len(username)
        else:
            masked_username = (
                username[0]
                + "*" * (len(username) - 2)
                + username[-1]
            )

        return masked_username + "@" + domain

    masked_text = re.sub(
        EMAIL_PATTERN,
        mask_email,
        text
    )

    print_header("EMAIL MASKING")
    print(masked_text)

    return masked_text


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    """Clean text using regular expressions."""

    cleaned = text

    # Remove URLs
    cleaned = re.sub(URL_PATTERN, "", cleaned)

    # Remove hashtags
    cleaned = re.sub(HASHTAG_PATTERN, "", cleaned)

    # Remove usernames
    cleaned = re.sub(USERNAME_PATTERN, "", cleaned)

    # Replace multiple spaces
    cleaned = re.sub(r"\s+", " ", cleaned)

    cleaned = cleaned.strip()

    print_header("CLEANED TEXT")
    print(cleaned)

    return cleaned


# ============================================================
# WORD FREQUENCY ANALYZER
# ============================================================

def word_frequency(text):
    """Count word frequencies using regex."""

    words = re.findall(WORD_PATTERN, text.lower())

    counter = Counter(words)

    print_header("WORD FREQUENCY")

    for word, count in counter.most_common(15):
        print(f"{word:<20} {count}")


# ============================================================
# NUMBER EXTRACTION
# ============================================================

def extract_numbers(text):
    """Extract integer and decimal numbers."""

    numbers = re.findall(NUMBER_PATTERN, text)

    display_results("NUMBERS", numbers)

    return numbers


# ============================================================
# PASSWORD VALIDATOR
# ============================================================

def validate_password(password):
    """
    Validate password strength.

    Requirements:
    - At least 8 characters
    - One uppercase letter
    - One lowercase letter
    - One number
    - One special character
    """

    print_header("PASSWORD VALIDATOR")

    checks = {
        "At least 8 characters":
            len(password) >= 8,

        "Contains uppercase letter":
            bool(re.search(r"[A-Z]", password)),

        "Contains lowercase letter":
            bool(re.search(r"[a-z]", password)),

        "Contains a number":
            bool(re.search(r"\d", password)),

        "Contains special character":
            bool(re.search(r"[^A-Za-z0-9]", password)),
    }

    for requirement, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {requirement}")

    if all(checks.values()):
        print("\nPassword strength: STRONG")
        return True

    print("\nPassword strength: WEAK")
    return False


# ============================================================
# EMAIL VALIDATOR
# ============================================================

def validate_email(email):
    """Check whether an email has a valid basic format."""

    print_header("EMAIL VALIDATOR")

    if re.fullmatch(EMAIL_PATTERN, email):
        print("Valid email address.")
        return True

    print("Invalid email address.")
    return False


# ============================================================
# PHONE VALIDATOR
# ============================================================

def validate_phone(phone):
    """Check whether a phone number has a supported format."""

    print_header("PHONE VALIDATOR")

    if re.fullmatch(PHONE_PATTERN, phone):
        print("Valid phone number.")
        return True

    print("Invalid phone number.")
    return False


# ============================================================
# GROUPS DEMONSTRATION
# ============================================================

def demonstrate_groups(text):
    """Demonstrate capturing groups."""

    print_header("CAPTURING GROUPS")

    pattern = (
        r"(?P<username>[A-Za-z0-9._%+-]+)"
        r"@"
        r"(?P<domain>[A-Za-z0-9.-]+)"
        r"\."
        r"(?P<extension>[A-Za-z]{2,})"
    )

    match = re.search(pattern, text)

    if not match:
        print("No email found.")
        return

    print("Complete email:", match.group())
    print("Username:", match.group("username"))
    print("Domain:", match.group("domain"))
    print("Extension:", match.group("extension"))


# ============================================================
# SPLIT DEMONSTRATION
# ============================================================

def demonstrate_split():
    """Demonstrate re.split()."""

    print_header("re.split()")

    text = "Python,Java;C++;JavaScript|Go"

    parts = re.split(r"[,;|]", text)

    print("Original:")
    print(text)

    print("\nSeparated values:")

    for part in parts:
        print("-", part)


# ============================================================
# SUBSTITUTION DEMONSTRATION
# ============================================================

def demonstrate_substitution():
    """Demonstrate re.sub()."""

    print_header("re.sub()")

    text = "Python     is     very     powerful."

    print("Original:")
    print(text)

    cleaned = re.sub(r"\s+", " ", text)

    print("\nAfter substitution:")
    print(cleaned)


# ============================================================
# CHARACTER CLASS DEMONSTRATION
# ============================================================

def demonstrate_character_classes():
    """Demonstrate common regex character classes."""

    print_header("CHARACTER CLASSES")

    text = "Python 3.12 costs $0 and is awesome!"

    patterns = {
        r"\d": "Digits",
        r"\w": "Word characters",
        r"\s": "Whitespace",
        r"[A-Z]": "Uppercase letters",
        r"[a-z]": "Lowercase letters",
    }

    for pattern, description in patterns.items():
        matches = re.findall(pattern, text)

        print(f"\n{description}:")
        print(matches)


# ============================================================
# QUANTIFIER DEMONSTRATION
# ============================================================

def demonstrate_quantifiers():
    """Demonstrate regex quantifiers."""

    print_header("REGEX QUANTIFIERS")

    text = "aa aaa aaaa aaaaa"

    patterns = {
        r"a+": "One or more",
        r"a*": "Zero or more",
        r"a{3}": "Exactly three",
        r"a{2,4}": "Between two and four",
    }

    for pattern, description in patterns.items():
        matches = re.findall(pattern, text)

        print(f"\n{description} ({pattern}):")
        print(matches)


# ============================================================
# ANALYZE TEXT
# ============================================================

def analyze_text(text):
    """Run the complete text analysis."""

    print_header("COMPLETE TEXT ANALYSIS")

    print("Characters:", len(text))

    words = re.findall(WORD_PATTERN, text)

    print("Words:", len(words))

    numbers = re.findall(NUMBER_PATTERN, text)

    print("Numbers:", len(numbers))

    emails = re.findall(EMAIL_PATTERN, text)

    print("Emails:", len(emails))

    urls = re.findall(URL_PATTERN, text)

    print("URLs:", len(urls))

    hashtags = re.findall(HASHTAG_PATTERN, text)

    print("Hashtags:", len(hashtags))

    usernames = re.findall(USERNAME_PATTERN, text)

    print("Usernames:", len(usernames))

    dates = re.findall(DATE_PATTERN, text)

    print("Dates:", len(dates))


# ============================================================
# CUSTOM SEARCH
# ============================================================

def custom_search(text):
    """Allow the user to enter a custom regex."""

    print_header("CUSTOM REGEX SEARCH")

    pattern = input("Enter a regex pattern: ")

    try:
        matches = re.findall(pattern, text)

        if matches:
            print("\nMatches found:")

            for match in matches:
                print("-", match)
        else:
            print("No matches found.")

    except re.error as error:
        print("Invalid regular expression.")
        print("Error:", error)


# ============================================================
# INTERACTIVE MENU
# ============================================================

def show_menu():
    """Display the application menu."""

    print("\n")
    print("=" * 60)
    print(f"{APP_NAME} v{VERSION}")
    print("=" * 60)

    print("1.  Analyze text")
    print("2.  Extract emails")
    print("3.  Extract phone numbers")
    print("4.  Extract URLs")
    print("5.  Extract dates")
    print("6.  Extract hashtags")
    print("7.  Extract usernames")
    print("8.  Extract numbers")
    print("9.  Mask credit cards")
    print("10. Mask emails")
    print("11. Clean text")
    print("12. Word frequency")
    print("13. Validate email")
    print("14. Validate phone")
    print("15. Validate password")
    print("16. Capturing groups")
    print("17. re.search() demonstration")
    print("18. re.match() demonstration")
    print("19. re.findall() demonstration")
    print("20. re.finditer() demonstration")
    print("21. re.split() demonstration")
    print("22. re.sub() demonstration")
    print("23. Character classes")
    print("24. Quantifiers")
    print("25. Custom regex search")
    print("0.  Exit")


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():
    """Run the Regex Analyzer application."""

    text = SAMPLE_TEXT

    print_header(APP_NAME)

    print("Welcome to the Python Regular Expressions project!")
    print("The application is ready with sample data.")

    while True:

        show_menu()

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            analyze_text(text)

        elif choice == "2":
            extract_emails(text)

        elif choice == "3":
            extract_phones(text)

        elif choice == "4":
            extract_urls(text)

        elif choice == "5":
            extract_dates(text)

        elif choice == "6":
            extract_hashtags(text)

        elif choice == "7":
            extract_usernames(text)

        elif choice == "8":
            extract_numbers(text)

        elif choice == "9":
            mask_credit_cards(text)

        elif choice == "10":
            mask_emails(text)

        elif choice == "11":
            clean_text(text)

        elif choice == "12":
            word_frequency(text)

        elif choice == "13":
            email = input("Enter an email address: ").strip()
            validate_email(email)

        elif choice == "14":
            phone = input("Enter a phone number: ").strip()
            validate_phone(phone)

        elif choice == "15":
            password = input("Enter a password: ")
            validate_password(password)

        elif choice == "16":
            demonstrate_groups(text)

        elif choice == "17":
            demonstrate_search(text)

        elif choice == "18":
            demonstrate_match(text)

        elif choice == "19":
            demonstrate_findall(text)

        elif choice == "20":
            demonstrate_finditer(text)

        elif choice == "21":
            demonstrate_split()

        elif choice == "22":
            demonstrate_substitution()

        elif choice == "23":
            demonstrate_character_classes()

        elif choice == "24":
            demonstrate_quantifiers()

        elif choice == "25":
            custom_search(text)

        elif choice == "0":
            print("\nThank you for using Regex Text & Data Analyzer!")
            print("Goodbye!")
            break

        else:
            print("\nInvalid choice. Please select an option from 0-25.")


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()

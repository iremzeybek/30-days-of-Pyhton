import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------
# STEP 1: Website address
# ---------------------------------------------------
url = "https://www.boxofficemojo.com/weekend/"

# ---------------------------------------------------
# STEP 2: Pretend to be a real browser
# ---------------------------------------------------
headers = {
    "User-Agent": "Mozilla/5.0"
}

# ---------------------------------------------------
# STEP 3: Download the page
# ---------------------------------------------------
response = requests.get(url, headers=headers)

print("Request status:", response.status_code)

# Stop if the request failed
if response.status_code != 200:
    print("Failed to download the webpage.")
    exit()

# ---------------------------------------------------
# STEP 4: Parse the HTML
# ---------------------------------------------------
soup = BeautifulSoup(response.text, "html.parser")

# ---------------------------------------------------
# STEP 5: Find the main table
# ---------------------------------------------------
table = soup.find("table")

if table is None:
    print("Could not find the box office table.")
    exit()

# ---------------------------------------------------
# STEP 6: Get all rows except the header
# ---------------------------------------------------
rows = table.find_all("tr")[1:]

# List to store results
movies_data = []

print("\nWORLDWIDE WEEKEND BOX OFFICE\n")

# ---------------------------------------------------
# STEP 7: Loop through rows
# ---------------------------------------------------
for row in rows[:10]:  # top 10 movies
    columns = row.find_all("td")

    # Make sure the row has enough columns
    if len(columns) < 8:
        continue

    # Extract rank
    rank = columns[0].get_text(strip=True)

    # Extract movie title
    title = columns[1].get_text(strip=True)

    # Extract weekend gross
    gross_text = columns[7].get_text(strip=True)

    # Clean the money text
    cleaned = gross_text.replace("$", "").replace(",", "")

    # Convert to integer if possible
    try:
        gross_number = int(cleaned)
    except:
        gross_number = 0

    # Save data
    movies_data.append({
        "rank": rank,
        "title": title,
        "gross": gross_number
    })

    # Print nicely
    print(f"{rank}. {title:35} $ {gross_number:,}")

# ---------------------------------------------------
# STEP 8: Save to a text file
# ---------------------------------------------------
with open("box_office_results.txt", "w", encoding="utf-8") as file:
    file.write("WORLDWIDE WEEKEND BOX OFFICE\n\n")

    for movie in movies_data:
        line = f"{movie['rank']}. {movie['title']} - $ {movie['gross']:,}\n"
        file.write(line)

print("\nData saved to box_office_results.txt")
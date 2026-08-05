import requests
from datetime import datetime

# ---------------------------------------------------
# Configuration
# ---------------------------------------------------
BASE_URL = "https://api.github.com/users"
OUTPUT_FILE = "github_report.txt"


# ---------------------------------------------------
# Helper: safe GET request
# ---------------------------------------------------
def get_json(url):
    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            return response.json()

        elif response.status_code == 404:
            print("\nUser not found.")
            return None

        elif response.status_code == 403:
            print("\nGitHub API rate limit reached. Try again later.")
            return None

        else:
            print(f"\nRequest failed with status code: {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print("\nRequest timed out.")
        return None

    except requests.exceptions.ConnectionError:
        print("\nNetwork connection error.")
        return None

    except requests.exceptions.RequestException as e:
        print(f"\nUnexpected error: {e}")
        return None


# ---------------------------------------------------
# Fetch profile information
# ---------------------------------------------------
def fetch_profile(username):
    url = f"{BASE_URL}/{username}"
    return get_json(url)


# ---------------------------------------------------
# Fetch repositories
# ---------------------------------------------------
def fetch_repositories(username):
    url = f"{BASE_URL}/{username}/repos?per_page=100"
    return get_json(url)


# ---------------------------------------------------
# Display profile
# ---------------------------------------------------
def display_profile(profile):
    print("\n===== GITHUB PROFILE =====")
    print(f"Name         : {profile.get('name')}")
    print(f"Username     : {profile.get('login')}")
    print(f"Bio          : {profile.get('bio')}")
    print(f"Followers    : {profile.get('followers')}")
    print(f"Following    : {profile.get('following')}")
    print(f"Public Repos : {profile.get('public_repos')}")
    print(f"Location     : {profile.get('location')}")
    print(f"Profile URL  : {profile.get('html_url')}")


# ---------------------------------------------------
# Display repositories
# ---------------------------------------------------
def display_repositories(repos):
    if not repos:
        print("\nNo repositories found.")
        return

    # Sort by stars (descending)
    repos_sorted = sorted(
        repos,
        key=lambda repo: repo["stargazers_count"],
        reverse=True
    )

    print("\n===== TOP REPOSITORIES =====")

    for index, repo in enumerate(repos_sorted[:10], start=1):
        print(f"\n{index}. {repo['name']}")
        print(f"   Stars   : {repo['stargazers_count']}")
        print(f"   Forks   : {repo['forks_count']}")
        print(f"   Language: {repo['language']}")
        print(f"   URL     : {repo['html_url']}")


# ---------------------------------------------------
# Save report to file
# ---------------------------------------------------
def save_report(profile, repos):
    repos_sorted = sorted(
        repos,
        key=lambda repo: repo["stargazers_count"],
        reverse=True
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write("GITHUB USER REPORT\n")
        file.write("=" * 50 + "\n")
        file.write(f"Generated: {datetime.now()}\n\n")

        file.write(f"Name         : {profile.get('name')}\n")
        file.write(f"Username     : {profile.get('login')}\n")
        file.write(f"Bio          : {profile.get('bio')}\n")
        file.write(f"Followers    : {profile.get('followers')}\n")
        file.write(f"Following    : {profile.get('following')}\n")
        file.write(f"Public Repos : {profile.get('public_repos')}\n")
        file.write(f"Location     : {profile.get('location')}\n")
        file.write(f"Profile URL  : {profile.get('html_url')}\n\n")

        file.write("TOP REPOSITORIES\n")
        file.write("-" * 50 + "\n")

        for index, repo in enumerate(repos_sorted[:10], start=1):
            file.write(f"{index}. {repo['name']}\n")
            file.write(f"   Stars   : {repo['stargazers_count']}\n")
            file.write(f"   Forks   : {repo['forks_count']}\n")
            file.write(f"   Language: {repo['language']}\n")
            file.write(f"   URL     : {repo['html_url']}\n\n")

    print(f"\nReport saved to '{OUTPUT_FILE}'")


# ---------------------------------------------------
# Main program
# ---------------------------------------------------
def main():
    print("GitHub REST API Practice Project")
    print("=" * 40)

    username = input("Enter a GitHub username: ").strip()

    if not username:
        print("Username cannot be empty.")
        return

    # Fetch profile
    profile = fetch_profile(username)

    if profile is None:
        return

    # Fetch repositories
    repos = fetch_repositories(username)

    if repos is None:
        return

    # Display results
    display_profile(profile)
    display_repositories(repos)

    # Save report
    save_report(profile, repos)


# ---------------------------------------------------
# Start program
# ---------------------------------------------------
if __name__ == "__main__":
    main()
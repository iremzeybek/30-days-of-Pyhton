from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import time
from datetime import datetime


# ==========================================
# CONFIGURATION
# ==========================================

LOGIN_URL = "https://the-internet.herokuapp.com/login"
USERNAME = "tomsmith"
PASSWORD = "SuperSecretPassword!"

CSV_FILE = "dashboard_data.csv"


# ==========================================
# BROWSER SETUP
# ==========================================

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )


# ==========================================
# LOGIN FUNCTION
# ==========================================

def login(driver, wait):
    print("Opening login page...")
    driver.get(LOGIN_URL)

    wait.until(
        EC.presence_of_element_located((By.ID, "username"))
    ).send_keys(USERNAME)

    wait.until(
        EC.presence_of_element_located((By.ID, "password"))
    ).send_keys(PASSWORD)

    wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    ).click()

    flash = wait.until(
        EC.presence_of_element_located((By.ID, "flash"))
    )

    if "You logged into a secure area!" in flash.text:
        print("Login successful!")
        return True

    print("Login failed!")
    return False


# ==========================================
# SCRAPE DASHBOARD DATA
# ==========================================

def scrape_dashboard(driver, wait):
    print("Scraping dashboard...")

    heading = wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "h2"))
    ).text

    message = wait.until(
        EC.presence_of_element_located((By.ID, "flash"))
    ).text.strip()

    current_url = driver.current_url
    page_title = driver.title

    logout_text = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "a.button.secondary.radius")
        )
    ).text

    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "page_title": page_title,
        "heading": heading,
        "message": message,
        "current_url": current_url,
        "logout_button": logout_text
    }

    return data


# ==========================================
# SAVE DATA TO CSV
# ==========================================

def save_to_csv(data):
    df = pd.DataFrame([data])

    try:
        old_df = pd.read_csv(CSV_FILE)
        df = pd.concat([old_df, df], ignore_index=True)
    except FileNotFoundError:
        pass

    df.to_csv(CSV_FILE, index=False)
    print(f"Data saved to {CSV_FILE}")


# ==========================================
# TAKE SCREENSHOT
# ==========================================

def take_screenshot(driver, filename):
    driver.save_screenshot(filename)
    print(f"Screenshot saved: {filename}")


# ==========================================
# SIMPLE SEARCH AUTOMATION
# ==========================================

def perform_demo_search(driver):
    print("Opening example search page...")

    driver.get("https://www.wikipedia.org/")

    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "searchInput"))
    )

    search_box.send_keys("Selenium software")
    search_box.send_keys(Keys.ENTER)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "firstHeading"))
    )

    print("Search completed.")


# ==========================================
# LOGOUT FUNCTION
# ==========================================

def logout(driver, wait):
    print("Returning to dashboard for logout...")

    driver.get("https://the-internet.herokuapp.com/secure")

    logout_btn = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a.button.secondary.radius")
        )
    )

    logout_btn.click()

    wait.until(
        EC.presence_of_element_located((By.ID, "username"))
    )

    print("Logged out successfully.")


# ==========================================
# MAIN PROGRAM
# ==========================================

def main():
    driver = create_driver()
    wait = WebDriverWait(driver, 15)

    try:
        success = login(driver, wait)

        if not success:
            return

        take_screenshot(driver, "dashboard.png")

        data = scrape_dashboard(driver, wait)

        print("\nCollected Data:")
        for key, value in data.items():
            print(f"{key}: {value}")

        save_to_csv(data)

        time.sleep(2)

        perform_demo_search(driver)

        take_screenshot(driver, "search_result.png")

        time.sleep(2)

        logout(driver, wait)

    except Exception as e:
        print("\nERROR OCCURRED")
        print(type(e).__name__)
        print(e)

    finally:
        print("\nClosing browser...")
        time.sleep(2)
        driver.quit()


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()

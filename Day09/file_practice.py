import os
import requests


# -----------------------------
# CREATE AND WRITE TO FILE
# -----------------------------
def create_file():
    filename = input("Enter a file name (example: notes.txt): ")
    text = input("Enter text to save: ")

    with open(filename, "w", encoding="utf-8") as file:
        file.write(text + "\n")

    print(f"File '{filename}' created successfully.\n")


# -----------------------------
# READ FILE
# -----------------------------
def read_file():
    filename = input("Enter file name to read: ")

    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            content = file.read()

        print("\n--- File Content ---")
        print(content)
        print("--------------------\n")
    else:
        print("File not found.\n")


# -----------------------------
# APPEND TEXT TO FILE
# -----------------------------
def append_file():
    filename = input("Enter file name to append text to: ")

    if os.path.exists(filename):
        text = input("Enter text to add: ")

        with open(filename, "a", encoding="utf-8") as file:
            file.write(text + "\n")

        print("Text added successfully.\n")
    else:
        print("File not found.\n")


# -----------------------------
# DOWNLOAD FILE
# -----------------------------
def download_file():
    url = input("Enter file URL: ")
    filename = input("Save as (example: image.png): ")

    try:
        response = requests.get(url)

        if response.status_code == 200:
            with open(filename, "wb") as file:
                file.write(response.content)

            size = os.path.getsize(filename)

            print(f"File downloaded successfully as '{filename}'.")
            print(f"File size: {size} bytes\n")
        else:
            print(f"Download failed. Status code: {response.status_code}\n")

    except Exception as error:
        print("An error occurred:", error)
        print()


# -----------------------------
# MENU
# -----------------------------
def main():
    while True:
        print("===== FILE PRACTICE MENU =====")
        print("1. Create a file")
        print("2. Read a file")
        print("3. Append text to a file")
        print("4. Download a file")
        print("5. Exit")

        choice = input("Choose an option (1-5): ")

        if choice == "1":
            create_file()
        elif choice == "2":
            read_file()
        elif choice == "3":
            append_file()
        elif choice == "4":
            download_file()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.\n")


# -----------------------------
# START PROGRAM
# -----------------------------
if __name__ == "__main__":
    main()
class Book:
    def __init__(self, title, author, total_copies):
        self.title = title
        self.author = author
        self.total_copies = total_copies
        self.available_copies = total_copies

    def borrow_book(self):
        if self.available_copies > 0:
            self.available_copies -= 1
            print(f"You borrowed '{self.title}'.")
        else:
            print(f"Sorry, '{self.title}' is not available right now.")

    def return_book(self):
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            print(f"You returned '{self.title}'.")
        else:
            print("All copies are already in the library.")

    def show_info(self):
        print(f"Title : {self.title}")
        print(f"Author: {self.author}")
        print(f"Available: {self.available_copies}/{self.total_copies}")
        print("-" * 30)


# Create book objects
book1 = Book("Python Basics", "John Smith", 3)
book2 = Book("Clean Code", "Robert Martin", 2)
book3 = Book("The Pragmatic Programmer", "Andrew Hunt", 1)

library = [book1, book2, book3]


def show_books():
    print("\nBooks in Library")
    print("=" * 30)
    for index, book in enumerate(library, start=1):
        print(f"{index}. {book.title} ({book.available_copies}/{book.total_copies})")
    print()


# Main program loop
while True:
    print("\nLibrary Menu")
    print("1 - Show all books")
    print("2 - Borrow a book")
    print("3 - Return a book")
    print("4 - Show detailed information")
    print("5 - Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        show_books()

    elif choice == "2":
        show_books()
        number = int(input("Enter book number to borrow: "))
        if 1 <= number <= len(library):
            library[number - 1].borrow_book()
        else:
            print("Invalid book number.")

    elif choice == "3":
        show_books()
        number = int(input("Enter book number to return: "))
        if 1 <= number <= len(library):
            library[number - 1].return_book()
        else:
            print("Invalid book number.")

    elif choice == "4":
        show_books()
        number = int(input("Enter book number for details: "))
        if 1 <= number <= len(library):
            library[number - 1].show_info()
        else:
            print("Invalid book number.")

    elif choice == "5":
        print("Goodbye!")
        break

    else:
        print("Please enter a valid option.")
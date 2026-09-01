import json
import os
from datetime import datetime

from dotenv import load_dotenv
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


# ============================================================
# Configuration
# ============================================================

load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER")

HISTORY_FILE = "sms_history.json"


# ============================================================
# Validation
# ============================================================

def validate_configuration():
    """Check whether all required environment variables exist."""

    missing = []

    if not ACCOUNT_SID:
        missing.append("TWILIO_ACCOUNT_SID")

    if not AUTH_TOKEN:
        missing.append("TWILIO_AUTH_TOKEN")

    if not TWILIO_PHONE:
        missing.append("TWILIO_PHONE_NUMBER")

    if missing:
        print("\nMissing configuration:")
        for item in missing:
            print(f"  - {item}")

        print("\nPlease check your .env file.")
        return False

    return True


def validate_phone_number(phone):
    """Basic phone number validation."""

    phone = phone.strip()

    if not phone.startswith("+"):
        print("Phone number must start with '+' and include the country code.")
        return False

    if not phone[1:].isdigit():
        print("Phone number can only contain digits after '+'.")
        return False

    if len(phone) < 10:
        print("Phone number appears to be too short.")
        return False

    return True


def validate_message(message):
    """Validate SMS message content."""

    message = message.strip()

    if not message:
        print("Message cannot be empty.")
        return False

    if len(message) > 1600:
        print("Message is too long for this practice application.")
        return False

    return True


# ============================================================
# History Management
# ============================================================

def load_history():
    """Load SMS history from JSON."""

    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        print("Warning: Could not read SMS history.")
        return []


def save_history(history):
    """Save SMS history to JSON."""

    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=4)

    except OSError as error:
        print(f"Could not save history: {error}")


def add_to_history(history, message_data):
    """Add a new SMS record to history."""

    history.append(message_data)
    save_history(history)


# ============================================================
# Twilio Client
# ============================================================

def create_client():
    """Create and return a Twilio client."""

    return Client(ACCOUNT_SID, AUTH_TOKEN)


# ============================================================
# SMS Functions
# ============================================================

def send_sms(client, history, recipient, message):
    """Send an SMS message using Twilio."""

    if not validate_phone_number(recipient):
        return

    if not validate_message(message):
        return

    print("\nSending SMS...")

    try:
        sms = client.messages.create(
            body=message,
            from_=TWILIO_PHONE,
            to=recipient
        )

        record = {
            "sid": sms.sid,
            "recipient": recipient,
            "message": message,
            "status": sms.status,
            "date": datetime.now().isoformat(timespec="seconds")
        }

        add_to_history(history, record)

        print("\nSMS sent successfully!")
        print(f"Message SID: {sms.sid}")
        print(f"Status: {sms.status}")

    except TwilioRestException as error:
        print("\nTwilio error occurred.")
        print(f"Error code: {error.code}")
        print(f"Message: {error.msg}")

    except Exception as error:
        print(f"\nUnexpected error: {error}")


def send_bulk_sms(client, history):
    """Send the same SMS to multiple recipients."""

    print("\n=== Bulk SMS ===")

    raw_numbers = input(
        "Enter phone numbers separated by commas:\n> "
    )

    recipients = [
        number.strip()
        for number in raw_numbers.split(",")
        if number.strip()
    ]

    message = input("Enter your message:\n> ")

    if not validate_message(message):
        return

    successful = 0

    for recipient in recipients:

        if not validate_phone_number(recipient):
            print(f"Skipping invalid number: {recipient}")
            continue

        try:
            sms = client.messages.create(
                body=message,
                from_=TWILIO_PHONE,
                to=recipient
            )

            record = {
                "sid": sms.sid,
                "recipient": recipient,
                "message": message,
                "status": sms.status,
                "date": datetime.now().isoformat(timespec="seconds")
            }

            add_to_history(history, record)

            successful += 1

            print(f"✓ Sent to {recipient}")

        except TwilioRestException as error:
            print(f"✗ Failed to send to {recipient}")
            print(f"  Error: {error.msg}")

    print(
        f"\nBulk operation complete: "
        f"{successful}/{len(recipients)} messages sent."
    )


# ============================================================
# Message Status
# ============================================================

def check_message_status(client):
    """Check the current status of an SMS."""

    sid = input("\nEnter Message SID:\n> ").strip()

    if not sid:
        print("Message SID cannot be empty.")
        return

    try:
        message = client.messages(sid).fetch()

        print("\n=== Message Status ===")
        print(f"SID:       {message.sid}")
        print(f"To:        {message.to}")
        print(f"From:      {message.from_}")
        print(f"Status:    {message.status}")
        print(f"Direction: {message.direction}")

    except TwilioRestException as error:
        print("\nCould not retrieve message.")
        print(f"Error: {error.msg}")


# ============================================================
# History
# ============================================================

def show_history(history):
    """Display previously sent messages."""

    print("\n=== SMS History ===")

    if not history:
        print("No messages have been sent yet.")
        return

    for index, record in enumerate(history, start=1):

        print(f"\n[{index}]")
        print(f"Date:      {record['date']}")
        print(f"Recipient: {record['recipient']}")
        print(f"Message:   {record['message']}")
        print(f"Status:    {record['status']}")
        print(f"SID:       {record['sid']}")


def show_statistics(history):
    """Display basic SMS statistics."""

    print("\n=== SMS Statistics ===")

    if not history:
        print("No SMS data available.")
        return

    total = len(history)

    statuses = {}

    for record in history:
        status = record.get("status", "unknown")
        statuses[status] = statuses.get(status, 0) + 1

    print(f"Total messages: {total}")

    for status, count in statuses.items():
        print(f"{status.capitalize()}: {count}")


# ============================================================
# Menu
# ============================================================

def display_menu():
    """Display the application menu."""

    print("\n" + "=" * 50)
    print("          TWILIO SMS MANAGER")
    print("=" * 50)

    print("1. Send SMS")
    print("2. Send Bulk SMS")
    print("3. Check Message Status")
    print("4. View SMS History")
    print("5. View Statistics")
    print("6. Exit")

    print("=" * 50)


# ============================================================
# Main Program
# ============================================================

def main():

    print("\nStarting Twilio SMS Manager...")

    if not validate_configuration():
        return

    client = create_client()
    history = load_history()

    print("Configuration loaded successfully.")

    while True:

        display_menu()

        choice = input("Choose an option: ").strip()

        if choice == "1":

            print("\n=== Send SMS ===")

            recipient = input(
                "Recipient phone number (+countrycode...):\n> "
            ).strip()

            message = input("Message:\n> ")

            send_sms(
                client,
                history,
                recipient,
                message
            )

        elif choice == "2":

            send_bulk_sms(
                client,
                history
            )

        elif choice == "3":

            check_message_status(client)

        elif choice == "4":

            show_history(history)

        elif choice == "5":

            show_statistics(history)

        elif choice == "6":

            print("\nThank you for using Twilio SMS Manager.")
            break

        else:

            print("\nInvalid option. Please choose 1-6.")


# ============================================================
# Program Entry Point
# ============================================================

if __name__ == "__main__":
    main()

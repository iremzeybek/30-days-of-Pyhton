import smtplib
import imaplib
import email
from email.message import EmailMessage
from email.header import decode_header

# =========================
# YOUR GMAIL INFORMATION
# =========================
EMAIL_ADDRESS = "irem.github@gmail.com"
APP_PASSWORD = "gpnk yljf qumi jzvj"

# =========================
# SEND EMAIL FUNCTION
# =========================
def send_email(receiver, subject, body):
    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.set_content(body)

    print("Connecting to Gmail SMTP server...")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, APP_PASSWORD)
        smtp.send_message(msg)

    print("Email sent successfully!")


# =========================
# READ INBOX FUNCTION
# =========================
def read_inbox(limit=5):
    print("Connecting to Gmail IMAP server...")

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL_ADDRESS, APP_PASSWORD)

    # Open inbox
    mail.select("inbox")

    # Search for all emails
    status, messages = mail.search(None, "ALL")

    if status != "OK":
        print("Could not read inbox.")
        return

    email_ids = messages[0].split()

    print(f"Total emails in inbox: {len(email_ids)}")

    # Read latest emails
    latest_ids = email_ids[-limit:]

    for i, email_id in enumerate(reversed(latest_ids), start=1):
        status, msg_data = mail.fetch(email_id, "(RFC822)")

        if status != "OK":
            print("Could not fetch email.")
            continue

        raw_email = msg_data[0][1]
        message = email.message_from_bytes(raw_email)

        # Decode subject
        subject, encoding = decode_header(message["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8", errors="ignore")

        # Decode sender
        from_ = message.get("From")

        print("\n" + "=" * 50)
        print(f"Email #{i}")
        print(f"From   : {from_}")
        print(f"Subject: {subject}")

        # Read plain text body if available
        body = ""

        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode(errors="ignore")
                        break
        else:
            payload = message.get_payload(decode=True)
            if payload:
                body = payload.decode(errors="ignore")

        print("Body preview:")
        print(body[:200])  # first 200 characters

    mail.logout()
    print("\nFinished reading inbox.")


# =========================
# MAIN PROGRAM
# =========================
if __name__ == "__main__":
    print("Choose an option:")
    print("1 - Send Email")
    print("2 - Read Inbox")

    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        receiver = input("Receiver email: ")
        subject = input("Subject: ")
        body = input("Message: ")

        send_email(receiver, subject, body)

    elif choice == "2":
        read_inbox(limit=5)

    else:
        print("Invalid choice.")
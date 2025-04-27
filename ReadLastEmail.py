import email
from email import policy
from bs4 import BeautifulSoup
import re

def extract_email_body(msg):
    """
    Extracts the plain text or HTML text from an email.message.EmailMessage
    """
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                body = part.get_payload()
                break
            elif content_type == "text/html" and not body:
                html = part.get_payload()
                soup = BeautifulSoup(html, "html.parser")
                body = soup.get_text()
    else:
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            body = msg.get_payload()
        elif content_type == "text/html":
            html = msg.get_payload()
            soup = BeautifulSoup(html, "html.parser")
            body = soup.get_text()

    return body.strip()


def extract_last_reply(msg):
    """
    Given a raw email string (plain or .eml), extract the last reply block.
    """
    #msg = email.message_from_string(raw_email_text, policy=policy.default)
    full_text = extract_email_body(msg)

    # Split based on reply markers
    split_patterns = [
        r"On.*wrote:",                          # "On DATE, NAME wrote:"
        r"From: .*",                            # From headers
        r"Sent: .*",                            # Sent headers
        r"-----Original Message-----",          # Outlook style
        r"^>.*",                                # Quoted lines
    ]

    pattern = re.compile("|".join(split_patterns), re.IGNORECASE | re.MULTILINE)
    parts = pattern.split(full_text)

    # Get the last segment that is non-empty
    parts = [p.strip() for p in parts if p.strip()]
    return parts[0] if parts else full_text

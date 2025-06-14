import os, json, base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
_TOKEN_URI = "https://oauth2.googleapis.com/token"

def _service(user_email: str):
    """Builds an authenticated Gmail API service for the given user."""
    creds = Credentials(
        None,
        refresh_token=os.getenv("GMAIL_REFRESH_TOKEN"),
        token_uri=_TOKEN_URI,
        client_id=os.getenv("GMAIL_CLIENT_ID"),
        client_secret=os.getenv("GMAIL_CLIENT_SECRET"),
        scopes=_SCOPES,
    )
    if not creds.refresh_token:
        raise RuntimeError("GMAIL_REFRESH_TOKEN secret missing or empty")
    return build("gmail", "v1", credentials=creds, cache_discovery=False)

def send_html_email(
    *,
    from_addr: str,
    to_addr: str,
    subject: str,
    html_body: str,
    attachment_html: str | None = None,
    attachment_name: str = "Profile.html",
):
    """Send an HTML e-mail (optional HTML attachment) via Gmail API."""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.add_alternative(html_body, subtype="html")

    if attachment_html is not None:
        msg.add_attachment(
            attachment_html.encode("utf-8"),
            maintype="text",
            subtype="html",
            filename=attachment_name,
        )

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    _service(from_addr).users().messages().send(userId="me", body={"raw": raw}).execute() 
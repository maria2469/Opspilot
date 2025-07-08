from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import base64
import datetime

def send_email(gmail_service, to_email, subject, body, start_time=None, end_time=None, meet_link=None):
    try:
        # Create multipart message
        message = MIMEMultipart("mixed")
        message["to"] = to_email
        message["from"] = "me"
        message["subject"] = subject

        # Add plain text part
        text_part = MIMEText(body, "plain")
        message.attach(text_part)

        # Optional: Add .ics calendar invite
        if start_time and end_time:
            start_str = start_time.strftime("%Y%m%dT%H%M%SZ")
            end_str = end_time.strftime("%Y%m%dT%H%M%SZ")
            uid = f"{start_str}-{to_email}"

            ical = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//OpsPilot//CalendarAgent//EN
METHOD:REQUEST
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}
DTSTART:{start_str}
DTEND:{end_str}
SUMMARY:{subject}
DESCRIPTION:{body}
LOCATION:{meet_link or 'Google Meet'}
ORGANIZER;CN=OpsPilot:mailto:me
ATTENDEE;CN={to_email};RSVP=TRUE:mailto:{to_email}
STATUS:CONFIRMED
SEQUENCE:0
TRANSP:OPAQUE
END:VEVENT
END:VCALENDAR""".replace("\n", "\r\n")

            calendar_part = MIMEText(ical, "calendar;method=REQUEST")
            message.attach(calendar_part)

        # Encode to base64 for Gmail API
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        print("📧 Sending email to:", to_email)
        print("🔸 Subject:", subject)
        print("🔸 Body Preview:", body[:150], "..." if len(body) > 150 else "")

        # Send email
        response = gmail_service.users().messages().send(
            userId="me",
            body={"raw": raw}
        ).execute()

        print(f"✅ Email with calendar invite sent to {to_email} | Message ID: {response['id']}")

    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")

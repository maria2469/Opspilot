import os
import pickle
import requests
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the scopes for Google API access
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.freebusy",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]



class InboxAgent:
    def __init__(self):
        self.creds = None

        # Load or refresh credentials
        if os.path.exists("token.pkl"):
            with open("token.pkl", "rb") as token_file:
                self.creds = pickle.load(token_file)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            with open("token.pkl", "wb") as token_file:
                pickle.dump(self.creds, token_file)

    def fetch_all_emails(self, query="is:unread", max_results=50):
        """
        Fetches up to `max_results` emails matching `query` via Gmail REST API using requests.
        Returns a list of dicts with keys: subject, sender, body, date.
        """
        token = self.creds.token
        headers = {"Authorization": f"Bearer {token}"}
        base_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"

        # 1) List message IDs
        params = {"maxResults": max_results, "q": query}
        resp = requests.get(base_url, headers=headers, params=params)
        resp.raise_for_status()
        messages = resp.json().get("messages", [])

        emails = []
        for msg in messages:
            msg_id = msg.get("id")
            try:
                # 2) Get full message
                get_url = f"{base_url}/{msg_id}"
                r2 = requests.get(get_url, headers=headers)
                r2.raise_for_status()
                msg_detail = r2.json()

                payload = msg_detail.get("payload", {})
                headers_list = payload.get("headers", [])

                subject = next((h["value"] for h in headers_list if h["name"] == "Subject"), "No Subject")
                sender = next((h["value"] for h in headers_list if h["name"] == "From"), "Unknown Sender")
                date = next((h["value"] for h in headers_list if h["name"] == "Date"), "")
                snippet = msg_detail.get("snippet", "")

                emails.append({
                    "subject": subject,
                    "sender": sender,
                    "body": snippet,
                    "date": date
                })
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Failed to fetch message {msg_id}: {e}")
            except Exception as e:
                print(f"⚠️ Unexpected error processing message {msg_id}: {e}")

        return emails

    def fetch_emails(self, max_results=5):
        """Fetch the latest unread emails (default wrapper)."""
        return self.fetch_all_emails(query="is:unread", max_results=max_results)

@st.cache_data(show_spinner=False)
def load_emails(_inbox, max_results=50):
    return _inbox.fetch_all_emails(query="is:unread", max_results=max_results)


def display_inbox_ui(inbox):
    st.header("📥 Unread Emails")

    if st.button("🔄 Refresh"):
        load_emails.clear()
    
    emails = load_emails(inbox)
    st.session_state.emails = emails

    if not emails:
        st.info("No unread emails")
        return

    # Create a dict in session state to track selection
    if "selected_email_ids" not in st.session_state:
        st.session_state.selected_email_ids = set()

    st.markdown("✅ **Select emails to include in the report:**")

    for idx, email in enumerate(emails):
        with st.expander(f"📨 {email['subject']} — {email['sender']}"):
            selected = st.checkbox(
                "Include in report",
                key=f"email_{idx}",
                value=email.get("id") in st.session_state.selected_email_ids
            )
            st.write(f"**From:** {email['sender']}")
            st.write(f"**Date:** {email['date']}")
            st.write(email["body"])
            st.markdown("---")

            # Track selected email IDs
            if selected:
                st.session_state.selected_email_ids.add(idx)
            else:
                st.session_state.selected_email_ids.discard(idx)

    # Save selected emails to session state for ReportAgent
    st.session_state.selected_emails = [
        emails[i] for i in st.session_state.selected_email_ids
    ]

    st.success(f"✅ {len(st.session_state.selected_emails)} email(s) selected for report.")

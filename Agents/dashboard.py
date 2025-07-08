import streamlit as st
from datetime import datetime, timedelta

def display_dashboard(inbox, calendar):
    st.header("📊 Team Activity Dashboard")

    with st.spinner("🔄 Fetching real-time data..."):
        # Unread emails (cached)
        emails = inbox.fetch_all_emails(query="is:unread", max_results=100)
        unread_count = len(emails)

        # Recent meetings
        now = datetime.utcnow().isoformat() + "Z"
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"
        events = calendar.service.events().list(
            calendarId="primary",
            timeMin=week_ago,
            timeMax=now,
            singleEvents=True,
            orderBy="startTime"
        ).execute().get("items", [])
        meeting_count = len(events)
        participants = {
            att["email"]
            for ev in events
            for att in ev.get("attendees", [])
            if att.get("email")
        }
        unique_participants = len(participants)

    c1, c2, c3 = st.columns(3)
    c1.metric("📬 Unread Emails", unread_count)
    c2.metric("📅 Meetings (7d)", meeting_count)
    c3.metric("👥 Participants", unique_participants)
    st.caption("⚡ Powered by Gmail + Google Calendar APIs")

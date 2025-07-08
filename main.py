# main.py

import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


# ------------------------
# 🚀 App Config
# ------------------------
st.set_page_config(page_title="OpsPilot | BLACKBOX.AI Track", layout="wide")
st.title("🧠 OpsPilot: AI-Powered Operations for Developers")

# ------------------------
# 📂 Sidebar Navigation
# ------------------------
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio(
    "Select Feature",
    ["🏠 Home","📈 Dashboard", "📥 Inbox", "📊 Reports", "📅 Meetings"],
    index=0
)
if page == "🏠 Home":
    st.markdown("""
        <style>
        .intro-title {
            font-size: 2.4em;
            font-weight: bold;
        }
        .intro-subtitle {
            font-size: 1.3em;
            margin-top: 0.5em;
            color: #555;
        }
        </style>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1.2, 1])  # Wider left for text

    with left_col:
        st.markdown('<div class="intro-title">🤖 Welcome to OpsPilot</div>', unsafe_allow_html=True)
        st.markdown('<div class="intro-subtitle">Your AI-powered operations coordinator for developers.</div>', unsafe_allow_html=True)
        st.markdown("""
        ### 🧠 What problem does it solve?
        Developers waste valuable hours switching between emails, calendars, and meetings.
        OpsPilot eliminates this by acting as your **AI assistant** that:
        
        - 📥 Reads and summarizes emails.
        - 📅 Negotiates and schedules meetings based on routines.
        - 📊 Generates automated reports.
        
        All in one place, with real-time integration using **Groq**, **Gmail**, **Google Calendar**, and more.

        ### 🚀 Why it matters?
        Focus on writing code, let OpsPilot handle the rest.
        """)

    with right_col:
        st.components.v1.html("""
            <iframe src='https://my.spline.design/greetingrobot-si1O8WmNrSfwOdljPAwrfemi/' 
                    frameborder='0' width='100%' height='500px'></iframe>
        """, height=500)

# ------------------------
# 🔁 Page Routing (Lazy Loading)

# ------------------------
elif page == "📈 Dashboard":
    from Agents.inbox import InboxAgent
    from Agents.calendar_agent import CalendarAgent
    from Agents.dashboard import display_dashboard

    inbox = InboxAgent()
    calendar = CalendarAgent()
    display_dashboard(inbox, calendar)

elif page == "📥 Inbox":
    from Agents.inbox import InboxAgent, display_inbox_ui

    inbox = InboxAgent()
    display_inbox_ui(inbox)

elif page == "📊 Reports":
    from Agents.inbox import InboxAgent
    from Agents.Summary_Agent import SummaryAgent
    from Agents.reports import ReportAgent

    inbox = InboxAgent()
    summarizer = SummaryAgent(
        api_key=os.getenv("GROQ_API_KEY"),
        api_url="https://api.groq.com/openai/v1/chat/completions",
        model="llama3-70b-8192"
    )
    ReportAgent(inbox, summarizer).display()

elif page == "📅 Meetings":
    from Agents.calendar_agent import CalendarAgent
    from Agents.meeting_ui import display_meetings

    calendar = CalendarAgent()
    display_meetings(calendar)

# ------------------------
# 📝 Footer
# ------------------------
st.markdown("---")
st.caption("🚀 BLACKBOX.AI Hackathon · Integrated with Groq, Gmail, Calendar, MCP · Team OpsPilot")

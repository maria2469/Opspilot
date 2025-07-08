import os
import requests
import datetime
import streamlit as st
import re


def fetch_past_events(service, email, days_back=14):
    now = datetime.datetime.utcnow()
    past = now - datetime.timedelta(days=days_back)
    try:
        events_result = service.events().list(
            calendarId=email,
            timeMin=past.isoformat() + "Z",
            timeMax=now.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        return events_result.get("items", [])
    except Exception as e:
        st.warning(f"⚠️ Could not fetch events for {email}: {e}")
        return []


def summarize_routine(events):
    if not events:
        return "No recent events available."

    entries = []
    for event in events:
        try:
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))
            summary = event.get("summary", "Busy")
            entries.append(f"- {start} to {end} | {summary}")
        except Exception:
            continue

    prompt = f"""
You are a calendar assistant. Based on the following event history, summarize this user's preferred weekly routine in UTC.

Event history:
{chr(10).join(entries)}

Only return the summary like: "Usually free 10:00–12:00 and 14:00–16:00 UTC on weekdays."
"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
    )

    return response.json()["choices"][0]["message"]["content"].strip()


def negotiate_time_slots(routines):
    prompt = f"""
You are a meeting negotiation assistant. Based on the following participant routines, suggest 3–5 compatible 30-minute time slots **tomorrow** in UTC that fit everyone's routine.

Participant routines:
{chr(10).join([f"- {r}" for r in routines])}

Return only a bullet list of times in this format:  
- YYYY-MM-DD HH:MM
- YYYY-MM-DD HH:MM
"""

    st.info("🤖 AI is negotiating optimal time slots...")

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
    )

    reply = response.json()["choices"][0]["message"]["content"].strip()
    st.success("✅ AI has suggested time slots. Please choose one below.")
    print("\n✅ Suggested Time Slots by LLM:\n", reply)

    # ✅ Robust datetime parser using regex
    slots = []
    for match in re.findall(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2})", reply):
        try:
            dt = datetime.datetime.strptime(match, "%Y-%m-%d %H:%M")
            slots.append(dt)
        except Exception:
            continue

    return slots


def suggest_meeting_time(attendees, calendar_service):
    st.info("🧠 Gathering routines for negotiation...")
    routines = []
    for name, email, _ in attendees:
        st.write(f"📅 Fetching routine for **{name}**...")
        events = fetch_past_events(calendar_service, email)
        summary = summarize_routine(events)
        st.success(f"🧠 {name}'s routine summarized.")
        routines.append(f"{name}: {summary}")

    slots = negotiate_time_slots(routines)

    if not slots:
        st.error("❌ Could not find suitable time slots.")
        return []

    return slots

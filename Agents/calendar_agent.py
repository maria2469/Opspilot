import os
import uuid
import pickle
import base64
import datetime
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .email_utils import send_email
from Agents.llm_negotiator import suggest_meeting_time  # 🧠 LLaMA + history-based negotiation

class CalendarAgent:
    def __init__(self):
        token_path = "token.pkl"
        if not os.path.exists(token_path):
            raise FileNotFoundError("❌ token.pkl not found. Please complete Google OAuth flow first.")

        with open(token_path, "rb") as token_file:
            self.creds = pickle.load(token_file)

        print("✅ Loaded credentials.")

        self.service = build("calendar", "v3", credentials=self.creds)
        self.gmail_service = build("gmail", "v1", credentials=self.creds)
        self.user_name = self._get_authenticated_user_name()
        self.user_email = self._get_authenticated_user_email()

        print(f"✅ Authenticated as {self.user_name} ({self.user_email})")

    def _get_authenticated_user_name(self):
        try:
            user_info = build("oauth2", "v2", credentials=self.creds).userinfo().get().execute()
            return user_info.get("name", "OpsPilot User")
        except Exception as e:
            print(f"⚠️ Failed to fetch user name: {e}")
            return "OpsPilot User"

    def _get_authenticated_user_email(self):
        try:
            user_info = build("oauth2", "v2", credentials=self.creds).userinfo().get().execute()
            return user_info.get("email", "no-reply@opspilot.dev")
        except Exception as e:
            print(f"⚠️ Failed to fetch user email: {e}")
            return "no-reply@opspilot.dev"

    def check_availability(self, attendees, start_time, end_time):
        for _, email, _ in attendees:
            try:
                print(f"🔍 Checking availability for {email} from {start_time} to {end_time}...")
                events_result = self.service.freebusy().query(body={
                    "timeMin": start_time.isoformat() + "Z",
                    "timeMax": end_time.isoformat() + "Z",
                    "items": [{"id": email}]
                }).execute()

                busy_times = events_result.get("calendars", {}).get(email, {}).get("busy", [])
                if busy_times:
                    print(f"⛔ {email} is busy at that time: {busy_times}")
                    return False
            except Exception as e:
                print(f"⚠️ Could not check availability for {email}: {e}")
                return False
        print("✅ All attendees are available.")
        return True

    def suggest_meeting_time(self, attendees):
        print("🧠 Suggesting meeting time using LLM negotiator...")
        return suggest_meeting_time(attendees, self.service)

    def schedule_meeting_multiple(self, attendees, topic, selected_time=None):
        try:
            print("🔐 Starting meeting scheduling...")
            if selected_time:
                print(f"📅 Using selected time: {selected_time}")
                start_time = selected_time
            else:
                time_slots = self.suggest_meeting_time(attendees)
                if not time_slots:
                    print("❌ No suitable time found by LLM.")
                    return "❌ Could not find a suitable time."
                start_time = time_slots[0]

            end_time = start_time + datetime.timedelta(minutes=30)
            time_str = start_time.strftime("%A, %d %B %Y at %H:%M UTC")
            print(f"🕒 Scheduling from {start_time} to {end_time}")

            if not self.check_availability(attendees, start_time, end_time):
                return "❌ One or more attendees are busy during the suggested time."

            attendee_list = [{"email": email} for _, email, _ in attendees]
            if self.user_email not in [a["email"] for a in attendee_list]:
                attendee_list.append({"email": self.user_email, "organizer": True})

            event = {
                        "summary": f"Team Meeting: {topic} (Invited by {self.user_name})",
                        "description": "Scheduled via OpsPilot",
                        "start": {"dateTime": start_time.isoformat() + "Z", "timeZone": "UTC"},
                        "end": {"dateTime": end_time.isoformat() + "Z", "timeZone": "UTC"},
                        "attendees": attendee_list,
                        "conferenceData": {
                            "createRequest": {
                                "conferenceSolutionKey": {"type": "hangoutsMeet"},
                                "requestId": str(uuid.uuid4())
                            }
                        },
                        "reminders": {"useDefault": True}
                    }

            print("📤 Creating event with the following payload:")
            print(event)

            created = self.service.events().insert(
                calendarId="primary",
                body=event,
                conferenceDataVersion=1,
                sendUpdates="all"
            ).execute()

            print("✅ Event created:", created)

            if not created.get("id"):
                print("❌ No event ID returned. Event creation may have failed.")
                return "❌ Event creation failed. No ID returned."

            calendar_link = created.get("htmlLink", "#")
            meet_link = created.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri", "No Meet Link")

            print("📧 Sending invitations...")
            for name, email, role in attendees:
                self._send_invitation_email(name, email, role, topic, start_time, end_time, meet_link, calendar_link)


            names = ", ".join([f"{n} ({r})" for n, _, r in attendees])
            return f"""✅ Meeting Scheduled with: **{names}**\n\n📝 **Topic:** {topic}  \n📅 **Time:** {time_str}  \n🔗 [Calendar Link]({calendar_link})  \n📹 Meet Link: {meet_link}"""

        except HttpError as err:
            print(f"❌ Google Calendar API Error: {err}")
            return f"❌ Google Calendar API Error: {err}"
        except Exception as e:
            print(f"❌ General Error: {e}")
            return f"❌ Error: {e}"

    def _send_invitation_email(self, name, email, role, topic, start_time, end_time, meet_link, calendar_link):
        time_str = start_time.strftime("%A, %d %B %Y at %H:%M")
        body = f"""You're invited to a meeting by {self.user_name}.

📝 Topic: {topic}  
🕙 Time: {time_str} UTC  
🔗 Google Meet: {meet_link}  
📅 Add to Calendar: {calendar_link}

– {self.user_name}
"""
        print(f"📨 Sending email to {email}...")
        send_email(self.gmail_service, email, f"Meeting Invite: {topic} from {self.user_name}", body)
        print(f"✅ Email sent to {email}.")

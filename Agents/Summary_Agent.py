# 📁 File: Agents/summary_agent.py

import os
import requests
from dotenv import load_dotenv
import streamlit as st

# ————————————————
# Load environment
# ————————————————
load_dotenv()
GROQ_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"


# ————————————————
# Summary Logic
# ————————————————
class SummaryAgent:
    def __init__(self, api_key: str, api_url: str, model: str):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model

    def summarize_email(self, subject: str, body: str) -> str:
        prompt = (
            f"You are a highly accurate email summarizer powered by Groq + LLaMA.\n\n"
            f"Summarize this email for a busy operations team:\n"
            f"---\n"
            f"Subject: {subject}\n"
            f"Body:\n{body}\n"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You summarize emails concisely."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4,
        }

        try:
            resp = requests.post(self.api_url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0]["message"]["content"].strip()
            return "⚠️ No summary returned."
        except Exception as e:
            return f"❌ Error: {e}"


# ————————————————
# Streamlit UI
# ————————————————
def main():
    st.set_page_config(page_title="Email Summarizer", layout="centered")
    st.title("📨 Groq Email Summarizer")

    st.markdown(
        """
        Enter an email **Subject** and **Body** below, then click **Summarize**.  
        Uses **Groq + LLaMA** under the hood.
        """
    )

    subject = st.text_input("✉️ Subject", placeholder="Email subject here…")
    body = st.text_area("📝 Body", height=200, placeholder="Paste email body here…")

    if st.button("🧠 Summarize Email"):
        if not subject.strip() or not body.strip():
            st.warning("⚠️ Please provide both subject and body.")
        elif not GROQ_KEY:
            st.error("❌ GROQ_API_KEY missing in .env")
        else:
            agent = SummaryAgent(GROQ_KEY, GROQ_URL, GROQ_MODEL)
            with st.spinner("Summarizing…"):
                summary = agent.summarize_email(subject, body)
            st.subheader("📋 Summary")
            st.write(summary)


if __name__ == "__main__":
    main()

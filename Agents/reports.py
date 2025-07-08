import streamlit as st

class ReportAgent:
    def __init__(self, inbox, summarizer):
        self.inbox = inbox
        self.summarizer = summarizer

    def _generate_markdown(self, emails):
        sections = []
        for idx, email in enumerate(emails, start=1):
            summary = self.summarizer.summarize_email(email["subject"], email["body"])
            sections.append(
                f"""### ✉️ Email {idx}
**From:** {email['sender']}  
**Subject:** {email['subject']}  

**Summary:**  
{summary}  
---
"""
            )
        return "\n".join(sections)

    def display(self):
        st.header("📊 Generate Ops Report")

        # Get selected emails from Inbox page
        emails = st.session_state.get("selected_emails", [])

        if not emails:
            st.warning("⚠️ No emails selected. Please mark emails in the Inbox tab.")
            return

        if st.button("📄 Generate Report"):
            with st.spinner("🧠 Summarizing selected emails..."):
                report_md = self._generate_markdown(emails)
            st.markdown(report_md, unsafe_allow_html=True)

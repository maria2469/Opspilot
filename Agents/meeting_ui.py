import streamlit as st
from Agents.calendar_agent import CalendarAgent

def display_meetings(calendar: CalendarAgent):
    st.header("👥 Schedule a Team Meeting")

    if "members" not in st.session_state:
        st.session_state.members = [{"name": "", "email": "", "role": ""}]
    if "suggested_slots" not in st.session_state:
        st.session_state.suggested_slots = []
    if "selected_slot_str" not in st.session_state:
        st.session_state.selected_slot_str = None

    with st.form("meeting_form"):
        topic = st.text_input("📜 Meeting Topic")
        for idx, mem in enumerate(st.session_state.members):
            c1, c2, c3 = st.columns(3)
            mem["name"] = c1.text_input("👤 Name", mem["name"], key=f"name_{idx}")
            mem["email"] = c2.text_input("✉️ Email", mem["email"], key=f"email_{idx}")
            mem["role"] = c3.text_input("🧑‍💼 Role", mem["role"], key=f"role_{idx}")

        c4, c5, c6 = st.columns([1, 1, 2])
        add = c4.form_submit_button("➕ Add Member")
        clear = c5.form_submit_button("🗑️ Clear")
        submit = c6.form_submit_button("✅ Suggest Time Slots")

    if add:
        st.session_state.members.append({"name": "", "email": "", "role": ""})
        st.info("➕ Member added.")
    if clear:
        st.session_state.members = []
        st.info("🗑️ Members cleared.")

    if submit:
        valid = [(m["name"], m["email"], m["role"]) for m in st.session_state.members if m["name"] and m["email"]]
        if not topic.strip():
            st.warning("⚠️ Enter a meeting topic.")
        elif not valid:
            st.warning("⚠️ Add at least one valid attendee.")
        else:
            with st.spinner("🤖 Suggesting time slots..."):
                st.session_state.suggested_slots = calendar.suggest_meeting_time(valid)
                st.session_state.topic = topic
                st.session_state.valid_attendees = valid
                st.session_state.selected_slot_str = None

    # ✅ Allow user to select one time slot
    if st.session_state.suggested_slots:
        slot_strs = [s.strftime("%Y-%m-%d %H:%M UTC") for s in st.session_state.suggested_slots]
        selected_str = st.selectbox("📅 Pick a time slot:", slot_strs)
        st.session_state.selected_slot_str = selected_str

        if st.button("✅ Confirm and Schedule"):
            chosen_dt = st.session_state.suggested_slots[slot_strs.index(selected_str)]
            with st.spinner("📅 Scheduling meeting..."):
                result = calendar.schedule_meeting_multiple(
                    st.session_state.valid_attendees,
                    st.session_state.topic,
                    selected_time=chosen_dt
                )
            if result.startswith("✅"):
                st.success("🎉 Meeting scheduled successfully!")
                st.markdown(result, unsafe_allow_html=True)
            else:
                st.error("❌ Failed to schedule meeting:")
                st.code(result)

            # Clear UI state
            st.session_state.suggested_slots = []
            st.session_state.selected_slot_str = None

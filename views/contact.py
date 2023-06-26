import time
import streamlit as st
from db_manager import add_message


def contact_page():
    st.markdown("<h1 style='text-align: center'>Contact Us</h1>",
                unsafe_allow_html=True)

    with st.form("contact-form", clear_on_submit=True):
        if not st.session_state["authenticated"]:
            name = st.text_input("Name")
            email = st.text_input("Email")
            subject = st.text_input("Subject")
            content = st.text_area("Content")
        else:
            name = st.session_state["user_name"]
            email = st.session_state["email"]
            subject = st.text_input("Subject")
            content = st.text_area("Content")

        send = st.form_submit_button("Send")

        if send:
            if not name or not email or not subject or not content:
                st.error("All fields are required")
            else:
                add_message(name, email, subject, content)
                success = st.success("Your message was sent successfully sent")
                time.sleep(1.5)
                success.empty()

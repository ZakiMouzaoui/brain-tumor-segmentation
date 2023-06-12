from datetime import datetime, timedelta
import time
from db_manager import authenticate_user, generate_password_reset_token, send_password_reset_email
import streamlit as st
import json
from streamlit_lottie import st_lottie
import re
from streamlit_extras.switch_page_button import switch_page
import jwt
import os
from dotenv import load_dotenv
from streamlit_cookies_manager import EncryptedCookieManager


def auth_page(cookies):
    @st.cache_data
    def load_lottie(path):
        with open(path, "r") as f:
            return json.load(f)

    def validate_email(email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        return re.fullmatch(regex, email)

    # Generate JWT token
    def generate_jwt_token(id, username, role, picture):
        jwt_secret = os.getenv('JWT_SECRET_KEY')

        payload = {
            "id": id,
            "username": username,
            "role": role,
            "picture": picture,
            "exp": datetime.utcnow() + timedelta(hours=1)  # Token expiration time
        }
        token = jwt.encode(payload, jwt_secret, algorithm="HS256")
        return token

    lottie_json = load_lottie("assets/anim-doctor.json")

    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.markdown("<h1 style='text-align: center'>Login</h1>",
                unsafe_allow_html=True)
    load_dotenv()

    if not "remember_me" in cookies or cookies["remember_me"] == "0":
        checked = False
    else:
        checked = True

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        st_lottie(lottie_json, height=250)
        with st.form("login-form"):
            email = st.text_input(
                "Email", value=cookies["email"] if checked else "")
            password = st.text_input(
                "Password", type="password", value=cookies["password"] if checked else "")
            keep_me = st.checkbox("Remember me", value=checked)

            st.markdown("</br>", unsafe_allow_html=True)
            login = st.form_submit_button("Login")
            if login:
                if not email or not password:
                    st.error("All fields are required")
                else:
                    if not validate_email(email):
                        st.error("Enter a valid email")
                    else:
                        response = authenticate_user(email, password)
                        if response["status"] == "error":
                            st.error(response["message"])

                        else:
                            st.session_state["authenticated"] = True
                            st.session_state["user_id"] = response["result"][0]
                            st.session_state["role"] = response["result"][1]
                            st.session_state["user_name"] = response["result"][2]
                            st.session_state["user_pic"] = response["result"][-1]
                            st.session_state["email"] = response["result"][4]
                            st.session_state["is_active"] = response["result"][3]

                            # token = generate_jwt_token(
                            #     st.session_state["user_id"], st.session_state["user_name"], st.session_state["role"], st.session_state["user_pic"])
                            if keep_me:
                                st.write("keep me")
                                cookies["remember_me"] = "1"
                                cookies["email"] = email
                                cookies["password"] = password
                            else:
                                cookies["remember_me"] = "0"
                                cookies["email"] = ""
                                cookies["password"] = ""

                            cookies["user_id"] = str(response["result"][0])
                            cookies["user_name"] = str(response["result"][2])
                            cookies["user_pic"] = str(response["result"][-1])
                            cookies["role"] = str(response["result"][1])
                            cookies["email"] = response["result"][4]
                            cookies["is_active"] = str(response["result"][3])

                            # st.experimental_set_query_params(uid=token)
                            st.experimental_rerun()

        with st.expander("Forgot password?"):
            with st.form("reset-form"):
                email = st.text_input("Email")
                send = st.form_submit_button("Send")

                if send:
                    if not email:
                        st.error("Email field is required")
                    elif not validate_email(email):
                        st.error("Enter a valid email")
                    else:
                        token = generate_password_reset_token(email)
                        with st.spinner("Sending ..."):
                            sent = send_password_reset_email(email, token)
                        if sent:
                            success = st.success(
                                "An email was sent to you. Click the button below to reset your password")
                            time.sleep(2.5)
                            success.empty()
                            st.session_state["Resetting"] = True
                        else:
                            st.error("An error while sending the email")

        if "Resetting" in st.session_state and st.session_state["Resetting"] == True:
            reset = st.button('Reset password')
            if reset:
                switch_page("Reset Password")

    # with col2:
    #     with st.form("signup-form"):
    #         name = st.text_input("Name")
    #         email = st.text_input("Email")
    #         pwd1 = st.text_input("Password", type="password")
    #         pwd2 = st.text_input("Confirm Password", type="password")
    #         signup = st.form_submit_button("Sign Up")

    #         if signup:
    #             if not email or not name or not pwd1:
    #                 st.error("All fields are required")
    #             else:
    #                 if not validate_email(email):
    #                         st.error("Enter a valid email")
    #                 else:
    #                     if not confirm_password(pwd1, pwd2):
    #                         st.error("Passwords are not matching")
    #                     else:
    #                         email_exists = check_email_exists(email)
    #                         if email_exists:
    #                             st.error("Email already exists")
    #                         else:
    #                             create_user(name, email, password)
    #                             st.success("Thank you for your registration")

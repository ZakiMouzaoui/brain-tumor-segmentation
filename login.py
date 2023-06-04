import time
from db_manager import authenticate_user, create_user, generate_password_reset_token, check_email_exists, send_password_reset_email
import streamlit as st
import json
from streamlit_lottie import st_lottie
import re
from streamlit_extras.switch_page_button import switch_page


def auth_page(cookies):
    @st.cache_data
    def load_lottie(path):
        with open(path, "r") as f:
            return json.load(f)

    def validate_email(email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        return re.fullmatch(regex, email)

    # if not bool(st.session_state):
    #         with open('.streamlit/config.toml', 'r') as file:
    #             config = toml.load(file)
    #         st.session_state["theme"] = config["theme"]["base"]
    #         st.session_state["config"] = config
    #         st.session_state["disabled"] = True
    #         st.session_state["submitted"] = False
    #         st.session_state["segment_loading"] = False
    #         st.session_state["segmented"] = False
    #         st.session_state["converted"] = False
    #         st.session_state["prediction"] = None

    # with st.sidebar:
    #         col1, col2, _ = st.columns(3)
    #         theme = st.session_state["theme"]
    #         with col1:
    #             if  theme == "dark":
    #                 theme_btn = st.button("🔆")
    #             else:
    #                 theme_btn = st.button("🌑")

    #             if theme_btn:
    #                 if theme == "dark":
    #                     st.session_state["theme"] = "light"
    #                 else:
    #                     st.session_state["theme"] = "dark"

    #                 change_theme(st.session_state["config"], st.session_state["theme"])
    #                 st.experimental_rerun()
    lottie_json = load_lottie("assets/anim-doctor.json")

    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.markdown("<h1 style='text-align: center'>Login</h1>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        st_lottie(lottie_json, height=250)
        with st.form("login-form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            keep_me = st.checkbox("Keep me logged in")
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

                            cookies["user_id"] = str(response["result"][0])
                            cookies["role"] = str(response["result"][1])
                            cookies["user_name"] = response["result"][2]
                            cookies["user_pic"] = response["result"][-1]
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

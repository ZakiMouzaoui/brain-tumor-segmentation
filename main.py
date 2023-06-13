import base64
import streamlit as st
from streamlit_option_menu import option_menu as om
import toml
from dotenv import load_dotenv
import os
from streamlit_cookies_manager import EncryptedCookieManager
import views


def change_theme(config, theme):
    config['theme']["base"] = theme
    config['theme']["primaryColor"] = "#265B94"
    with open('.streamlit/config.toml', 'w') as file:
        toml.dump(config, file)


load_dotenv()


# def verify_jwt_token(token):
#     try:
#         payload = jwt.decode(token, os.getenv(
#             "JWT_SECRET_KEY"), algorithms=["HS256"])
#         return payload
#     except jwt.ExpiredSignatureError:
#         return None  # Token has expired
#     except jwt.InvalidTokenError:
#         return None  # Invalid token


st.set_page_config(page_title='Brain AI', page_icon="🧠", layout="wide")

st.markdown("""

        <style>
        .css-15zrgzn {display: none}
        .css-eczf16 {display: none}
        .css-jn99sy {display: none}
        div[data-testid="stMarkdownContainer"] > p{
                font-size:1.2rem
        }
        </style>
        """, unsafe_allow_html=True)


def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


if not "theme" in st.session_state:
    with open('.streamlit/config.toml', 'r') as file:
        config = toml.load(file)
    st.session_state["theme"] = config["theme"]["base"]
    st.session_state["config"] = config


def get_cookies():
    cookies = EncryptedCookieManager(
        prefix="brain-ai-cookies/",
        password=os.getenv("COOKIES_PASSWORD"),
    )

    if not cookies.ready():
        st.stop()
    return cookies


cookies = get_cookies()

if not "authenticated" in st.session_state or st.session_state["authenticated"] is None:
    # token = verify_jwt_token(
    #     st.experimental_get_query_params().get("uid", [None])[0])

    # if not token:
    #     st.session_state["authenticated"] = False
    # else:
    #     st.session_state["authenticated"] = True
    #     st.session_state["user_id"] = token["id"]
    #     st.session_state["doctor_patients"] = []
    #     st.session_state["prediction"] = None
    #     st.session_state["role"] = token["role"]
    #     st.session_state["user_name"] = token["username"]
    #     st.session_state["user_pic"] = token["picture"]

    if not "user_id" in cookies or cookies["user_id"] == "-1":
        st.session_state["authenticated"] = False
    else:
        st.session_state["authenticated"] = True
        st.session_state["user_id"] = cookies["user_id"]
        st.session_state["role"] = cookies["role"]
        st.session_state["user_name"] = cookies["user_name"]
        st.session_state["user_pic"] = cookies["user_pic"]
        st.session_state["email"] = cookies["email"]

pages_ = []
icons_ = []

if not st.session_state["authenticated"]:
    pages_ = ["Login", "Contact"]
    icons_ = ["person", "envelope-at"]

else:
    role = str(st.session_state["role"])
    if role == "0":
        pages_ = ["Dashboard", "History"]
        icons_ = ["card-checklist", "clock-history"]

    elif role == "1":
        pages_ = ["Home", "Patients"]
        icons_ = ["house", "bi-people"]
    elif role == "2":
        pages_ = ["Dashboard"]
        icons_ = ["card-checklist"]
    else:
        pages_ = ["Medical Record"]
        icons_ = ["journal-text"]

    pages_.append("Profile")
    icons_.append("person")
    if role != "0":
        pages_.append("Contact")
        icons_.append("envelope-at")

with st.sidebar:
    if st.session_state["authenticated"]:
        user_name = st.session_state["user_name"]
        user_pic = st.session_state['user_pic']
        encoded_img = get_base64_of_bin_file(user_pic)

        st.markdown(
            f"<h2 style='text-align: center'>{user_name}</h2>", unsafe_allow_html=True)
        st.markdown(
            f'<img width=100, height=110, style="display: block; margin-left: auto; margin-right: auto; border-radius: 50%" src="data:image/png;base64,{encoded_img}" alt="Profile Picture">', unsafe_allow_html=True)
        st.markdown(" ")

    selected = om("", pages_, icons=icons_, default_index=0)

    col1, col2, _ = st.columns(3)
    theme = st.session_state["theme"]

    with col1:
        if theme == "dark":
            theme_btn = st.button("🔆", help="Light theme")
        else:
            theme_btn = st.button("🌑", help="Dark theme")

        if theme_btn:
            if theme == "dark":
                st.session_state["theme"] = "light"
            else:
                st.session_state["theme"] = "dark"

            change_theme(st.session_state["config"], st.session_state["theme"])
            st.experimental_rerun()
        with _:
            if st.session_state["authenticated"]:
                logout = st.button("Logout ")
                if logout:
                    cookies["user_id"] = "-1"

                    st.session_state["authenticated"] = None
                    st.session_state["patients-order"] = None
                    st.experimental_set_query_params()
                    st.experimental_rerun()
    st.markdown(
        """
            <div style="text-align: center;">
                <p style="font-size: 1rem; color: #888;">
                    &copy; 2023 Brain AI. All rights reserved
                </p>
            </div>
        """,
        unsafe_allow_html=True
    )

if selected == "Home":
    from views import home
    home.home_page()
else:
    st.session_state["submitted"] = False
    if selected == "Login":
        from views import login
        login.auth_page(cookies)
    elif selected == "Dashboard":
        if role == '0':
            from views import dashboard
            dashboard.dashboard_page()
        else:
            from views import staff_dashboard
            staff_dashboard.staff_dashboard()

    elif selected == "Contact":
        from views import contact
        contact.contact_page()
    elif selected == "History":
        from views import history
        history.history_page()
    elif selected == "Patients":
        from views import stats
        stats.stats_page()
    elif selected == "Profile":
        from views import profile_page
        profile_page.profile_page(cookies)
    elif selected == "Medical Record":
        from views import appointments
        appointments.appointments_page()

padding = 0
st.markdown(f"""
        <style>
            .reportview-container .main .block-container{{
            padding-top: {padding}rem;
            padding-right: {padding}rem;
            padding-left: {padding}rem;
            padding-bottom: {padding}rem;

        }} </style> """, unsafe_allow_html=True)

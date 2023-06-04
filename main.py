import base64
import streamlit as st
from streamlit_option_menu import option_menu as om
from streamlit_cookies_manager import EncryptedCookieManager
import toml


def change_theme(config, theme):
    config['theme']["base"] = theme
    config['theme']["primaryColor"] = "#265B94"
    with open('.streamlit/config.toml', 'w') as file:
        toml.dump(config, file)


st.set_page_config(page_title='Brain AI', page_icon="🧠", layout="wide")


def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


cookies = EncryptedCookieManager(
    prefix="brats_v1/streamlit-cookies-manager/",
    password="secret_password12345",
)

if not cookies.ready():
    st.stop()

if not "user_id" in st.session_state:
    with open('.streamlit/config.toml', 'r') as file:
        config = toml.load(file)
    st.session_state["theme"] = config["theme"]["base"]
    st.session_state["config"] = config

    if not "user_id" in cookies or cookies["user_id"] == "-1":
        st.session_state["authenticated"] = False
        st.session_state["user_id"] = "-1"

    else:
        st.session_state["authenticated"] = True
        st.session_state["user_id"] = cookies["user_id"]
        st.session_state["user_name"] = cookies["user_name"]
        st.session_state["user_pic"] = cookies["user_pic"]
        st.session_state["role"] = cookies["role"]

    st.session_state["submitted"] = False
    st.session_state["segment_loading"] = False
    st.session_state["segmented"] = False
    st.session_state["converted"] = False
    st.session_state["prediction"] = None
    st.session_state["t1_key"] = None
    st.session_state["t1ce_key"] = None
    st.session_state["t2_key"] = None
    st.session_state["flair_key"] = None
    st.session_state["clicked_btn"] = False

pages = []
icons = []

if "role" in st.session_state:
    role = str(st.session_state["role"])

if not st.session_state["authenticated"]:
    pages = ["Home", "Login", "Contact"]
    icons = ["house", "person", "envelope-at"]

else:
    if role == "0" or role == "2":
        pages = ["Dashboard", "History"]
        icons = ["card-checklist", "clock-history"]
    elif role == "1":
        pages = ["Home", "Patients"]
        icons = ["house", "bi-people"]

        # notifications = view_notifications(st.session_state["user_id"])
        # new_notifications = list(filter(lambda x: x[4] == 0, notifications))
        # old_notifications = list(filter(lambda x: x[4] == 1, notifications))

        # st.session_state["new_notifications"] = new_notifications
        # st.session_state["old_notifications"] = old_notifications

        # if not new_notifications:
        #     pages.append("Notifications")
        # else:
        #     pages.append(f"Notifications ({len(new_notifications)})")
    else:
        pages = ["Medical Record"]
        icons = ["journal-text"]

    pages.append("Profile")
    icons.append("person")
    if role != "0":
        pages.append("Contact")
        icons.append("envelope-at")


with st.sidebar:
    if st.session_state["authenticated"]:
        user_name = st.session_state["user_name"]
        user_pic = st.session_state['user_pic']
        encoded_img = get_base64_of_bin_file(user_pic)

        st.markdown(
            f"<h2 style='text-align: center'>{user_name}</h2>", unsafe_allow_html=True)
        st.markdown(
            f'<img width=92, height=98, style="display: block; margin-left: auto; margin-right: auto; border-radius: 50%" src="data:image/png;base64,{encoded_img}" alt="Profile Picture">', unsafe_allow_html=True)
        st.markdown(" ")

    selected = om("", pages, icons=icons, default_index=0)

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
                    st.session_state["authenticated"] = False
                    st.experimental_rerun()
    # st.subheader("How to use ❓")
    # st.markdown("""
    #     <ol>
    #         <li>Upload your MRI sequences files either in NIFTI or DICOM format</li>
    #         <li>Click on Segmentation button. You will have the ability to choose whether to preprocess yout MRI scans or not by removing the skull from them</li>
    #         <li>After the segmentation you can view your MRI sequences and choose between them as well as the segmented tumor</li>
    #     </ol>
    #     """, unsafe_allow_html=True)

    # st.subheader("About ℹ️")
    # st.markdown("""
    #     <div>
    #         <p>Brain AI is a web app that allows neurologist to segment a tumor from MRI scans using a deep learning model</p>
    #     </div>
    #     """, unsafe_allow_html=True)

    # st.divider()
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
    from Home import home_page
    home_page()
elif selected == "Login":
    from login import auth_page
    auth_page(cookies)
elif selected == "Dashboard":
    if role == '0':
        from dashboard import dashboard_page
        dashboard_page()
    else:
        from staff_dashboard import staff_dashboard
        staff_dashboard()

elif selected == "Contact":
    from contact import contact_page
    contact_page()
elif selected == "History":
    from history import history_page
    history_page()
elif selected == "Patients":
    from stats import stats_page
    stats_page()
elif selected == "Profile":
    from profile_page import profile_page
    profile_page(cookies)
elif selected == "Medical Record":
    from appointments import appointments_page
    appointments_page()

padding = 0
st.markdown(f"""
        <style>
            .reportview-container .main .block-container{{
            padding-top: {padding}rem;
            padding-right: {padding}rem;
            padding-left: {padding}rem;
            padding-bottom: {padding}rem;

        }} </style> """, unsafe_allow_html=True)

st.markdown("""

        <style>
        .css-15zrgzn {display: none}
        .css-eczf16 {display: none}
        .css-jn99sy {display: none}
        div[data-testid="stMarkdownContainer"] > p{
                font-size:1.2rem
        }
        # p{
        #     font-size:1.3rem

        # }
        i{
            color: red !important
        }
        </style>
        """, unsafe_allow_html=True)

import streamlit as st
from db_manager import change_password, change_profile_pic
import time
from PIL import Image
import os

def profile_page(cookies):
    def confirm_password(pwd1, pwd2):
        return pwd1 == pwd2
    
    st.markdown("<h1 style='text-align: center'>Profile 👤</h1>", unsafe_allow_html=True)
    st.markdown(" ")
    user_id = st.session_state["user_id"]
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Change password")
        with st.form("password-form"):
            old_pwd = st.text_input("Old password", type="password")
            pwd1 = st.text_input("New password", type="password")
            pwd2 = st.text_input("Confirm new password", type="password")

            change = st.form_submit_button("Change")
            if change:
                if not old_pwd or not pwd1 or not pwd2:
                    st.error("All fields are required")
                else:
                    if not confirm_password(pwd1, pwd2):
                        st.error("Passwords are not matching")
                   
                    else:
                        response = change_password(user_id, old_pwd, pwd1)

                        if response["status"] == "error":
                            st.error(response["message"])
                        else:
                            success = st.success("Password changed successfully")
                            time.sleep(1.5)
                            success.empty()

    with c2:
        st.subheader("Change picture")
        file = st.file_uploader("_", label_visibility="collapsed", type=["png", "jpg", "jpeg", "webp"])
        _,col2,_ = st.columns([2,1,2])
        with col2:
            save = st.button("Save", disabled=file is None, use_container_width=True)
        if save:
            image = Image.open(file)
                
            os.makedirs(f"uploads/{user_id}", exist_ok=True)
            ext = file.name.split(".")[-1]
            path = f"uploads/{user_id}/profile_img.{ext}"
            image.save(path)
            st.session_state["user_pic"] = path
            cookies["user_pic"] = path
            change_profile_pic(user_id, path)
            st.experimental_rerun()
            success = st.success("Image changed successfully")
            time.sleep(1.5)
            success.empty()
            
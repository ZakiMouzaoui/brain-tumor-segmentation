import base64
import time
from db_manager import (
    edit_user, retrieve_users,
    view_all_patients,
    block_unblock_user,
    get_messages,
    mark_as_read,
    add_history,
    delete_single_message,
    delete_all_messages,
    create_user,
    get_ratings
)

import streamlit as st
from streamlit_card import card
import pandas as pd
import streamlit_nested_layout
import re


def dashboard_page():
    @st.cache_data(show_spinner=False)
    def get_base64_staff(bin_file):
        with open(bin_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    @st.cache_data(show_spinner=False)
    def get_base64_doctor(bin_file):
        with open(bin_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    @st.cache_data(show_spinner=False)
    def get_base64_patient(bin_file):
        with open(bin_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    @st.cache_data(show_spinner=False)
    def get_base64_message(bin_file):
        with open(bin_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    def paginate(items, per_page):
        pages = [items[i:i+per_page] for i in range(0, len(items), per_page)]
        return {
            'total': len(items),
            'pages_no': len(pages),
            'pages': pages
        }

    def validate_email(email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        return re.fullmatch(regex, email)

    def retrieve_users_():
        users = retrieve_users()
        return users

    def retrieve_patients_():
        patients = view_all_patients()
        return patients

    def retrieve_ratings():
        ratings = get_ratings()
        return ratings

    def retrieve_messages():
        all_messages = get_messages()
        st.session_state["all_messages"] = all_messages

    st.markdown("<h1 style='text-align: center'>Dashboard</h1>",
                unsafe_allow_html=True)

    if not "patients-order" in st.session_state or st.session_state["patients-order"] is None:
        st.session_state["patients"] = retrieve_patients_()
        st.session_state["users"] = retrieve_users_()
        st.session_state["ratings"] = retrieve_ratings()
        st.session_state["users-idx"] = 0
        st.session_state["patients-idx"] = 0
        st.session_state["users-order"] = "Name(A-Z)"
        st.session_state["patients-order"] = "Name(A-Z)"
        retrieve_messages()

    users = st.session_state["users"]
    patients = st.session_state["patients"]
    all_messages = st.session_state["all_messages"]
    doctors = list(filter(lambda x: x[4] == 1, users))
    staffs = list(filter(lambda x: x[4] == 2, users))

    col1, col2, col3, col4 = st.columns(4)

    # with col1:
    #     card(
    #         title="Doctors",
    #         text=f"{len(doctors)}",
    #         image="https://img.freepik.com/premium-vector/avatar-male-doctor-with-black-hair-beard-doctor-with-stethoscope-vector-illustrationxa_276184-32.jpg?w=2000",
    #         url=""
    #     )

    # with col2:
    #     card(
    #         title="Staffs",
    #         text=f"{len(staffs)}",
    #         image="https://banner2.cleanpng.com/20191121/lkg/transparent-staff-icon-hotel-icon-service-icon-5dd63a2248cce4.9645499215743206742982.jpg",
    #         url=""
    #     )

    # with col3:
    #     card(
    #         title="Patients",
    #         text=f"{len(patients)}",
    #         image="https://cdn3.iconfinder.com/data/icons/corona-pandemic-disease/512/005-patient-512.png",
    #         url="",
    #     )

    new_messages = list(filter(lambda x: x[5] == 0, all_messages))
    seen_messages = list(filter(lambda x: x[5] == 1, all_messages))

    staff_img = get_base64_staff("assets/staff_icon.png")
    doctor_img = get_base64_doctor("assets/doctor_icon.png")
    patient_img = get_base64_patient("assets/patient_icon.png")
    message_img = get_base64_message("assets/new_message.jpg")

    st.write(f"""
        <div class="cards-list">
            <div class="card 1">
                <div class="card_image"> <img src="data:image/png;base64,{doctor_img}" /> </div>
                <div class="card_title">
                    Doctors
                    <div class="card-subtitle">{len(doctors)}</div>
                </div>
            </div>
            <div class="card 1">
                <div class="card_image"> <img src="data:image/png;base64,{staff_img}" /> </div>
                <div class="card_title">
                    Staffs
                    <div class="card-subtitle">{len(staffs)}</div>
                </div>
            </div>
            <div class="card 1">
                <div class="card_image"> <img src="data:image/png;base64,{patient_img}" /> </div>
                <div class="card_title">
                    Patients
                    <div class="card-subtitle">{len(patients)}</div>
                </div>
            </div>
            <div class="card 1">
                <div class="card_image"> <img src="data:image/png;base64,{message_img}" /> </div>
                <div class="card_title">
                    New Messages
                    <div class="card-subtitle">{len(new_messages)}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('''
        <style>
            .cards-list {
        z-index: 0;
        width: 100%;
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        }

        .card {
        position: relative;
        margin: 30px auto;
        width: 300px;
        height: 250px;
        border-radius: 40px;
        box-shadow: 5px 5px 30px 7px rgba(0,0,0,0.1), -5px -5px 30px 7px rgba(0,0,0,0.1);
        cursor: pointer;
        transition: 0.4s;
        }

        .card .card_image {
        width: inherit;
        height: inherit;
        border-radius: 40px;
        linear-gradient(to bottom, rgba(245, 246, 252, 0.52), rgba(117, 19, 93, 0.73))
        }

        .card .card_image img {
        width: inherit;
        height: inherit;
        border-radius: 40px;
        object-fit: cover;
        }

        .card .card_title {
        text-align: center;
        border-radius: 40px;
        font-weight: bold;
        font-size: 2rem !important;
        position: absolute;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.35); /* Adjust the opacity as needed */
        color: #fff;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        }

        .card:hover {
        transform: scale(0.9, 0.9);
        box-shadow: 5px 5px 30px 15px rgba(0,0,0,0.25), 
            -5px -5px 30px 15px rgba(0,0,0,0.22);
        }

        @media all and (max-width: 500px) {
        .card-list {
            /* On small screens, we are no longer using row direction but column */
            flex-direction: column;
            }
        }
        </style>
    ''', unsafe_allow_html=True)

    # with col4:
    #     card(
    #         title="New Messages",
    #         text=f"{len(new_messages)}",
    #         image="https://img.uxwing.com/wp-content/themes/uxwing/download/communication-chat-call/text-message-icon.png",
    #         url=""
    #     )
#     st.markdown("""
#         <div class="card">
#         <h2 class="card-title">Doctors</h2>
#         <h3 class="card-subtitle">2</h3>
#         <img class="card-image" src="https://cdn-icons-png.flaticon.com/512/3774/3774299.png" alt="Image 1">
#     </div>

#     <div class="card">
#         <h2 class="card-title">Staffs</h2>
#         <h3 class="card-subtitle">1</h3>
#         <img class="card-image" src="https://cdn-icons-png.flaticon.com/512/3461/3461573.png" alt="Image 2">
#     </div>

#     <div class="card">
#         <h2 class="card-title">Patients</h2>
#         <h3 class="card-subtitle">4</h3>
#         <img class="card-image" src="https://cdn3.iconfinder.com/data/icons/corona-pandemic-disease/512/005-patient-512.png" alt="Image 3">
#     </div>

#     <div class="card">
#         <h2 class="card-title">New messages</h2>
#         <h3 class="card-subtitle">2</h3>
#         <img class="card-image" src="https://icons-for-free.com/iconfiles/png/512/inbox+message+one+message+icon-1320166594682862187.png" alt="Image 4">
#     </div>
#     """, unsafe_allow_html=True)
#     st.markdown("""
#         <style>
#     .card {
#       display: inline-block;
#       width: 22.8%;
#       margin: 0.95%;
#       padding: 1%;
#       border-radius: 5px;
#       border: 1px solid #ddd;
#       position: relative;
#     }

#     .card-title {
#       font-size: 1.5rem;
#       font-weight: bold;
#       margin-bottom: 5px;
#     }

#     .card-subtitle {
#       font-size: 1.2rem;
#       color: #666;
#       margin-bottom: 10px;
#     }

#     .card-image {
#       position: absolute;
#       top: 0;
#       right: 0;
#       width: 30%;
#       margin-top:10%;
#       margin-right: 5%;
#       border-radius: 5px;
#       height: 50;
#       width:50;
#     }
#   </style>
#     """, unsafe_allow_html=True)

    cc1, cc2 = st.columns(2)
    paginated_users = users.copy()
    paginated_patients = patients.copy()

    with cc1:
        _, __ = st.columns(2)
        with _:
            order_user = st.selectbox("Sort users by", options=[
                                      "Name(A-Z)", "Name(Z-A)", "Date ⬆️", "Date ⬇️"])
            if order_user == "Name(A-Z)":
                paginated_users = sorted(paginated_users, key=lambda x: x[1])

            elif order_user == "Name(Z-A)":
                paginated_users = sorted(
                    paginated_users, key=lambda x: x[1], reverse=True)

            elif order_user == "Date ⬆️":
                paginated_users = sorted(paginated_users, key=lambda x: x[-1])

            else:
                paginated_users = sorted(
                    paginated_users, key=lambda x: x[-1], reverse=True)

            if order_user != st.session_state["users-order"]:
                st.session_state["users-idx"] = 0
            st.session_state["users-order"] = order_user

        th_props = [
            ('font-size', '1rem'),
            ('text-align', 'center'),
            ('font-weight', 'bold'),
            ('color', '#6d6d6d'),
        ]

        td_props = [
            ('font-size', '1rem')
        ]

        styles = [
            dict(selector="th", props=th_props),
            dict(selector="td", props=td_props)
        ]

        pagination = paginate(paginated_users, 2)
        idx = st.session_state["users-idx"]
        paginated_users = pagination["pages"][st.session_state["users-idx"]]

        users_df = pd.DataFrame(
            paginated_users, columns=["Id", "Name", "Sex", "Email", "Role", "Status", "Joining date"])
        # users_df.drop("Id", inplace=True, axis=1)
        users_df['Status'] = users_df['Status'].replace(
            {0: 'Blocked', 1: 'Active'})
        users_df['Sex'] = users_df['Sex'].replace({"Male": 'M', "Female": 'F'})
        users_df['Role'] = users_df['Role'].replace({1: 'Doctor', 2: 'Staff'})
        users_df = users_df.style.set_properties(
            **{'text-align': 'left'}).set_table_styles(styles)

        st.subheader("Users")
        st.table(users_df)

        pages_no = pagination["pages_no"]
        ccc1, ccc2 = st.columns(2)

        with ccc1:
            co1, co2, co3 = st.columns([3, 1, 5])
            with co1:
                previous = st.button(
                    "previous", key="previous-users", disabled=idx == 0)
                if previous:
                    idx = idx - 1

                    st.session_state["users-idx"] = idx
                    st.experimental_rerun()
            with co2:
                st.write(f"{idx+1}/{pages_no}")
            with co3:
                next = st.button("next", key="next-users",
                                 disabled=idx == pages_no-1)
                if next:
                    idx = idx + 1
                    st.session_state["users-idx"] = idx
                    st.experimental_rerun()

        # with co1:
        #     cc_1, cc_2, cc_3 = st.columns(3)
        #     current_page = st.session_state["current_page"]
        #     total_pages = st.session_state["total_pages"]

        #     with cc_1:
        #         if current_page > 1:
        #             if st.button("Previous"):
        #                 current_page -= 1
        #                 st.session_state["current_page"] = current_page
        #                 st.experimental_rerun()
        #         else:
        #             st.button("Previous", disabled=True)

        #     with cc_2:
        #         st.write(f"Page {current_page} of {total_pages}")
        #     with cc_3:
        #         if current_page < total_pages:
        #             if st.button("Next"):
        #                 current_page += 1
        #                 st.session_state["current_page"] = current_page
        #                 st.experimental_rerun()
        #         else:
        #             st.button("Next", disabled=True)

        # retrieve_users_(st.session_state["order_col_user"], st.session_state["order_type_user"])

        # custom_css = {
        #     ".ag-row": {"font-size": "1rem !important"},
        #     ".ag-header-cell-label": {"font-size": "1rem !important"}
        # }

        # df  = pd.DataFrame(users, columns=["Id", "Name", "Sex", "Email", "Status", "Joining date"])
        # gd = GridOptionsBuilder.from_dataframe(users_df)
        # gd.configure_pagination(enabled=True)
        # gd.configure_selection(selection_mode="multiple", use_checkbox=True)
        # gd.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=2)
        # gridOptions = gd.build()

        # AgGrid(
        #     users_df, gridOptions=gridOptions,
        #     columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        #     custom_css=custom_css, update_mode=GridUpdateMode.MODEL_CHANGED,
        #     key="user-aggrid"
        #     )

        # with column2:
        #     for i in range(6):
        #         st.markdown(" ")
        #     csv_file = st.file_uploader("Or import a csv file", type=["csv"])
        #     confirm = st.button("Confirm", disabled=csv_file is None)
    with cc2:
        # patients = retrieve_patients_(st.session_state["order_col_patient"], st.session_state["order_type_patient"])
        _, __ = st.columns(2)
        with _:
            order_patient = st.selectbox("Sort patients by", options=[
                                         "Name(A-Z)", "Name(Z-A)", "Date ⬆️", "Date ⬇️"])
            if order_patient == "Name(A-Z)":
                paginated_patients = sorted(
                    paginated_patients, key=lambda x: x[1])

            elif order_patient == "Name(Z-A)":
                paginated_patients = sorted(
                    paginated_patients, key=lambda x: x[1], reverse=True)

            elif order_patient == "Date ⬆️":
                paginated_patients = sorted(
                    paginated_patients, key=lambda x: x[-1])

            else:
                paginated_patients = sorted(
                    paginated_patients, key=lambda x: x[-1], reverse=True)
            if order_patient != st.session_state["patients-order"]:
                st.session_state["patients-idx"] = 0
                st.session_state["patients-order"] = order_patient

        patient_pagination = paginate(paginated_patients, 2)

        pages_no = patient_pagination["pages_no"]
        patient_idx = st.session_state["patients-idx"]
        paginated_patients = patient_pagination["pages"][patient_idx]
        patients_df = pd.DataFrame(paginated_patients, columns=[
                                   "Id", "Name", "Email", "Sex", "Age", "User Id", "Assigned to", "Joining date", ])
        patients_df.drop('User Id', inplace=True, axis=1)
        patients_df = patients_df.style.set_properties(
            **{'text-align': 'left'}).set_table_styles(styles)

        st.subheader("Patients")
        st.table(patients_df)
        cc1, cc2 = st.columns(2)
        with cc1:
            co1, co2, co3 = st.columns([3, 1, 5])
            with co1:
                previous_btn = st.button(
                    "previous", key="previous-patients", disabled=patient_idx == 0)
                if previous_btn:
                    patient_idx -= 1
                    st.session_state["patients-idx"] = patient_idx
                    st.experimental_rerun()
            with co2:
                st.write(f"{patient_idx+1}/{pages_no}")
            with co3:
                next_btn = st.button(
                    "next", key="next-patients", disabled=patient_idx == pages_no-1)
                if next_btn:
                    patient_idx += 1
                    st.session_state["patients-idx"] = patient_idx
                    st.experimental_rerun()

    # st.divider()
    # co1, _ = st.columns(2)
    # with co1:
    #     requests_df = pd.DataFrame(requests, columns=["Id","Name", "Sex", "Age", "Tumor", "user_id", "Requested by", "Date"])
    #     requests_df.drop("user_id", inplace=True, axis=1)
    #     #requests_df = requests_df.style.set_properties(**{'text-align': 'left'}).set_table_styles(styles)

    #     st.subheader("Pending requests")
    #     st.table(requests_df)

    st.divider()
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("Add a new user")
        with st.form("add-user-form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            sex = st.selectbox("Sex", options=["Male", "Female"])
            role = st.selectbox(
                "Role", options=[1, 2], format_func=lambda x: "Doctor" if x == 1 else "Staff")
            add = st.form_submit_button("Create")

            if add:
                if not name or not email:
                    st.error("All fields are required")
                elif not validate_email(email):
                    st.error("Invalid email format")
                else:
                    create = False
                    with st.spinner(""):
                        create = create_user(name, email, sex, role)
                    if create:
                        st.session_state["create-user-success"] = True
                        retrieve_users_()
                        st.experimental_rerun()
                    else:
                        st.session_state["create-user-success"] = None
                        st.error("Something went wrong")
            if "create-user-success" in st.session_state and st.session_state["create-user-success"] is not None:
                st.success("User created successfully")
                st.session_state["create-user-success"] = None

    with c2:
        st.subheader("Edit a user info")
        if users:
            edit_select = st.selectbox(
                "Select a user", options=users, format_func=lambda x: x[1])

            with st.form("edit-form"):
                name = st.text_input("Name", value=edit_select[1])
                sex = st.selectbox("Sex", options=["Male", "Female"])
                edit_btn = st.form_submit_button("Edit")
                if edit_btn:
                    if not name:
                        st.error("All fields are required")
                    else:
                        edited = False
                        with st.spinner(""):
                            edited = edit_user(edit_select[0], name, sex)
                        if edited:
                            success = st.success("User edited successfully")
                            time.sleep(1.5)
                            success.empty()
                            st.experimental_rerun()
                        else:
                            st.error("Something went wrong")
        else:
            st.write("No user available")
    with c3:
        st.subheader("Block / Unblock a user")
        if not users:
            st.write("No user available")
        else:
            with st.form("block-unblock"):
                selected_user = st.selectbox(
                    "Select a user", options=users, format_func=lambda x: x[1])
                _, __ = st.columns(2)
                with _:
                    action = st.radio("Choose an action", options=[
                        "block", "unblock"], horizontal=True)
                submit = st.form_submit_button("Confirm")
                if submit:
                    if action == "block":
                        activity = f"You blocked the user '{selected_user[1]}'"
                        val = 0
                    else:
                        val = 1
                        activity = f"You unblocked the user '{selected_user[1]}'"

                    block_unblock_user(selected_user[0], val)
                    add_history(activity)

                    # retrieve_users_(st.session_state["order_col_user"], st.session_state["order_type_user"])
                    st.success("Operation completed successfully")
                    time.sleep(0.5)
                    st.experimental_rerun()
    st.divider()

    co1, co2 = st.columns(2)
    with co1:
        st.subheader("New messages")
        if not new_messages:
            st.write("you dont have any new message 🗑️")
        else:
            for new_message in new_messages:
                col1, col2 = st.columns([2, 1])
                with col1:
                    with st.expander(new_message[3]):

                        st.write(
                            f"<p class='message-title'><span>From</span> : {new_message[1]}</p>", unsafe_allow_html=True)
                        st.write(
                            f"<p class='message-title'><span>Email</span> : {new_message[2]}</p>", unsafe_allow_html=True)
                        st.write(
                            f"<p class='message-title'><span>Content</span> : {new_message[4]}</p>", unsafe_allow_html=True)
                        st.write(
                            f"<p class='message-title'><span>Date</span> : {new_message[-1]}</p>", unsafe_allow_html=True)
                        st.markdown(" ")

                        _, __, ___ = st.columns([2, 1, 1])
                        with _:
                            mark_read = st.button(
                                "Mark as read", key=f"mark-msg-read {new_message[0]}", use_container_width=True)
                            if mark_read:
                                mark_as_read(new_message[0])
                                retrieve_messages()
                                st.experimental_rerun()
                        with __:
                            delete_btn = st.button(
                                "Delete", key=f"delete-msg-new {new_message[0]}")
                            if delete_btn:
                                delete_single_message(new_message[0])
                                retrieve_messages()
                                st.experimental_rerun()
            # with col2:
            #     c1, c2 = st.columns(2)

            #     with c1:
            #         is_read = message[5] == 1
            #         read_btn = st.button("Mark as read", key=f'read_btn {message[0]}', disabled=is_read)
            #         if read_btn:
            #             mark_as_read(message[0])
            #             retrieve_messages()
            #             st.experimental_rerun()
    with co2:
        st.subheader("Seen messages")
        if not seen_messages:
            st.write("you dont have any message 🗑️")
        else:
            for message in seen_messages:
                col1, col2 = st.columns([2, 1])
                with col1:
                    with st.expander(message[3]):

                        st.write(
                            f"<p class='message-title'><span>From</span> : {message[1]}</p>", unsafe_allow_html=True)
                        st.write(
                            f"<p class='message-title'><span>Email</span> : {message[2]}</p>", unsafe_allow_html=True)
                        st.write(
                            f"<p class='message-title'><span>Content</span> : {message[4]}</p>", unsafe_allow_html=True)
                        st.write(
                            f"<p class='message-title'><span>Date</span> : {message[-1]}</p>", unsafe_allow_html=True)
                        st.markdown(" ")
                        delete_btn = st.button(
                            "Delete", key=f"delete-msg-old{message[0]}")
                        if delete_btn:
                            delete_single_message(message[0])
                            retrieve_messages()
                            st.experimental_rerun()
            st.markdown(" ")
            delete_all = st.button("Delete all", key="delete-all-old-btn")
            if delete_all:
                delete_all_messages()
                retrieve_messages()
                st.experimental_rerun()
    st.divider()
    st.subheader("Feedbacks")
    ratings = st.session_state["ratings"]

    ratings_df = pd.DataFrame(ratings, columns=[
        "Id", "User", "Rating", "Comment", "Date", ])

    ratings_df = ratings_df.style.set_properties(
        **{'text-align': 'left'}).set_table_styles(styles)
    col1, col2 = st.columns(2)
    with col1:
        st.table(ratings_df)
    # st.markdown('''
    #         <style>
    #             div[data-testid="stMarkdownContainer"] > p {

    #                 font-size: 1.4rem;
    #             }
    #             .message-title > span{
    #                 text-decoration: underline;
    #                 color: #265B94
    #             }

    #         </style>
    #     ''', unsafe_allow_html=True)
    # st.markdown("""
    # <style>
    #     p{
    #         font-size: 2rem;
    #         font-weight: bold;
    #     }
    #     </style>
    # """, unsafe_allow_html=True)

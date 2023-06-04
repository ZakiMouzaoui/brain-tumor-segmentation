import time
from db_manager import (
    edit_user, retrieve_users, view_all_patients,
    #   get_pending_requests,
    #     approve_deny_request,
    block_unblock_user,
    get_messages,
    mark_as_read,
    add_history,
    paginate_users,
    delete_single_message,
    add_notification,
    delete_all_messages,
    create_user
)
import streamlit as st
from streamlit_card import card
import pandas as pd
import streamlit_nested_layout
import re
# from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridUpdateMode
# from st_aggrid.grid_options_builder import GridOptionsBuilder


def dashboard_page():
    def validate_email(email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        return re.fullmatch(regex, email)

    def retrieve_users_(order_col, order_type):
        n = retrieve_users()
        items_per_page = 3

        # Calculate the total number of pages
        total_pages = n // items_per_page

        if n % items_per_page != 0:
            total_pages += 1

        # Initialize the current page
        current_page = st.session_state["current_page"]
        start_index = (current_page - 1) * items_per_page

        users = paginate_users(order_col, order_type,
                               items_per_page, start_index)
        st.session_state["users"] = users
        st.session_state["total_pages"] = total_pages

        return users

    def retrieve_patients_(order_col, order_type):
        patients = view_all_patients(order_col, order_type)
        st.session_state["patients"] = patients
        return patients

    # def retrieve_pending_requests():
    #     requests = get_pending_requests()
    #     st.session_state["requests"] = requests
    #     return requests

    def retrieve_messages():
        all_messages = get_messages()
        st.session_state["all_messages"] = all_messages

    st.markdown("<h1 style='text-align: center'>Dashboard 🖥️</h1>",
                unsafe_allow_html=True)

    if not "requests" in st.session_state:
        st.session_state["order_user"] = "Name (A-Z)"
        st.session_state["order_col_user"] = "name"
        st.session_state["order_type_user"] = "ASC"

        st.session_state["order_patient"] = "Name (A-Z)"
        st.session_state["order_col_patient"] = "name"
        st.session_state["order_type_patient"] = "ASC"

        st.session_state["current_page"] = 1
        # retrieve_pending_requests()
        retrieve_messages()

        retrieve_patients_(
            st.session_state["order_col_patient"], st.session_state["order_type_patient"])
        retrieve_users_(st.session_state["order_col_user"],
                        st.session_state["order_type_user"])
    users = st.session_state["users"]
    patients = st.session_state["patients"]
    # requests = st.session_state["requests"]
    all_messages = st.session_state["all_messages"]
    doctors = list(filter(lambda x: x[4] == 1, users))
    staffs = list(filter(lambda x: x[4] == 2, users))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        card(
            title="Doctors",
            text=f"{len(doctors)}",
            image="https://img.freepik.com/premium-vector/avatar-male-doctor-with-black-hair-beard-doctor-with-stethoscope-vector-illustrationxa_276184-32.jpg?w=2000",
            url=""
        )

    with col2:
        card(
            title="Staffs",
            text=f"{len(staffs)}",
            image="https://banner2.cleanpng.com/20191121/lkg/transparent-staff-icon-hotel-icon-service-icon-5dd63a2248cce4.9645499215743206742982.jpg",
            url=""
        )

    with col3:
        card(
            title="Patients",
            text=f"{len(patients)}",
            image="https://cdn3.iconfinder.com/data/icons/corona-pandemic-disease/512/005-patient-512.png",
            url="",
        )
    new_messages = list(filter(lambda x: x[5] == 0, all_messages))
    seen_messages = list(filter(lambda x: x[5] == 1, all_messages))

    with col4:
        card(
            title="New Messages",
            text=f"{len(new_messages)}",
            image="https://img.uxwing.com/wp-content/themes/uxwing/download/communication-chat-call/text-message-icon.png",
            url=""
        )

    cc1, cc2 = st.columns(2)

    with cc1:
        _, __ = st.columns(2)
        with _:
            order_user = st.selectbox("Sort users by", options=[
                                      "Name(A-Z)", "Name(Z-A)", "Date ⬆️", "Date ⬇️"])
            if order_user == "Name(A-Z)":
                st.session_state["order_col_user"] = "name"
                st.session_state["order_type_user"] = "ASC"

            elif order_user == "Name(Z-A)":
                st.session_state["order_col_user"] = "name"
                st.session_state["order_type_user"] = "DESC"

            elif order_user == "Date ⬆️":
                st.session_state["order_col_user"] = "created_at"
                st.session_state["order_type_user"] = "ASC"

            else:
                st.session_state["order_col_user"] = "created_at"
                st.session_state["order_type_user"] = "DESC"

            retrieve_users_(st.session_state["order_col_user"],
                            st.session_state["order_type_user"])

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

        # users = retrieve_users_(st.session_state["order_col_user"], st.session_state["order_type_user"])
        users_df = pd.DataFrame(
            users, columns=["Id", "Name", "Sex", "Email", "Role", "Status", "Joining date"])
        # users_df.drop("Id", inplace=True, axis=1)
        users_df['Status'] = users_df['Status'].replace(
            {0: 'Blocked', 1: 'Active'})
        users_df['Sex'] = users_df['Sex'].replace({"Male": 'M', "Female": 'F'})
        users_df['Role'] = users_df['Role'].replace({1: 'Doctor', 2: 'Staff'})
        users_df = users_df.style.set_properties(
            **{'text-align': 'left'}).set_table_styles(styles)

        st.subheader("Users")
        st.table(users_df)

        co1, co2 = st.columns(2)

        with co1:
            cc_1, cc_2, cc_3 = st.columns(3)
            current_page = st.session_state["current_page"]
            total_pages = st.session_state["total_pages"]

            with cc_1:
                if current_page > 1:
                    if st.button("Previous"):
                        current_page -= 1
                        st.session_state["current_page"] = current_page
                        st.experimental_rerun()
                else:
                    st.button("Previous", disabled=True)

            with cc_2:
                st.write(f"Page {current_page} of {total_pages}")
            with cc_3:
                if current_page < total_pages:
                    if st.button("Next"):
                        current_page += 1
                        st.session_state["current_page"] = current_page
                        st.experimental_rerun()
                else:
                    st.button("Next", disabled=True)

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
        patients_df = pd.DataFrame(patients, columns=[
                                   "Id", "Name", "Sex", "Age", "User Id", "Assigned to", "Joining date", ])
        patients_df.drop('User Id', inplace=True, axis=1)

        _, __ = st.columns(2)
        with _:
            order_patient = st.selectbox("Sort patients by", options=[
                                         "Name(A-Z)", "Name(Z-A)", "Date ⬆️", "Date ⬇️"])
            if order_patient == "Name(A-Z)":
                st.session_state["order_col_patient"] = "name"
                st.session_state["order_type_patient"] = "ASC"

            elif order_patient == "Name(Z-A)":
                st.session_state["order_col_patient"] = "name"
                st.session_state["order_type_patient"] = "DESC"

            elif order_patient == "Date ⬆️":
                st.session_state["order_col_patient"] = "created_at"
                st.session_state["order_type_patient"] = "ASC"

            else:
                st.session_state["order_col_patient"] = "created_at"
                st.session_state["order_type_patient"] = "DESC"

        patients_df = patients_df.style.set_properties(
            **{'text-align': 'left'}).set_table_styles(styles)

        st.subheader("Patients")
        st.table(patients_df)
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
                        retrieve_users_(
                            st.session_state["order_col_user"], st.session_state["order_type_user"])
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

    # st.divider()
    # co1, _ = st.columns(2)
    # with co1:
    #     requests_df = pd.DataFrame(requests, columns=["Id","Name", "Sex", "Age", "Tumor", "user_id", "Requested by", "Date"])
    #     requests_df.drop("user_id", inplace=True, axis=1)
    #     #requests_df = requests_df.style.set_properties(**{'text-align': 'left'}).set_table_styles(styles)

    #     st.subheader("Pending requests")
    #     st.table(requests_df)

    # with _:
    #     st.subheader("Accept / Refuse a request")

    #     if requests:
    #         disabled_req = False
    #     else:
    #         disabled_req = True
    #     with st.form("approve-reject"):
    #         selected_request = st.selectbox("Select a request", options=requests, format_func=lambda x: f"Request #{x[0]}")
    #         __, _ = st.columns(2)
    #         with __:
    #             action = st.radio("Choose an action", options=["approve", "reject"], horizontal=True)
    #             submit_ = st.form_submit_button("Confirm", disabled= disabled_req)

    #             if submit_:
    #                 if action == "approve":
    #                     approve_deny_request(selected_request[0], 1)
    #                     add_notification(selected_request[5], selected_request[0], "Request approved", f"Your request for the patient {selected_request[1]} has been approved")
    #                 else:
    #                     approve_deny_request(selected_request[0], 0)
    #                     add_notification(selected_request[5], selected_request[0], "Request rejected", f"Your request for the patient {selected_request[1]} has been rejected")

    #                 st.success("Operation completed successfully")
    #                 time.sleep(0.5)
    #                 st.experimental_rerun()

    st.divider()
    # st.subheader("Messages")

    # if not all_messages:
    #     st.write("You dont have any message 🗑️")
    # else:
    #     for message in all_messages:
    #         col1, col2 = st.columns([2,1])
    #         with col1:
    #             with st.expander(message[3]):
    #                 st.write(f"<p class='message-title'><span>From</span> : {message[1]}</p>", unsafe_allow_html=True)
    #                 st.write(f"<p class='message-title'><span>Email</span> : {message[2]}</p>", unsafe_allow_html=True)
    #                 st.write(f"<p class='message-title'><span>Content</span> : {message[4]}</p>", unsafe_allow_html=True)

    #         with col2:
    #             c1, c2 = st.columns(2)

    #             with c1:
    #                 is_read = message[5] == 1
    #                 read_btn = st.button("Mark as read", key=f'read_btn {message[0]}', disabled=is_read)
    #                 if read_btn:
    #                     mark_as_read(message[0])
    #                     retrieve_messages()
    #                     st.experimental_rerun()
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
                        st.markdown(" ")

                        _, __ = st.columns(2)
                        with _:
                            mark_read = st.button(
                                "Mark as read", key=f"mark-msg-read {new_message[0]}")
                            if mark_read:
                                mark_as_read(new_message[0])
                                st.experimental_rerun()
                        with __:
                            delete_btn = st.button(
                                "Delete", key=f"delete-msg-new {new_message[0]}")
                            if delete_btn:
                                delete_single_message(new_message[0])
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
                        st.markdown(" ")
                        delete_btn = st.button(
                            "Delete message", key=f"delete-msg-old{message[0]}")
                        if delete_btn:
                            delete_single_message(message[0])
                            st.experimental_rerun()
            st.markdown(" ")
            delete_all = st.button("Delete all", key="delete-all-old-btn")
            if delete_all:
                delete_all_messages()
                st.experimental_rerun()

    st.markdown('''
            <style>
                div[data-testid="stMarkdownContainer"] > p {
                
                    font-size: 1.4rem;
                }
                .message-title > span{
                    text-decoration: underline;
                    color: #265B94
                }
                
            </style>
        ''', unsafe_allow_html=True)

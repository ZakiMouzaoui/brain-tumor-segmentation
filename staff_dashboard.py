import datetime
import time
from db_manager import (
    retrieve_users, view_all_patients,
    add_history,
    paginate_users,
    add_patient,
    edit_patient,
    delete_patient,
    add_appointment,
    get_appointments,
    add_notification,
)
import streamlit as st
from streamlit_card import card
import pandas as pd
import streamlit_nested_layout


def staff_dashboard():
    def check_valid_appointment_date(date):
        return date >= datetime.date.today()

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

    def retrieve_appointments():
        appointments = get_appointments()
        st.session_state["appointments"] = appointments
        return appointments

    if not "appointments" in st.session_state:
        st.session_state["order_user"] = "Name (A-Z)"
        st.session_state["order_col_user"] = "name"
        st.session_state["order_type_user"] = "ASC"

        st.session_state["order_patient"] = "Name (A-Z)"
        st.session_state["order_col_patient"] = "name"
        st.session_state["order_type_patient"] = "ASC"

        st.session_state["current_page"] = 1

    retrieve_users_(
        st.session_state["order_col_user"], st.session_state["order_type_user"])
    retrieve_patients_(
        st.session_state["order_col_patient"], st.session_state["order_type_patient"])
    retrieve_appointments()

    users = st.session_state["users"]
    patients = st.session_state["patients"]
    appointments = st.session_state["appointments"]

    users = list(filter(lambda x: x[4] == 1, users))

    st.markdown("<h1 style='text-align: center'>Dashboard 🖥️</h1>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        card(
            title="Doctors",
            text=f"{len(users)}",
            image="https://img.freepik.com/premium-vector/avatar-male-doctor-with-black-hair-beard-doctor-with-stethoscope-vector-illustrationxa_276184-32.jpg?w=2000",
            url=""
        )

    with col2:
        card(
            title="Patients",
            text=f"{len(patients)}",
            image="https://cdn3.iconfinder.com/data/icons/corona-pandemic-disease/512/005-patient-512.png",
            url="",
        )

    with col3:
        card(
            title="Appointments",
            text=f"{len(appointments)}",
            image="https://static.vecteezy.com/system/resources/previews/003/738/383/original/appointment-date-icon-free-vector.jpg",
            url="",
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
        users_df.drop("Role", axis=1, inplace=True)
        users_df['Status'] = users_df['Status'].replace(
            {0: 'Blocked', 1: 'Active'})
        users_df['Sex'] = users_df['Sex'].replace({"Male": 'M', "Female": 'F'})

        users_df = users_df.style.set_properties(
            **{'text-align': 'left'}).set_table_styles(styles)

        st.subheader("Doctors")
        st.table(users_df)

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

    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Add a patient")
        with st.form("patient-add-form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            age = st.number_input("Age", min_value=18,
                                  max_value=100, value=50, step=1, format="%d")
            sex = st.selectbox("Sex", options=["Male", "Female"])
            doctor_assigned = st.selectbox(
                "Assign to doctor", options=users, format_func=lambda x: x[1])

            add_btn = st.form_submit_button("Add")
            if add_btn:
                if not name or not email:
                    st.error("All fields are required")
                else:

                    created = add_patient(
                        doctor_assigned[0], name, email, sex, age)
                    if not created:
                        st.error("Something went wrong")
                    else:
                        st.session_state["success"] = True
                        # retrieve_patients_(
                        #     st.session_state["order_col_patient"], st.session_state["order_type_patient"])
                        st.experimental_rerun()
            if "success" in st.session_state and st.session_state["success"] is not None:
                st.session_state["success"] = None
                st.success("Patient added successfully")

    with col2:
        st.subheader("Edit a patient")
        if not patients:
            st.write("No patients to edit")
        else:
            selected_patient_edit = st.selectbox(
                "Select a patient", options=patients, format_func=lambda x: x[1])
            with st.form("edit-form"):
                name = st.text_input("Name", value=selected_patient_edit[1])
                age = st.number_input("Age", min_value=18, max_value=100,
                                      value=selected_patient_edit[3], step=1, format="%d")
                sex = st.selectbox("Sex", options=["Male", "Female"])

                edit_btn = st.form_submit_button("Edit")
                if edit_btn:
                    if not name or not age:
                        st.error("All fields are required")
                    else:
                        edited = edit_patient(
                            selected_patient_edit[0], name, sex, age)
                        if not edited:
                            st.error("Something went wrong")
                        else:
                            st.success("Patient edited successfully")
                            # retrieve_patients_(
                            #     st.session_state["order_col_patient"], st.session_state["order_type_patient"])
                            st.experimental_rerun()
    with col3:
        st.subheader("Delete a patient")
        if not patients:
            st.write("No patients to edit")
        else:
            selected_patient_delete = st.selectbox(
                "Select a patient", key="delete-selectbox", options=patients, format_func=lambda x: x[1])
            delete_btn = st.button("Delete")
            if delete_btn:
                delete_patient(selected_patient_delete[0])
                # retrieve_patients_(
                #     st.session_state["order_col_patient"], st.session_state["order_type_patient"])
                # retrieve_appointments()
                st.experimental_rerun()

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Appointments")
        appointments_df = pd.DataFrame(appointments, columns=[
                                       "Id", "Patient name", "Doctor name", "Date", "Status", ])
        appointments_df["Status"] = appointments_df["Status"].replace(
            {0: 'Pending', 1: 'Confirmed', 2: "Canceled"})

        _, __ = st.columns(2)
        with _:
            order_patient = st.selectbox("Sort appointments by", options=[
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

        appointments_df = appointments_df.style.set_properties(
            **{'text-align': 'left'}).set_table_styles(styles)

        st.subheader("appointments")
        st.table(appointments_df)
    with col2:
        st.subheader("Create an appointment")
        with st.form("appointment-for"):
            patient_select = st.selectbox(
                "Select patient", options=patients, format_func=lambda x: x[1])
            doctor_select = st.selectbox(
                "Select doctor", options=users, format_func=lambda x: x[1])
            date = st.date_input("Appointment date")

            add = st.form_submit_button(
                "Create", disabled=patient_select is None or doctor_select is None)
            if add:
                if not check_valid_appointment_date(date):
                    st.error("Please enter a valid date")
                else:
                    add_appointment(patient_select[0], doctor_select[0], date)
                    st.session_state["appointment-success"] = True
                    # retrieve_appointments()
                    st.experimental_rerun()
            if "appointment-success" in st.session_state and st.session_state["appointment-success"] is not None:
                st.session_state["appointment-success"] = None
                st.success("Appointment added")
    # st.markdown("""
    #     <style>
    #         button.css-19j7fr0.edgvbvh10{
    #             background-color: #d11a2a;
    #             border-color: #d11a2a;
    #             color: white
    #         }
    #     </style>
    # """, unsafe_allow_html=True)

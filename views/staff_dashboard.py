import base64
import datetime
from db_manager import (
    retrieve_users,
    view_all_patients,
    add_history,
    add_patient,
    edit_patient,
    delete_patient,
    add_appointment,
    get_appointments,
    delete_appointment
)
import streamlit as st
from streamlit_card import card
import pandas as pd
import streamlit_nested_layout


def staff_dashboard():
    def check_valid_appointment_date(date):
        return date >= datetime.date.today()

    # def retrieve_users_(order_col, order_type):

    #     n = retrieve_users()
    #     items_per_page = 3

    #     # Calculate the total number of pages
    #     total_pages = n // items_per_page

    #     if n % items_per_page != 0:
    #         total_pages += 1

    #     # Initialize the current page
    #     current_page = st.session_state["current_page"]
    #     start_index = (current_page - 1) * items_per_page

    #     users = paginate_users(order_col, order_type,
    #                            items_per_page, start_index)
    #     st.session_state["users"] = users
    #     st.session_state["total_pages"] = total_pages

    #     return users

    def retrieve_users_():
        users = retrieve_users()
        return users

    def retrieve_patients_(order_col, order_type):
        patients = view_all_patients(order_col, order_type)
        # st.session_state["patients"] = patients
        return patients

    def retrieve_appointments():
        appointments = get_appointments()
        # st.session_state["staff_appointments"] = appointments
        return appointments

    def filter_appointments(l, filter_):
        if filter_ != -1:
            l = list(filter(
                lambda x: x[-1] == filter_, l))
        return l

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
    def get_base64_appointment(bin_file):
        with open(bin_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    if not "staff-appointments" in st.session_state:
        # st.session_state["order_user"] = "Name (A-Z)"
        # st.session_state["order_col_user"] = "name"
        # st.session_state["order_type_user"] = "ASC"

        # st.session_state["order_patient"] = "Name (A-Z)"
        # st.session_state["order_col_patient"] = "name"
        # st.session_state["order_type_patient"] = "ASC"

        # st.session_state["current_page"] = 1
        st.session_state["users"] = retrieve_users_()
        st.session_state["patients"] = view_all_patients()
    st.session_state["staff-appointments"] = retrieve_appointments()

    # retrieve_users_(
    #     st.session_state["order_col_user"], st.session_state["order_type_user"])
    # retrieve_patients_(
    #     st.session_state["order_col_patient"], st.session_state["order_type_patient"])
    # retrieve_appointments()

    users = st.session_state["users"]
    patients = st.session_state["patients"]
    appointments = st.session_state["staff-appointments"]
    users = list(filter(lambda x: x[4] == 1, users))
    filtered_appointments = appointments.copy()

    st.markdown("<h1 style='text-align: center'>Dashboard</h1>",
                unsafe_allow_html=True)

    # col1, col2, col3 = st.columns(3)

    # with col1:
    #     card(
    #         title="Doctors",
    #         text=f"{len(users)}",
    #         image="https://img.freepik.com/premium-vector/avatar-male-doctor-with-black-hair-beard-doctor-with-stethoscope-vector-illustrationxa_276184-32.jpg?w=2000",
    #         url=""
    #     )

    # with col2:
    #     card(
    #         title="Patients",
    #         text=f"{len(patients)}",
    #         image="https://cdn3.iconfinder.com/data/icons/corona-pandemic-disease/512/005-patient-512.png",
    #         url="",
    #     )

    # with col3:
    #     card(
    #         title="Appointments",
    #         text=f"{len(appointments)}",
    #         image="https://static.vecteezy.com/system/resources/previews/003/738/383/original/appointment-date-icon-free-vector.jpg",
    #         url="",
    #     )

    doctor_img = get_base64_doctor("assets/doctor_icon.png")
    patient_img = get_base64_patient("assets/patient_icon.png")
    appointment_img = get_base64_appointment("assets/appointment.jpg")

    st.write(f"""
        <div class="cards-list">
            <div class="card 1">
                <div class="card_image"> <img src="data:image/png;base64,{doctor_img}" /> </div>
                <div class="card_title">
                    Doctors
                    <div class="card-subtitle">{len(users)}</div>
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
                <div class="card_image"> <img src="data:image/png;base64,{appointment_img}" /> </div>
                <div class="card_title">
                    Appointments
                    <div class="card-subtitle">{len(appointments)}</div>
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
    cc1, cc2 = st.columns(2)

    with cc1:
        _, __ = st.columns(2)
        with _:
            order_user = st.selectbox("Sort users by", options=[
                                      "Name(A-Z)", "Name(Z-A)", "Date ⬆️", "Date ⬇️"])
            if order_user == "Name(A-Z)":
                # st.session_state["order_col_user"] = "name"
                # st.session_state["order_type_user"] = "ASC"
                users = sorted(users, key=lambda x: x[1])

            elif order_user == "Name(Z-A)":
                # st.session_state["order_col_user"] = "name"
                # st.session_state["order_type_user"] = "DESC"
                users = sorted(users, key=lambda x: x[1], reverse=True)

            elif order_user == "Date ⬆️":
                # st.session_state["order_col_user"] = "created_at"
                # st.session_state["order_type_user"] = "ASC"
                users = sorted(users, key=lambda x: x[-1])

            else:
                # st.session_state["order_col_user"] = "created_at"
                # st.session_state["order_type_user"] = "DESC"
                users = sorted(users, key=lambda x: x[-1], reverse=True)

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
        _, __ = st.columns(2)
        with _:
            order_patient = st.selectbox("Sort patients by", options=[
                                         "Name(A-Z)", "Name(Z-A)", "Date ⬆️", "Date ⬇️"])
            if order_patient == "Name(A-Z)":
                patients = sorted(patients, key=lambda x: x[1])

            elif order_patient == "Name(Z-A)":
                patients = sorted(patients, key=lambda x: x[1], reverse=True)

            elif order_patient == "Date ⬆️":
                patients = sorted(patients, key=lambda x: x[-1])

            else:
                patients = sorted(patients, key=lambda x: x[-1], reverse=True)
        patients_df = pd.DataFrame(patients, columns=[
                                   "Id", "Name", "Email", "Sex", "Age", "User Id", "Assigned to", "Joining date", ])
        patients_df.drop('User Id', inplace=True, axis=1)
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
                    created = False
                    with st.spinner(""):
                        created = add_patient(
                            doctor_assigned[0], name, email, sex, age)

                    if not created:
                        st.error("Something went wrong")
                    else:
                        st.session_state["success"] = True
                        # retrieve_patients_(
                        # st.session_state["order_col_patient"], st.session_state["order_type_patient"])
                        st.session_state["patients"] = view_all_patients()

                        st.experimental_rerun()
            if "success" in st.session_state and st.session_state["success"] is not None:
                st.session_state["success"] = None
                st.success("Patient added successfully")
                staff_name = st.session_state["user_name"]
                add_history(
                    f'The patient "{name}" is added by {staff_name}')

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
                                      value=selected_patient_edit[4], step=1, format="%d")
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
                            st.session_state["edit-success"] = True
                            st.session_state["patients"] = view_all_patients()

                            st.experimental_rerun()
                if "edit-success" in st.session_state and st.session_state["edit-success"] is not None:
                    st.success("Patient edited successfully")
                    st.session_state["edit-success"] = None
                    staff_name = st.session_state["user_name"]
                    add_history(
                        f'The patient "{name}" is edited by {staff_name}')
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
                staff_name = st.session_state["user_name"]
                add_history(f'The patient "{name}" is deleted by {staff_name}')
                st.session_state["patients"] = view_all_patients()
                st.experimental_rerun()

    st.divider()
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        st.subheader("Appointments")
        _, __ = st.columns(2)
        with _:
            filter_ = st.selectbox("Filter appointments", options=[
                -1, 0, 1, 2], format_func=lambda x: "Pending" if x == 0 else "Confirmed" if x == 1 else "Canceled" if x == 2 else "All")
            filtered_appointments = filter_appointments(
                filtered_appointments, filter_)

        appointments_df = pd.DataFrame(filtered_appointments, columns=[
                                       "Id", "Patient", "Doctor", "Date", "Status", ])
        appointments_df["Status"] = appointments_df["Status"].replace(
            {0: 'Pending', 1: 'Confirmed', 2: "Canceled"})
        appointments_df = appointments_df.style.set_properties(
            **{'text-align': 'left'}).set_table_styles(styles)

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
                st.success("Appointment created")
    with col3:
        st.subheader("Delete an appointment")
        selected_appointment = st.selectbox(
            "Select an appointment", options=appointments, label_visibility="collapsed", format_func=lambda x: f"Appointment #{x[0]}" if x[0] != "Select" else "Select")
        with st.form("delete-appointment"):
            st.text_input("Patient", selected_appointment[1], disabled=True)
            st.text_input("Doctor", selected_appointment[2], disabled=True)
            st.text_input("Date", selected_appointment[3], disabled=True)
            delete_appointment_btn = st.form_submit_button("Delete")

            if delete_appointment_btn:
                delete_appointment(selected_appointment[0])
                st.session_state["appointment-deleted"] = True
                st.experimental_rerun()

            if "appointment-deleted" in st.session_state and st.session_state["appointment-deleted"] is not None:
                st.session_state["appointment-deleted"] = None
                st.success("Appointment deleted")

    if st.session_state["theme"] == "dark":
        st.write('''
                            <style>
                                input:disabled, label{
                                    -webkit-text-fill-color: white !important;

                                }

                            </style>
                        ''', unsafe_allow_html=True)
    else:
        st.write('''
                        <style>
                            input:disabled, label{
                                -webkit-text-fill-color: #31333F !important;

                            }

                        </style>
                    ''', unsafe_allow_html=True)

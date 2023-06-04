import glob
import json
import streamlit as st
from db_manager import get_appointments_for_patient, edit_appointment, get_medical_records_for_patient
import pandas as pd
import matplotlib.pyplot as plt
from skimage import transform
from matplotlib.cm import get_cmap
import nibabel as nib


def appointments_page():
    def plot_seg(segment, cmap_val="viridis", ):
        # seg = st.session_state["prediction"]
        angle = 90

        cols = 5
        rows = 4
        fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(5, 4))
        idx = 0

        cmap = get_cmap(cmap_val)

        for i in range(rows):
            for j in range(cols):
                axes[i, j].imshow(transform.rotate(
                    segment[idx, :, :], angle=angle), cmap=cmap)
                axes[i, j].axis("off")
                idx += 1

        # legend_patches = [mpatches.Patch(color=cmap(
        #     i / (len(class_labels) - 1)), label=label) for i, label in enumerate(class_labels)]
        # plt.legend(handles=legend_patches, loc="upper right", fontsize=6.5)
        return fig

    id = st.session_state["user_id"]

    def get_medical_records():
        records = get_medical_records_for_patient(st.session_state["user_id"])
        st.session_state["patient_records"] = records

    def retrieve_appointments():
        appointments = get_appointments_for_patient(id)
        st.session_state["appointments"] = appointments

    st.markdown("<h1 style='text-align: center'>Medical Record 📝</h1>",
                unsafe_allow_html=True)
    st.markdown(" ")

    if not "patient_records" in st.session_state:
        get_medical_records()
        retrieve_appointments()

    records = st.session_state["patient_records"]
    appointments = st.session_state["appointments"]

    appointments_df = pd.DataFrame(appointments, columns=[
        "Id", "Doctor name", "Date", "Status", ])
    appointments_df["Status"] = appointments_df["Status"].replace({
        0: "Pending", 1: "Confirmed", 2: "Canceled"
    })
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
    appointments_df = appointments_df.style.set_properties(
        **{'text-align': 'left', 'padding': '0.3rem'}).set_table_styles(styles)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("MRI results")
        fig = plot_seg(
            nib.load(glob.glob(f"uploads/{id}/segmentation/*")[0]).get_fdata())
        st.pyplot(fig)
    with col2:
        st.subheader("Tumor informations")
        st.markdown("<div class='tumor-info'>", unsafe_allow_html=True)
        st.markdown(
            f"<h5> Tumor type : {records[2]}</h5>", unsafe_allow_html=True)

        for k, v in json.loads(records[3]).items():
            st.markdown(f"""<h5>{k} :  {v}</h5>""",
                        unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("""
                <style>

                </style>
            """, unsafe_allow_html=True)

    st.divider()
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader("appointments")
        st.table(appointments_df)
    with col2:
        st.subheader("Confirm / Cancel")
        filtered = list(filter(lambda x: x[-1] == 0, appointments))
        if filtered:
            with st.form("cancel-confirm"):
                selected = st.selectbox(
                    "Select an appointment", options=filtered, format_func=lambda x: f'Appointment #{x[0]}')
                st.text_input("Doctor name", value=selected[1], disabled=True)
                st.text_input("Date", value=selected[2], disabled=True)

                option = st.radio("_", options=["Confirm", "Cancel"],
                                  horizontal=True, label_visibility="collapsed")
                if option == "Confirm":
                    val = 1
                else:
                    val = 2
                submit = st.form_submit_button("Submit")
                if submit:
                    edit_appointment(selected[0], val)
                    retrieve_appointments()
        else:
            st.write("No pending appointments")

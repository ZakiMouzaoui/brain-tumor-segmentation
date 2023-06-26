import glob
import json
import os
import streamlit as st
from db_manager import get_appointments_for_patient, edit_appointment, get_medical_records_for_patient
import pandas as pd
import matplotlib.pyplot as plt
from skimage import transform
from matplotlib.cm import get_cmap
import nibabel as nib
from fpdf import FPDF
import cv2
import numpy as np


def appointments_page():
    def create_slices(inp):
        res = np.zeros((240, 240, 20))

        start_slice = 60
        step = 2
        num_slices = 20

        for i in range(num_slices):
            slice_index = start_slice + i * step
            res[:, :, i] = inp[:, :, slice_index]
        return res

    def plot_seg(format, sequence, segment, cmap_val="viridis"):
        if format == "DICOM":
            angle = 90
            sequence = cv2.resize(sequence[:, :, :], (240, 240))
        else:
            angle = 270
            sequence = create_slices(sequence)

        cols = 5
        rows = 4
        fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(5, 4))
        idx = 0

        cmap = get_cmap(cmap_val)

        for i in range(rows):
            for j in range(cols):
                tumor_region = np.where(
                    segment[idx, :, :] > 0, segment[idx, :, :], np.nan)

                axes[i, j].imshow(transform.rotate(
                    sequence[:, :, idx], angle=angle), cmap="gray")
                axes[i, j].imshow(transform.rotate(
                    tumor_region, angle=angle), cmap=cmap)
                axes[i, j].axis("off")
                idx += 1
        return fig

    id = st.session_state["user_id"]

    def get_medical_records():
        records = get_medical_records_for_patient(st.session_state["user_id"])
        st.session_state["patient_records"] = records

    def retrieve_appointments():
        appointments = get_appointments_for_patient(id)
        st.session_state["appointments"] = appointments

    st.markdown("<h1 style='text-align: center'>Medical Record</h1>",
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

    co1, co2 = st.columns(2)
    with co1:
        st.markdown(
            "<h3 style='text-align:center'tumor>MRI results</h3>", unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        # with cc1:
        #     sequence = st.selectbox("Select a sequence", options=[
        #                             "T1", "T1(gadolinium)", "T2", "FLAIR"])
        with cc1:
            cmap = st.selectbox("Select a color type", options=[
                                "viridis", "rainbow", "ocean"], format_func=lambda x: 'Type1' if x == "viridis" else "Type2" if x == "rainbow" else "Type3")
        with cc2:

            st.image(f"assets/{cmap}-dark.png")

        seq = nib.load(
            glob.glob(f"uploads/{id}/results/t2_nii/*")[0]).get_fdata()

        fig = plot_seg(
            records[5],
            seq,
            nib.load(
                f"uploads/{id}/results/segmentation/segmentation.nii.gz").get_fdata(),
            cmap
        )
        st.pyplot(fig)
    with co2:

        st.markdown(
            "<h3 style='text-align:center'tumor>Tumor informations</h3>", unsafe_allow_html=True)
        # st.markdown("<div class='tumor-info'>",
        #             unsafe_allow_html=True)
        for i in range(4):
            st.markdown(" ")

        if records[3] == "HGG":
            type = "High Grade Glioma"
        else:
            type = "Low Grade Glioma"
        cc1, cc2 = st.columns(2)
        d = json.loads(records[4])
        keys_list = list(d.keys())
        keys_list_1 = keys_list[:3]
        keys_list_2 = keys_list[3:]
        helps = [
            "Shape elongation is a measure of how elongated or stretched an object is",
            "Shape flatness measures the degree to which an object is flat or two-dimensional",
            "This measurement represents the maximum diameter of the object in three-dimensional space",
            "Shape sphericity is a measure of how closely an object resembles a sphere.",
            "GLCM (Gray Level Co-occurrence Matrix) contrast is a texture feature that measures the local variations in gray-level intensities within an image.",
            "(Neighborhood Gray-Tone Difference Matrix) complexity is a texture feature that quantifies the complexity of textures within an image. It provides information about the variations in gray-level intensity differences between neighboring pixels in an image.",
            "NGTDM strength measures the strength of gray-level intensity changes in the neighborhood of each voxel within an image"
        ]

        with cc1:

            st.text_input("Tumor type", type, disabled=True)

            for idx, k in enumerate(keys_list_1):

                # st.markdown(f"""<h5 style='text-align:center'>{k} :  {v:.2f}  <i class="fa fa-question-circle" area-hidden="true"></i></h5>""",
                #        unsafe_allow_html=True)

                st.text_input(
                    k, value=d[k], key=k, disabled=True, help=helps[idx])

        with cc2:
            for idx, k in enumerate(keys_list_2):

                # st.markdown(f"""<h5 style='text-align:center'>{k} :  {v:.2f}  <i class="fa fa-question-circle" area-hidden="true"></i></h5>""",
                #        unsafe_allow_html=True)

                st.text_input(
                    k, value=d[k], key=k, disabled=True, help=helps[idx+3])

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
        col1, col2, _ = st.columns(3)
        with col2:
            if not os.path.exists(f"uploads/{id}/results/reports"):
                # st.session_state["reported"] = False
                os.makedirs(
                    f"uploads/{id}/reports")
                pdf = FPDF()

                # Add a page
                pdf.add_page()

                # set style and size of font
                # that you want in the pdf
                pdf.set_font("Arial", size=15)

                pdf.cell(200, 10, txt="Medical Record",
                         ln=1, align='C')

                # create a cell
                pdf.cell(200, 10, txt=f"Tumor type : {type}",
                         ln=1, align='C')

                for k, v in json.loads(id).items():
                    # add another cell
                    pdf.cell(200, 10, txt=f"{k} : {v}",
                             ln=2, align='C')
                pdf.output(
                    f"uploads/{id}/results/reports/report.pdf")

            with open(f"uploads/{id}/results/reports/report.pdf", "rb") as pdf_file:
                PDFbyte = pdf_file.read()

            st.download_button(
                label="Download as PDF",
                data=PDFbyte,
                file_name=f'{id} report.pdf',
                mime='text/pdf',
            )

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Appointments")
        st.table(appointments_df)

    with col2:
        _, __, _ = st.columns([1, 4, 1])
        with __:
            st.subheader("Confirm / Cancel")
            filtered = list(filter(lambda x: x[-1] == 0, appointments))
            if filtered:
                with st.form("cancel-confirm"):
                    selected = st.selectbox(
                        "Select an appointment", options=filtered, format_func=lambda x: f'Appointment #{x[0]}')
                    st.text_input(
                        "Doctor name", value=selected[1], disabled=True)
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
                        st.experimental_rerun()
                        # retrieve_appointments()
            else:
                st.write("No pending appointments")

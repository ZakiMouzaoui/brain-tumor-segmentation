import glob
import streamlit as st
from db_manager import get_appointments_for_doctor, get_medical_records_for_doctor
import pandas as pd
import matplotlib.pyplot as plt
from skimage import transform
from matplotlib.cm import get_cmap
import nibabel as nib
import json
import cv2
# plt2.style.use('dark_background')
import numpy as np
from fpdf import FPDF
import os


def stats_page():
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
        st.write(format)
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

    # def retrieve_patients():
    #     st.session_state["patients"] = view_patients(id)

    def retrieve_appointments():
        appointments = get_appointments_for_doctor(id)
        return appointments

    def filter_appointments(l, filter_):
        if filter_ != -1:
            l = list(filter(
                lambda x: x[-1] == filter_, l))
        return l

    def get_medical_records_():
        st.session_state["medical_records"] = get_medical_records_for_doctor(
            st.session_state["user_id"])

    st.markdown("<h1 style='text-align: center'>Patients</h1>",
                unsafe_allow_html=True)
    st.markdown(" ")

    if not "appointments" in st.session_state or st.session_state["appointments"] is None:
        appointments = retrieve_appointments()
        st.session_state["appointments"] = appointments

    get_medical_records_()

    col1, col2 = st.columns(2)
    patients = st.session_state["doctor-patients"]
    appointments = st.session_state["appointments"]
    records = st.session_state["medical_records"]

    with col1:
        _, __ = st.columns(2)
        with _:
            order_patient = st.selectbox("Sort patients by", options=[
                                         "Name(A-Z)", "Name(Z-A)", "Date ⬆️", "Date ⬇️"])
            if order_patient == "Name(A-Z)":
                # st.session_state["order_col_patient"] = "name"
                # st.session_state["order_type_patient"] = "ASC"
                st.session_state["doctor-patients"] = sorted(
                    patients, key=lambda x: x[1])
                patients = st.session_state["doctor-patients"]

            elif order_patient == "Name(Z-A)":
                # st.session_state["order_col_patient"] = "name"
                # st.session_state["order_type_patient"] = "DESC"
                st.session_state["doctor-patients"] = sorted(
                    patients, key=lambda x: x[1], reverse=True)
                patients = st.session_state["doctor-patients"]

            elif order_patient == "Date ⬆️":
                # st.session_state["order_col_patient"] = "created_at"
                # st.session_state["order_type_patient"] = "ASC"
                st.session_state["doctor-patients"] = sorted(
                    patients, key=lambda x: x[4])
                patients = st.session_state["doctor-patients"]

            else:
                # st.session_state["order_col_patient"] = "created_at"
                # st.session_state["order_type_patient"] = "DESC"
                st.session_state["doctor-patients"] = sorted(
                    patients, key=lambda x: x[4], reverse=True)
                patients = st.session_state["doctor-patients"]

        patients_df = pd.DataFrame(patients, columns=[
                                   "Id", "Name", "Sex", "Age", "Joining date"])
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

        patients_df_style = patients_df.style.set_properties(
            **{'text-align': 'left'}).set_table_styles(styles)

        st.subheader("Patients")
        st.table(patients_df_style)

    with col2:
        _, __ = st.columns(2)
        with _:
            filter_ = st.selectbox("Filter appointments", options=[
                -1, 0, 1, 2], format_func=lambda x: "Pending" if x == 0 else "Confirmed" if x == 1 else "Canceled" if x == 2 else "All")

            # st.session_state["appointments"] = filter_appointments(filter_)
            # st.session_state["filter"] = filter_
            # retrieve_appointments(st.session_state["filter"])
            appointments = filter_appointments(appointments, filter_)

        appointments_df = pd.DataFrame(appointments, columns=[
            "Id", "Patient name", "Doctor name", "Date", "Status", ])
        appointments_df["Status"] = appointments_df["Status"].replace({
            0: "Pending", 1: "Confirmed", 2: "Canceled"
        })
        appointments_df.drop(columns=["Doctor name"], axis=1, inplace=True)
        appointments_df = appointments_df.style.set_properties(
            **{'text-align': 'left'}).set_table_styles(styles)

        st.subheader("Appointments")
        st.table(appointments_df)
    st.divider()

    select_patients = patients.copy()
    select_patients.insert(0, ("Select", "Select"))

    st.markdown("<h3 style='text-align: center'>View a medical record</h3>",
                unsafe_allow_html=True)
    _, cc2, _ = st.columns([2, 1, 2])
    with cc2:
        selected_patient = st.selectbox(
            "Select a patient", options=select_patients, label_visibility="collapsed", format_func=lambda x: x[1] if x[0] != "Select" else "Select")
    if selected_patient[0] != "Select":
        record = list(
            filter(lambda x: x[1] == selected_patient[0], records))
        if record:
            record = record[0]

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
                    glob.glob(f"uploads/{selected_patient[0]}/results/t2_nii/*")[0]).get_fdata()
                fig = plot_seg(
                    record[5],
                    seq,
                    nib.load(
                        f"uploads/{selected_patient[0]}/results/segmentation/segmentation.nii.gz").get_fdata(),
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
                if record[3] == "HGG":
                    type = "High Grade Glioma"
                else:
                    type = "Low Grade Glioma"
                cc1, cc2 = st.columns(2)
                d = json.loads(record[4])
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
                col1, col2, col3 = st.columns(3)
                with col2:
                    if not os.path.exists(f"uploads/{selected_patient[0]}/results/reports"):
                        # st.session_state["reported"] = False
                        os.makedirs(
                            f"uploads/{selected_patient[0]}/results/reports")
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

                        for k, v in json.loads(record[4]).items():
                            # add another cell
                            pdf.cell(200, 10, txt=f"{k} : {v}",
                                     ln=2, align='C')
                        pdf.output(
                            f"uploads/{selected_patient[0]}/results/reports/report.pdf")

                    with open(f"uploads/{selected_patient[0]}/results/reports/report.pdf", "rb") as pdf_file:
                        PDFbyte = pdf_file.read()

                    st.download_button(
                        label="Download as PDF",
                        data=PDFbyte,
                        file_name=f'{selected_patient[1]} report.pdf',
                        mime='text/pdf',
                    )
        else:
            st.markdown(
                "<h3 style='text-align: center'>No medical record found for these patient </h3>", unsafe_allow_html=True)
    st.divider()
    st.subheader("Stats")
    ##########################################################################
    patients_count_by_sex = patients_df['Sex'].value_counts(
    ).reset_index()
    patients_count_by_sex.columns = ['Sex', 'Count']

    # Plot bar chart for count of patients by sex
    fig1 = plt.figure()
    plt.bar(patients_count_by_sex['Sex'], patients_count_by_sex['Count'], color=[
        "blue", "pink"])
    plt.xlabel('Sex', fontdict={"size": "15"})
    plt.ylabel('Count', fontdict={"size": "15"})
    plt.title('Count of Patients by Sex', fontdict={"size": "15"})
    plt.yticks(range(0, patients_count_by_sex['Count'].max() + 1))
    #########################################################################
    records_df = pd.DataFrame(records)
    fig2 = None
    fig3 = None

    if len(records_df) > 0:
        # tumor_types_count = records_df[2].value_counts().reset_index()
        # tumor_types_count.columns = ['tumor_type', 'count']

        # # Plot the bar chart
        # fig2 = plt.figure()
        # plt.bar(tumor_types_count['tumor_type'], tumor_types_count['count'], color=[
        #     "blue", "pink"])

        # plt.xlabel('Tumor Type', fontdict={"size": "20"})
        # plt.ylabel('Number of Patients', fontdict={"size": "20"})
        # plt.title('Number of Patients with HGG and LGG Tumor Types', fontdict={
        #           "size": "20"})
        # plt.xticks(rotation=0)
        # plt.yticks(range(0, patients_count_by_sex['Count'].max() + 1))
        hgg_count = records_df[3].value_counts().get('HGG', 0)
        lgg_count = records_df[3].value_counts().get('LGG', 0)

        # Pie chart labels
        labels = ['HGG', 'LGG']

        # Data to plot
        sizes = [hgg_count, lgg_count]

        # Set colors for the pie slices
        colors = ['#FF4040', '#008000']
        fig2 = plt.figure()
        # Plot the pie chart
        plt.pie(sizes, labels=labels, colors=colors,
                autopct='%1.1f%%', startangle=90)

        # Set aspect ratio to make the pie chart a circle
        plt.axis('equal')

        # Add a title to the pie chart
        plt.title('HGG and LGG percentage')

        age_distribution = records_df.groupby(2)[8].mean()

        # Plot the bar chart
        fig3 = plt.figure(figsize=(8, 6))
        age_distribution.plot(kind='bar', color=[
            "blue", "pink"])
        plt.xlabel('Tumor Type', fontdict={"size": "20"})
        plt.ylabel('Average Age', fontdict={"size": "20"})
        plt.title('Distribution of HGG and LGG Tumor Types based on Age', fontdict={
                  "size": "20"})

    col1, col2, col3 = st.columns(3)
    with col1:
        st.pyplot(fig1, use_container_width=True)
    if fig2 is not None:
        with col2:
            st.pyplot(fig2)
        with col3:
            st.pyplot(fig3)
    else:
        st.write("Not available yet")

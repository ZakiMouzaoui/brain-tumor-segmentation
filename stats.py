import glob
import streamlit as st
from db_manager import get_appointments_for_doctor, get_medical_records
import pandas as pd
import matplotlib.pyplot as plt
from skimage import transform
from matplotlib.cm import get_cmap
import nibabel as nib
import json

# plt2.style.use('dark_background')


def stats_page():
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

    # def retrieve_patients():
    #     st.session_state["patients"] = view_patients(id)

    def retrieve_appointments(filter_):
        appointments = get_appointments_for_doctor(id)

        if filter_ != -1:
            st.session_state["appointments"] = list(filter(
                lambda x: x[-1] == filter_, appointments))
        else:
            st.session_state["appointments"] = appointments

    def get_medical_records_():
        st.session_state["medical_records"] = get_medical_records()

    st.markdown("<h1 style='text-align: center'>Patients 😷</h1>",
                unsafe_allow_html=True)
    st.markdown(" ")

    if not "medical_records" in st.session_state:
        st.session_state["filter"] = -1
    get_medical_records_()
    # retrieve_patients()
    retrieve_appointments(st.session_state["filter"])

    col1, col2 = st.columns(2)
    patients = st.session_state["patients"]
    appointments = st.session_state["appointments"]
    records = st.session_state["medical_records"]

    with col1:
        patients_df = pd.DataFrame(patients, columns=[
                                   "Id", "Name", "Sex", "Age", "Joining date"])
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
        appointments_df = pd.DataFrame(appointments, columns=[
            "Id", "Patient name", "Doctor name", "Date", "Status", ])
        appointments_df["Status"] = appointments_df["Status"].replace({
            0: "Pending", 1: "Confirmed", 2: "Canceled"
        })
        _, __ = st.columns(2)
        with _:
            filter_ = st.selectbox("Filter appointments", options=[
                -1, 0, 1, 2], format_func=lambda x: "Pending" if x == 0 else "Confirmed" if x == 1 else "Canceled" if x == 2 else "All")

            st.session_state["filter"] = filter_
            retrieve_appointments(st.session_state["filter"])
            # st.experimental_rerun()
        appointments_df = appointments_df.style.set_properties(
            **{'text-align': 'left'}).set_table_styles(styles)

        st.subheader("appointments")
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
                st.subheader("MRI results")
                fig = plot_seg(
                    nib.load(glob.glob(f"uploads/{selected_patient[0]}/segmentation/*")[0]).get_fdata())
                st.pyplot(fig)
            with co2:

                st.subheader("Tumor informations")
                st.markdown("<div class='tumor-info'>", unsafe_allow_html=True)
                st.markdown(
                    f"<h5> Tumor type : {record[2]}</h5>", unsafe_allow_html=True)

                for k, v in json.loads(record[3]).items():
                    st.markdown(f"""<h5>{k} :  {v:.2f}</h5>""",
                                unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("""
                <style>

                </style>
            """, unsafe_allow_html=True)
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
    plt.xlabel('Sex', fontdict={"size": "20"})
    plt.ylabel('Count', fontdict={"size": "20"})
    plt.title('Count of Patients by Sex', fontdict={"size": "20"})
    plt.yticks(range(0, patients_count_by_sex['Count'].max() + 1))
    #########################################################################
    records_df = pd.DataFrame(records)
    fig2 = None
    fig3 = None

    if len(records_df) > 0:
        tumor_types_count = records_df[2].value_counts().reset_index()
        tumor_types_count.columns = ['tumor_type', 'count']

        # Plot the bar chart
        fig2 = plt.figure()
        plt.bar(tumor_types_count['tumor_type'], tumor_types_count['count'], color=[
            "blue", "pink"])

        plt.xlabel('Tumor Type', fontdict={"size": "20"})
        plt.ylabel('Number of Patients', fontdict={"size": "20"})
        plt.title('Number of Patients with HGG and LGG Tumor Types', fontdict={
                  "size": "20"})
        plt.xticks(rotation=0)
        plt.yticks(range(0, patients_count_by_sex['Count'].max() + 1))

        age_distribution = records_df.groupby(2)[6].mean()

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
        st.pyplot(fig1)
    if fig2 is not None:
        with col2:
            st.pyplot(fig2)
        with col3:
            st.pyplot(fig3)
    else:
        st.write("Not available yet")

    # df = pd.DataFrame(patients, columns=[
    #                   "Name", "Sex", "Age", "Tumor Type", "Date"])
    # df.index.names = ['ID']
    # # df.drop(["user_id"], inplace=True, axis=1)

    # delete = st.button("delete")
    # if delete:
    #     delete_patients()
    #     st.experimental_rerun()

    # st.subheader("You can view your added patients here")
    # st.dataframe(df, width=1000)

    # tumor_counts = df['Tumor Type'].value_counts()
    # fig, ax = plt2.subplots()
    # wedges, labels, autopct = ax.pie(
    #     tumor_counts, labels=tumor_counts.index, autopct='%1.1f%%', colors=["#DB6000", "#166399"])

    # # for label in labels:
    # #     label.set_color('white')

    # ax.set_title('Tumor Type Distribution', color="white")
    # ax.axis('equal')  # Equal aspect ratio ensures a circular pie chart

    # if not df.empty:
    #     col1, col2, col3 = st.columns(3)
    #     grouped_data = df.groupby(['Sex', 'Tumor Type']).size().unstack()

    #     fig2, ax2 = plt2.subplots()

    #     # Set the width of the bars
    #     bar_width = 0.15

    #     # Generate the positions of the bars
    #     bar_positions = range(len(grouped_data.index))

    #     if "HGG" in grouped_data:
    #         # Plot the HGG bars
    #         ax2.bar(
    #             bar_positions, grouped_data['HGG'], width=bar_width, label='HGG', color="#DB6000")

    #     if "LGG" in grouped_data:
    #         # Plot the LGG bars next to the HGG bars
    #         ax2.bar([p + bar_width for p in bar_positions], grouped_data['LGG'],
    #                 width=bar_width, label='LGG', color="#166399")

    #     ax2.set_title('Sex and Tumor Type Distribution', color="white")
    #     ax2.set_xlabel('Sex', color="white")
    #     ax2.set_ylabel('Count', color="white")

    #     # Set the x-axis tick labels
    #     ax2.set_xticks([p + bar_width / 2 for p in bar_positions])
    #     ax2.set_xticklabels(grouped_data.index)

    #     # Set the legend
    #     ax2.legend(title='Tumor Type', loc='upper right')

    #     with col1:
    #         st.pyplot(fig, use_container_width=True)
    #     with col2:
    #         st.pyplot(fig2, use_container_width=True)

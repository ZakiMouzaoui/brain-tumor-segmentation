import cv2
import dicom2nifti
from antspynet.utilities import brain_extraction
import SimpleITK as sitk
from radiomics import featureextractor
import pickle
import ants
import json
from streamlit_card import card
from streamlit_lottie import st_lottie_spinner
from skimage import transform
from matplotlib.cm import get_cmap
from keras.models import load_model
import shutil
from glob import glob
import nibabel as nib
import os
import pandas as pd
import numpy as np
from db_manager import view_patients, add_medical_record, check_if_rated, add_rating
import streamlit as st
import matplotlib.pyplot as plt
from streamlit_star_rating import st_star_rating
plt.style.use('default')


########################## MAIN FUNCTION ###########################################
def home_page():
    def get_patients():
        patients = view_patients(st.session_state["user_id"])
        return patients

    @st.cache_resource(show_spinner=False)
    def load_seg_model():
        return load_model("assets/ARUGD_training_checkpoint2.h5", compile=False)

    @st.cache_data(show_spinner=False)
    def load_lottie_file(file_path):
        with open(file_path, "r") as f:
            return json.load(f)

    def normalize(img):
        mean = img.mean()
        std = img.std()
        return (img - mean) / (std + 0.00001)

    def segment_tumor(model, t1, t1ce, t2, flair):
        if st.session_state["file_format"] == "DICOM":
            t1 = cv2.resize(t1[:, :, 0:-1], (240, 240))
            t1ce = cv2.resize(t1ce[:, :, 0:-1], (240, 240))
            t2 = cv2.resize(t2[:, :, 0:-1], (240, 240))
            flair = cv2.resize(flair[:, :, 0:-1], (240, 240))

        x = np.stack([normalize(t1), normalize(t1ce),
                     normalize(t2), normalize(flair)])
        x = np.transpose(x, (3, 1, 2, 0))
        prediction = model.predict(x)
        pred_argmax = np.argmax(prediction[0], axis=-1)
        st.session_state["prediction"] = pred_argmax

    @st.cache_data(show_spinner=False)
    def load_classification_model():
        class_model = pickle.load(
            open("assets/random_forest_classifier.pkl", "rb"))
        return class_model

    @st.cache_data(show_spinner=False)
    def load_scaler():
        scaler = pickle.load(open("assets/scaler.pkl", "rb"))
        return scaler

    def classify_tumor(model, sequ):
        seg = st.session_state["prediction"].transpose((2, 1, 0))
        settings = {}
        settings['binWidth'] = 25
        settings['resampledPixelSpacing'] = None
        settings['interpolator'] = 'sitkBSpline'
        settings['verbose'] = False
        extractor = featureextractor.RadiomicsFeatureExtractor(**settings)
        extractor.enableFeatureClassByName('glcm')

        sequ = sitk.GetImageFromArray(sequ)
        seg = sitk.GetImageFromArray(seg)

        featureVector2 = extractor.execute(sequ, seg)
        elongation2 = []
        flatness2 = []
        majAL2 = []
        minAL2 = []
        threedimdiam2 = []
        spher2 = []
        surfArea2 = []
        energ2 = []
        entrop2 = []
        kurt2 = []
        mean2 = []
        skew2 = []
        cont2 = []
        correl2 = []
        idm2 = []
        coarse2 = []
        complexity2 = []
        strength2 = []

        elongation2.append(featureVector2['original_shape_Elongation'])
        flatness2.append(featureVector2['original_shape_Flatness'])
        majAL2.append(featureVector2['original_shape_MajorAxisLength'])
        minAL2.append(featureVector2['original_shape_MinorAxisLength'])
        threedimdiam2.append(
            featureVector2['original_shape_Maximum3DDiameter'])
        spher2.append(featureVector2['original_shape_Sphericity'])
        surfArea2.append(featureVector2['original_shape_SurfaceArea'])
        energ2.append(featureVector2['original_firstorder_Energy'])
        entrop2.append(featureVector2['original_firstorder_Entropy'])
        kurt2.append(featureVector2['original_firstorder_Kurtosis'])
        mean2.append(featureVector2['original_firstorder_Mean'])
        skew2.append(featureVector2['original_firstorder_Skewness'])
        cont2.append(featureVector2['original_glcm_Contrast'])
        correl2.append(featureVector2['original_glcm_Correlation'])
        idm2.append(featureVector2['original_glcm_Idm'])
        coarse2.append(featureVector2['original_ngtdm_Coarseness'])
        complexity2.append(featureVector2['original_ngtdm_Complexity'])
        strength2.append(featureVector2['original_ngtdm_Strength'])

        test_data = {
            'elongation': elongation2,
            'flatness': flatness2,
            'major_axis_length': majAL2,
            'minor_axis_length': minAL2,
            'max_3D_diameter': threedimdiam2,
            'sphericity': spher2,
            'surface_area': surfArea2,
            'energy': energ2,
            'entropy': entrop2,
            'kurtosis': kurt2,
            'mean': mean2,
            'skewness': skew2,
            'contrast': cont2,
            'correlation': correl2,
            'inverse_diff_moment': idm2,
            'coarseness': coarse2,
            'complexity': complexity2,
            'strength': strength2,
        }
        test_df = pd.DataFrame(test_data)
        scaler = load_scaler()
        test_scaled = scaler.transform(test_df.values)

        tumor_infos = {
            "Shape elongation": elongation2[0],
            "Shape flatness": flatness2[0],
            "Max shape 3d diameter": threedimdiam2[0].item(),
            "Shape sphericity": spher2[0].item(),
            "GLCM contrast": cont2[0].item(),
            "NGTDM complexity": complexity2[0].item(),
            "NGTDM strength": strength2[0].item()
        }
        return (model.predict(test_scaled), test_df, tumor_infos)

    @st.cache_data
    def getBrainSizeForVolume(image_volume):
        total = 0
        for i in range(image_volume.shape[-1]):
            arr = image_volume[:, :, i].flatten()
            image_count = np.count_nonzero(arr)
            total = total+image_count
        return total

    @st.cache_data
    def getMaskSizesForVolume(image_volume):
        totals = dict([(0, 0), (1, 0), (2, 0), (3, 0)])
        for i in range(image_volume.shape[-1]):
            # flatten 2D image into 1D array and convert mask 4 to 2
            arr = image_volume[:, :, i].flatten()
            # arr[arr == 4] = 3

            unique, counts = np.unique(arr, return_counts=True)
            unique = unique.astype(int)
            values_dict = dict(zip(unique, counts))
            for k in range(0, 4):
                totals[k] += values_dict.get(k, 0)
        return totals

    # @st.cache_data(show_spinner=False)
    def plot_ants(_seq):
        cols = 5
        rows = 4
        fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(5, 4))
        idx = 0
        if st.session_state["file_format"] == "DICOM":
            angle = 90
        else:
            angle = 270

        for i in range(rows):
            for j in range(cols):
                axes[i, j].imshow(transform.rotate(
                    _seq[:, :, idx], angle=angle), cmap="gray")
                axes[i, j].axis("off")
                idx += 1

        return fig

    # @st.cache_data(show_spinner=False)
    def plot_seg(cmap_val="viridis"):
        seg = st.session_state["prediction"]
        if st.session_state["file_format"] == "DICOM":
            angle = 90
        else:
            angle = 270

        cols = 5
        rows = 4
        fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(5, 4))
        idx = 0
        class_labels = ["No Tumor", "Tumor Core/Necrosis",
                        "Edema", "Enhancing Tumor"]
        cmap = get_cmap(cmap_val)

        for i in range(rows):
            for j in range(cols):
                axes[i, j].imshow(transform.rotate(
                    seg[idx, :, :], angle=angle), cmap=cmap)
                axes[i, j].axis("off")
                idx += 1

        # legend_patches = [mpatches.Patch(color=cmap(
        #     i / (len(class_labels) - 1)), label=label) for i, label in enumerate(class_labels)]
        # plt.legend(handles=legend_patches, loc="upper right", fontsize=6.5)
        return fig

    def skull_strip(path, modality):
        ants_image = ants.image_read(path)
        brain_mask = brain_extraction(
            ants_image, verbose=False, modality=modality)
        # brain_mask = ants.get_mask(prob_brain_mask, low_thresh=0.5)
        result = ants.mask_image(ants_image, brain_mask)

        return result

    def upload_file(uploaded_file, modality):
        os.makedirs(f"temp/{id}/"+modality, exist_ok=True)

        temp_dir = os.path.join(f"temp/{id}/", modality)
        files = glob(temp_dir + "/*")

        for f in files:
            os.remove(f)

        for file in uploaded_file:
            with open(temp_dir + "/"+file.name, "wb") as f:
                f.write(file.getbuffer())

    def upload_nifti(upload_file, path):
        with open(path + "/"+upload_file.name, "wb") as f:
            f.write(upload_file.getvalue())
    id = st.session_state["user_id"]
    if not "has_rated" in st.session_state:
        st.session_state["has_rated"] = check_if_rated(id)
        st.session_state["show_rating"] = False
        st.session_state["patients"] = get_patients()

    if st.session_state["authenticated"] == False:
        disabled = True
        submit_help = "Please login"

    else:
        submit_help = ""
        disabled = False

    hide_streamlit_style = """
                <style>
                # div[data-testid="stToolbar"] {
                # visibility: hidden;
                # height: 0%;
                # position: fixed;
                # }

                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }

                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
    
                footer {
                    visibility: hidden;
                }
      
                </style>
                """

    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    st.markdown(
        """<style>
      div[class*="stRadio"] > label > div[data-testid="stMarkdownContainer"] > p {
          font-size: 1.8rem;
      }

      div.stButton>button:first-child {margin-left: 0}
      div[data-testid="stMarkdownContainer"] > p{
        font-size:1.3rem
      }
      [data-testid="stHeader"]{
        background-color:rgba(0,0,0,0)
    }

    .stButton{
        padding:0 
    }

      
          </style>
    """, unsafe_allow_html=True)

    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.markdown("<h1 style='text-align: center'>Brain AI 🧠</h1>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        card(
            title="Accuracy",
            text="Accurate segmentation for targeted treatment",
            image="https://i0.wp.com/statisticsbyjim.com/wp-content/uploads/2021/09/target.png?resize=300%2C291&ssl=1",
            url=""
        )

    with col2:
        card(
            title="Speed",
            text="Efficient brain tumor segmentation for faster diagnosis",
            image="https://storage.googleapis.com/aliz-website-sandbox-strapi-cms/Customer_experience_cb479609da/Customer_experience_cb479609da.png",
            url=""
        )

    with col3:
        card(
            title="Ease",
            text="Effortless segmentation with one button click",
            image="https://media.istockphoto.com/id/1172207434/vector/click-here-the-button.jpg?s=612x612&w=0&k=20&c=uszvKX_5Sc0jKPq4jiMNbEgK7EOC3XFg-J6BsDsfwcE=",
            url=""
        )

    st.markdown("### ✔️ Semantic segmentation for brain tumor")
    st.markdown(
        "### ✔️ Classification of the segmented tumor (High Grade Glioma or Low Grade Glioma)")
    # st.markdown("### ✔️ Survival rate prediction for the patient")
    st.markdown("#")
    id = st.session_state["user_id"]
    # Uploading Data
    st.subheader('Upload the 4 sequences(T1, T1 post contrast, T2 and FLAIR)')
    c1, _, _, _ = st.columns(4)

    with c1:
        file_format = st.selectbox(
            "Choose a file format", options=["NIFTI", "DICOM"])
        if file_format == "NIFTI":
            # st.session_state["converted"] = True
            types = ["nii.gz", "nii"]
            multiple = False

        else:
            types = ["dcm"]
            multiple = True
            # if not st.session_state["converted"]:
            #     st.session_state["converted"] = False

        if st.session_state["prediction"] is not None:
            st.session_state["submitted"] = False
            st.session_state["converted"] = False

    with st.form("my-form"):
        col1, col2 = st.columns(2, gap="small")
        with col1:
            t1_file = st.file_uploader(
                'T1', type=types, accept_multiple_files=multiple)

        with col2:
            t1ce_file = st.file_uploader(
                'T1* (Post Contrast)', type=types, accept_multiple_files=multiple)

        col1, col2 = st.columns(2)

        with col1:
            t2_file = st.file_uploader(
                'T2', type=types, accept_multiple_files=multiple)

        with col2:
            flair_file = st.file_uploader(
                'FLAIR', type=types, accept_multiple_files=multiple)

        submitted = st.form_submit_button(
            "Upload", help=submit_help, disabled=disabled)

        if submitted:
            st.session_state["prediction"] = None
            if file_format == "DICOM":
                if len(t1_file) != 0 and len(t2_file) != 0 and len(t1ce_file) != 0 and len(flair_file) != 0:
                    st.session_state["submitted"] = True
                    st.session_state["Prediction"] = None
                else:
                    _, __, ___ = st.columns([1, 2, 1])
                    st.session_state["submitted"] = False
                    with _:
                        st.error("Please submit all necessary files")
            else:
                if t1_file and t1ce_file and t2_file and flair_file:
                    st.session_state["submitted"] = True
                else:
                    _, __, ___ = st.columns([1, 2, 1])
                    st.session_state["submitted"] = False
                    with _:
                        st.error("Please submit all necessary files")

    if st.session_state["submitted"]:
        seg_disabled = False
        seg_help = ""
        st.session_state["prediction"] = None
        # st.session_state["converted"] = False
        st.session_state["file_format"] = file_format
        # id = st.session_state["user_id"]
        if file_format == "DICOM":

            if not st.session_state["converted"]:
                upload_file(t1_file, "t1")
                upload_file(t1ce_file, "t1ce")
                upload_file(t2_file, "t2")
                upload_file(flair_file, "flair")

                with st.spinner("Converting your files..."):
                    if os.path.exists(f"temp/{id}/t1_nii"):
                        shutil.rmtree(f"temp/{id}/t1_nii")

                    if os.path.exists(f"temp/{id}/t1ce_nii"):
                        shutil.rmtree(f"temp/{id}/t1ce_nii")

                    if os.path.exists(f"temp/{id}t2_nii"):
                        shutil.rmtree(f"temp/{id}/t2_nii")

                    if os.path.exists(f"temp/{id}/flair_nii"):
                        shutil.rmtree(f"temp/{id}/flair_nii")

                    os.makedirs(f"temp/{id}/t1_nii")
                    os.makedirs(f"temp/{id}/t2_nii")
                    os.makedirs(f"temp/{id}/t1ce_nii")
                    os.makedirs(f"temp/{id}/flair_nii")

                    dicom2nifti.convert_directory(
                        os.path.join("temp", str(id), "t1"), f"temp/{id}/t1_nii")
                    dicom2nifti.convert_directory(
                        os.path.join("temp", str(id), "t2"), f"temp/{id}/t2_nii")
                    dicom2nifti.convert_directory(
                        os.path.join("temp", str(id), "t1ce"), f"temp/{id}/t1ce_nii")
                    dicom2nifti.convert_directory(
                        os.path.join("temp", str(id), "flair"), f"temp/{id}/flair_nii")
                st.session_state["converted"] = True
        else:
            st.session_state["converted"] = True
            if os.path.exists("temp/t1_nii"):
                shutil.rmtree("temp/t1_nii")

            if os.path.exists("temp/t1ce_nii"):
                shutil.rmtree("temp/t1ce_nii")

            if os.path.exists("temp/t2_nii"):
                shutil.rmtree("temp/t2_nii")

            if os.path.exists("temp/flair_nii"):
                shutil.rmtree("temp/flair_nii")

            os.makedirs("temp/t1_nii")
            os.makedirs("temp/t2_nii")
            os.makedirs("temp/t1ce_nii")
            os.makedirs("temp/flair_nii")

            upload_nifti(t1_file, "temp/t1_nii")
            upload_nifti(t1ce_file, "temp/t1ce_nii")
            upload_nifti(t2_file, "temp/t2_nii")
            upload_nifti(flair_file, "temp/flair_nii")

        t1_nii = glob(f"temp/{id}/t1_nii/*")[0]
        t1ce_nii = glob(f"temp/{id}/t1ce_nii/*")[0]
        t2_nii = glob(f"temp/{id}/t2_nii/*")[0]
        flair_nii = glob(f"temp/{id}/flair_nii/*")[0]

        st.session_state['t1'] = t1_nii
        st.session_state['t1ce'] = t1ce_nii
        st.session_state['t2'] = t2_nii
        st.session_state['flair'] = flair_nii
    else:
        seg_disabled = True
        seg_help = "Make sure you uploaded the necessary files"
    _, _, col3, _, _ = st.columns(5)

    with col3:
        with st.expander("Segmentation"):
            with st.form("my_form"):
                preprocess = st.radio(
                    "Choose an option",
                    ('With Skull Removal', 'Without Skull Removal'),
                    help="Choose whether you remove the skull before or no"
                )

                # Every form must have a submit button.
                segment_btn = st.form_submit_button(
                    "Start", disabled=seg_disabled, help=seg_help)
                if segment_btn:
                    st.session_state["type"] = None
                    st.session_state["segment_loading"] = True

        if st.session_state["segment_loading"] == True:
            # PREPROCESSING STEP
            if preprocess == "With Skull Removal":
                with st.spinner("Preprocessing T1..."):
                    t1 = skull_strip(t1_nii, "t1")
                with st.spinner("Preprocessing T1*..."):
                    t1ce = skull_strip(t1ce_nii, "t1")
                with st.spinner("Preprocessing T2..."):
                    t2 = skull_strip(t2_nii, "t2")
                with st.spinner("Preprocessing Flair..."):
                    flair = skull_strip(flair_nii, "flair")
            else:
                t1 = nib.load(t1_nii).get_fdata()
                t1ce = nib.load(t1ce_nii).get_fdata()
                t2 = nib.load(t1_nii).get_fdata()
                flair = nib.load(t1_nii).get_fdata()
            if st.session_state["file_format"] == "NIFTI":
                t1 = t1[:, :, 60:80]
                t1ce = t1ce[:, :, 60:80]
                t2 = t2[:, :, 60:80]
                flair = flair[:, :, 60:80]

            st.session_state["final_t2"] = t1

            # SEGMENTATION STEP
            lottie_json = load_lottie_file("assets/brain ai animation.json")
            with st_lottie_spinner(lottie_json, height=100, speed=2, quality="low"):
                model = load_seg_model()
                segment_tumor(
                    model,
                    t1,
                    t1ce,
                    t2,
                    flair,
                )

            st.session_state["segment_loading"] = False
            if "type" in st.session_state:
                st.session_state["type"] = None

    if st.session_state["prediction"] is not None:
        st.session_state["submitted"] = False
        st.session_state["converted"] = False

        ccc1, __, cc3, ___ = st.columns(4)
        with ccc1:
            sequence = st.selectbox("Choose an MRI sequence", options=[
                                    "T1", "T1*(Gadolinium)", "T2", "FLAIR"], key="sequence-select")
            if sequence:
                st.session_state["sequence"] = sequence
        with cc3:
            cmap = st.selectbox("Choose a color map", options=[
                                "viridis", "rainbow", "ocean"], format_func=lambda x: "color 1" if x == "viridis" else "color 2" if x == "rainbow" else "color 3", key="cmap-select")
            st.session_state["cmap"] = cmap
        with ___:

            st.image(f"assets/{cmap}-cmap.png")

        cc1, cc2 = st.columns(2)
        if st.session_state["sequence"] == "T1":
            seq = nib.load(st.session_state["t1"]).get_fdata()
        elif st.session_state["sequence"] == "T1*(Gadolinium)":
            seq = nib.load(st.session_state["t1ce"]).get_fdata()
        elif st.session_state["sequence"] == "T2":
            seq = nib.load(st.session_state["t2"]).get_fdata()
        else:
            seq = nib.load(st.session_state["flair"]).get_fdata()

        if st.session_state["file_format"] == "NIFTI":
            seq = seq[:, :, 60:80]
        with cc1:
            fig2 = plot_ants(seq)
            st.pyplot(fig2, use_container_width=True)

        with cc2:
            fig = plot_seg(cmap_val=st.session_state["cmap"])
            st.pyplot(fig, use_container_width=True)
        ####### END OF SELECT BOX ###########################
        st.divider()
        _, co2, co3, co4 = st.columns([1, 1, 1, 1])

        ######## CLASSIFICATION BUTTON #######################
        with co2:
            # t2_ = nib.load(st.session_state["t2"]).get_fdata()
            t2_ = st.session_state["final_t2"]
            if st.session_state["file_format"] == "DICOM":

                t2_ = cv2.resize(t2_[:, :, 0:-1], (240, 240))

            classification = st.button("Tumor Type", use_container_width=True)
            if classification:
                class_model = load_classification_model()
                lottie_json = load_lottie_file(
                    "assets/brain ai animation.json")

                with st_lottie_spinner(lottie_json, height=100, speed=2):
                    tumor_type, _, infos = classify_tumor(class_model, t2_)
                    if (tumor_type[0] == 1):
                        st.session_state["type"] = "High Grade Glioma"
                    else:
                        st.session_state["type"] = "Low Grade Glioma"

                    st.session_state["tumor_infos"] = infos
            if "type" in st.session_state and st.session_state["type"] is not None:
                # col1, _, __ = st.columns([1,2,1])
                with co2:
                    st.info(st.session_state["type"])
                    for k, v in st.session_state["tumor_infos"].items():
                        st.write(f"{k}: {v:.2f}")
            ######## END OF CLASSIFICATION #######################

            ######## SURVIVAL BUTTON #############################
            # with co3:
            #     with st.expander("Survival prediction"):
            #         with st.form("form"):
            #             age = st.number_input(
            #                 "Enter the patient age", min_value=10, max_value=100, format="%d", value=60)
            #             eor = st.selectbox("Extent of resection(EOR)", help="The EOR is a measure of how much of the tumor mass is successfully removed surgically. GTR ===> total tumor removed, STR ===> small portion removed", options=[
            #                                "GTR", "STR", "NOTHING"])
            #             predict = st.form_submit_button("Predict")

            ###### END OF SURVIVAL #############################
        with co3:
            st.markdown(
                "<h4>Save medical record</h4>", unsafe_allow_html=True)
            patients = st.session_state["patients"]
            with st.form("save-form", clear_on_submit=True):
                patient_select = st.selectbox(
                    "Select a patient", options=patients, format_func=lambda x: x[1])

                # st.selectbox("Sex", options=[
                #     "Male", "Female"], index=0 if patient_select[2] == "Male" else 1, disabled=True)
                # st.number_input(
                #     "Age", value=patient_select[3], disabled=True)
                tumor_type = st.selectbox(
                    "Tumor type", options=["HGG", "LGG"])

                cc1, cc2, cc3 = st.columns([1, 2, 1])
                with cc2:
                    save_info = st.form_submit_button(
                        "Save", use_container_width=True)

                if save_info:
                    with st.spinner("saving ..."):
                        nifti = nib.Nifti1Image(
                            st.session_state["prediction"].astype(np.float32), np.eye(4))
                        if os.path.exists(f"uploads/{patient_select[0]}/segmentation"):
                            shutil.rmtree(
                                f"uploads/{patient_select[0]}/segmentation")

                        os.makedirs(
                            f"uploads/{patient_select[0]}/segmentation")
                        nib.save(
                            nifti, f"uploads/{patient_select[0]}/segmentation"+"/segmentation.nii.gz")

                    json_str = json.dumps(st.session_state["tumor_infos"])

                    add_medical_record(patient_select[0], tumor_type, json_str)
                    st.success("Medical record saved")
                    st.session_state["prediction"] = None
                    shutil.rmtree(f"temp/{id}")
                    st.session_state["show_rating"] = True
                    st.experimental_rerun()
    else:
        if st.session_state["show_rating"] == True:
            if not st.session_state["has_rated"]:
                c1, c2, c3 = st.columns([1, 2, 1])
                with c2:
                    st.markdown(
                        "<h3 style='text-align:center;'>Rate our model</h3>", unsafe_allow_html=True)
                    with st.form("rate-form"):
                        stars = st_star_rating("", 5, 3, 30)
                        text = st.text_area("Say somthing",
                                            placeholder="Give your feedback")

                        rate = st.form_submit_button("Submit")
                        if rate:
                            add_rating(id, stars, None if not text else text)
                            st.session_state["show_rating"] = False
                            st.experimental_rerun()

                    cc1, cc2, cc3 = st.columns(3)
                    with cc2:
                        cancel = st.button("Later", use_container_width=True)
                        if cancel:
                            st.session_state["show_rating"] = False
                            st.experimental_rerun()

    st.markdown("""<style>
        h4{
            margin-top: -1rem;
            margin-left: 2.5rem
        }
    </style>""", unsafe_allow_html=True)
    # padding = 0
    # st.markdown(f"""
    #     <style>
    #         .reportview-container .main .block-container{{
    #         padding-top: {padding}rem;
    #         padding-right: {padding}rem;
    #         padding-left: {padding}rem;
    #         padding-bottom: {padding}rem;

    #     }} </style> """, unsafe_allow_html=True)

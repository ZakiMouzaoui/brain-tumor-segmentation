import base64
import cv2
import dicom2nifti
from antspynet.utilities import brain_extraction
import SimpleITK as sitk
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

if st.session_state["theme"] == "dark":
    plt.style.use('dark_background')
else:
    plt.style.use('default')

########################## MAIN FUNCTION ###########################################


def home_page():
    @st.cache_resource(show_spinner=False)
    def load_seg_model():
        return load_model("models/attention_res_unet_guided_decoder.h5", compile=False)

    @st.cache_data(show_spinner=False)
    def load_lottie_file(file_path):
        with open(file_path, "r") as f:
            return json.load(f)

    def normalize(img):
        mean = img.mean()
        std = img.std()
        return (img - mean) / (std + 0.00001)

    def create_slices(inp):
        res = np.zeros((240, 240, 20))

        start_slice = 60
        step = 3
        num_slices = 20

        for i in range(num_slices):
            slice_index = start_slice + i * step
            res[:, :, i] = inp[:, :, slice_index]
        return res

    def segment_tumor(model, t1_seq, t1ce_seq, t2_seq, flair_seq):
        if st.session_state["file_format"] == "DICOM":
            t1_seq = cv2.resize(t1_seq[:, :, :], (240, 240))
            t1ce_seq = cv2.resize(t1ce_seq[:, :, :], (240, 240))
            t2_seq = cv2.resize(t2_seq[:, :, :], (240, 240))
            flair_seq = cv2.resize(flair_seq[:, :, :], (240, 240))

        x = np.stack([normalize(t1_seq), normalize(t1ce_seq),
                     normalize(t2_seq), normalize(flair_seq)])
        x = np.transpose(x, (3, 1, 2, 0))
        prediction = model.predict(x)
        pred_argmax = np.argmax(prediction[0], axis=-1)
        st.session_state["prediction"] = pred_argmax

    @st.cache_data(show_spinner=False)
    def load_classification_model():
        class_model = pickle.load(
            open("models/random_forest_classifier.pkl", "rb"))
        return class_model

    @st.cache_data(show_spinner=False)
    def load_scaler():
        scaler = pickle.load(open("models/scaler.pkl", "rb"))
        return scaler

    @st.cache_data(show_spinner=False)
    def load_extractor():
        extractor = pickle.load(
            open("models/extractor.pkl", "rb"))
        return extractor

    def classify_tumor(model, sequ):
        seg = st.session_state["prediction"].transpose((2, 1, 0))
        extractor = load_extractor()

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
        pred = model.predict(test_scaled)[0]

        return (pred, test_df, tumor_infos)

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
    def plot_seg(seq_, cmap_val="viridis"):
        seg = st.session_state["prediction"]

        if st.session_state["file_format"] == "DICOM":
            angle = 90
        else:
            angle = 270

        cols = 5
        rows = 4
        fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(5, 4))
        idx = 0

        cmap = get_cmap(cmap_val)

        for i in range(rows):
            for j in range(cols):
                tumor_region = np.where(
                    seg[idx, :, :] > 0, seg[idx, :, :], np.nan)
                axes[i, j].imshow(transform.rotate(
                    seq_[:, :, idx], angle=angle), cmap="gray")
                axes[i, j].imshow(transform.rotate(
                    tumor_region, angle=angle), cmap=cmap)

                axes[i, j].axis("off")
                idx += 1
        return fig

    def skull_strip(path, modality):
        ants_image = ants.image_read(path)
        brain_mask = brain_extraction(
            ants_image, verbose=False, modality=modality)

        result = ants.mask_image(ants_image, brain_mask)

        return result

    def upload_file(uploaded_file, modality):
        os.makedirs(f"temp/{id}/"+modality)

        temp_dir = os.path.join(f"temp/{id}/", modality)
        # files = glob(temp_dir + "/*")

        # for f in files:
        #     os.remove(f)

        for file in uploaded_file:
            with open(temp_dir + "/"+file.name, "wb") as f:
                f.write(file.getbuffer())

    def upload_nifti(upload_file, path):
        # if not "file_extension" in st.session_state or st.session_state["file_extension"] is None:
        st.session_state["file_extension"] = upload_file.name.split(".")[
            0][-1]

        with open(path + "/"+upload_file.name, "wb") as f:
            f.write(upload_file.getvalue())

    @st.cache_data(show_spinner=False)
    def get_base64_img1(bin_file):
        with open(bin_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    @st.cache_data(show_spinner=False)
    def get_base64_img2(bin_file):
        with open(bin_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    @st.cache_data(show_spinner=False)
    def get_base64_img3(bin_file):
        with open(bin_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    id = st.session_state["user_id"]
    # st.write("""
    #     <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    # """, unsafe_allow_html=True)

    if not "doctor-patients" in st.session_state or st.session_state["doctor-patients"] is None:
        st.session_state["show_rating"] = False
        st.session_state["doctor-patients"] = view_patients(id)
        st.session_state["submitted"] = False
        st.session_state["segment_loading"] = False
        st.session_state["segmented"] = False
        st.session_state["converted"] = False
        st.session_state["prediction"] = None

    if st.session_state["authenticated"] == False:
        disabled = True
        submit_help = "Please login"

    else:
        st.session_state["has_rated"] = check_if_rated(id)
        submit_help = ""
        disabled = False

    # st.session_state["submitted"] = False

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
    st.markdown("<h1 style='text-align: center'>Brain AI</h1>",
                unsafe_allow_html=True)

    accuracy_img = get_base64_img1("assets/accuracy.png")
    speed_img = get_base64_img2("assets/speed.png")
    ease_img = get_base64_img3("assets/ease.png")

    st.write(f"""
        <div class="cards-list">
            <div class="card 1">
                <div class="card_image"> <img src="data:image/png;base64,{accuracy_img}" /> </div>
                <div class="card_title">
                    Accuracy
                    <!--<div class="card-subtitle">Accurate segmentation for targeted treatment</div>-->
                </div>
            </div>
            <div class="card 1">
                <div class="card_image"> <img src="data:image/png;base64,{speed_img}" /> </div>
                <div class="card_title">
                    Speed
                    <!--<div class="card-subtitle">Efficient brain tumor segmentation for faster diagnosis</div>-->
                </div>
            </div>
            <div class="card 1">
                <div class="card_image"> <img src="data:image/png;base64,{ease_img}" /> </div>
                <div class="card_title">
                    Ease
                    <!--<div class="card-subtitle">Effortless segmentation with one button click</div>-->
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
        .card .card-subtitle{
            font-size:1.7rem;
            font-weight: 500;
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

    with st.form("my-form", clear_on_submit=True):
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
            st.session_state["submitted"] = False
            st.session_state["converted"] = False

            if file_format == "DICOM":
                if len(t1_file) != 0 and len(t2_file) != 0 and len(t1ce_file) != 0 and len(flair_file) != 0:
                    st.session_state["submitted"] = True
                else:
                    _, __, ___ = st.columns([1, 2, 1])
                    with _:
                        st.error("Please submit all necessary files")
            else:
                if t1_file and t1ce_file and t2_file and flair_file:
                    st.session_state["submitted"] = True
                else:
                    _, __, ___ = st.columns([1, 2, 1])

                    with _:
                        st.error("Please submit all necessary files")

    if st.session_state["submitted"] == True:
        seg_disabled = False
        seg_help = ""

        st.session_state["file_format"] = file_format

        if file_format == "DICOM":
            if not st.session_state["converted"]:
                if os.path.exists(f"temp/{id}"):
                    shutil.rmtree(f"temp/{id}")

                upload_file(t1_file, "t1")
                upload_file(t1ce_file, "t1ce")
                upload_file(t2_file, "t2")
                upload_file(flair_file, "flair")

                with st.spinner("Converting DICOM files to NIFTI..."):
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
            if os.path.exists(f"temp/{id}"):
                shutil.rmtree(f"temp/{id}")

            os.makedirs(f"temp/{id}/t1_nii")
            os.makedirs(f"temp/{id}/t2_nii")
            os.makedirs(f"temp/{id}/t1ce_nii")
            os.makedirs(f"temp/{id}/flair_nii")

            upload_nifti(t1_file, f"temp/{id}/t1_nii")
            upload_nifti(t1ce_file, f"temp/{id}/t1ce_nii")
            upload_nifti(t2_file, f"temp/{id}/t2_nii")
            upload_nifti(flair_file, f"temp/{id}/flair_nii")

        _, __, ___ = st.columns([1, 3, 2])
        with _:
            st.success("Your files are ready")

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
                    help="Choose whether you remove the skull before or no",
                    label_visibility="collapsed"
                )

                # Every form must have a submit button.
                segment_btn = st.form_submit_button(
                    "Start", disabled=seg_disabled, help=seg_help)
                if segment_btn:
                    st.session_state["type"] = None
                    st.session_state["segment_loading"] = True

        if st.session_state["segment_loading"] == True:
            t1_nii = glob(f"temp/{id}/t1_nii/*")[0]
            t1ce_nii = glob(f"temp/{id}/t1ce_nii/*")[0]
            t2_nii = glob(f"temp/{id}/t2_nii/*")[0]
            flair_nii = glob(f"temp/{id}/flair_nii/*")[0]

            st.session_state['t1'] = t1_nii
            st.session_state['t1ce'] = t1ce_nii
            st.session_state['t2'] = t2_nii
            st.session_state['flair'] = flair_nii
            # PREPROCESSING STEP
            if preprocess == "With Skull Removal":
                with st.spinner("Removing skull from T1"):
                    t1 = skull_strip(t1_nii, "t1")
                with st.spinner("Removing skull from T1*"):
                    t1ce = skull_strip(t1ce_nii, "t1")
                with st.spinner("Removing skull from T2"):
                    t2 = skull_strip(t2_nii, "t2")
                with st.spinner("Removing skull from FLAIR"):
                    flair = skull_strip(flair_nii, "flair")
            else:

                t1 = nib.load(t1_nii).get_fdata()
                t1ce = nib.load(t1ce_nii).get_fdata()
                t2 = nib.load(t2_nii).get_fdata()
                flair = nib.load(flair_nii).get_fdata()
            if st.session_state["file_format"] == "NIFTI":
                t1 = create_slices(t1)
                t1ce = create_slices(t1ce)
                t2 = create_slices(t2)
                flair = create_slices(flair)

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
        # st.session_state["submitted"] = False
        st.session_state["converted"] = False

        ccc1, __, cc3, ___ = st.columns(4)
        with ccc1:
            sequence = st.selectbox("Choose an MRI sequence", options=[
                                    "T1", "T1*(Gadolinium)", "T2", "FLAIR"], key="sequence-select")
            if sequence:
                st.session_state["sequence"] = sequence
        with cc3:
            cmap = st.selectbox("Choose a color type", options=[
                                "viridis", "rainbow", "ocean"], format_func=lambda x: "Type 1" if x == "viridis" else "Type 2" if x == "rainbow" else "Type 3", key="cmap-select")
            st.session_state["cmap"] = cmap
        with ___:

            st.image(f"assets/{cmap}-dark.png")

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
            seq = create_slices(seq)
        with cc1:
            seq = cv2.resize(seq[:, :, :], (240, 240))
            fig2 = plot_ants(seq)
            st.pyplot(fig2, use_container_width=True)

        with cc2:
            fig = plot_seg(seq, cmap_val=st.session_state["cmap"])
            st.pyplot(fig, use_container_width=True)
        ####### END OF SELECT BOX ###########################
        st.divider()
        co1, co2, co3 = st.columns(3)

        ######## CLASSIFICATION BUTTON #######################
        with co2:
            # t2_ = nib.load(st.session_state["t2"]).get_fdata()
            t2_ = st.session_state["final_t2"]
            if st.session_state["file_format"] == "DICOM":

                t2_ = cv2.resize(t2_[:, :, :], (240, 240))
            cc1, cc2, cc3 = st.columns([1, 2, 1])
            with cc2:
                classification = st.button(
                    "Tumor Type", use_container_width=True)
                if classification:
                    class_model = load_classification_model()
                    lottie_json = load_lottie_file(
                        "assets/brain ai animation.json")

                    with st_lottie_spinner(lottie_json, height=100, speed=2):
                        tumor_type, _, infos = classify_tumor(class_model, t2_)
                        if (tumor_type == 1):
                            st.session_state["type"] = "High Grade Glioma"
                        else:
                            st.session_state["type"] = "Low Grade Glioma"

                        st.session_state["tumor_infos"] = infos

        if "type" in st.session_state and st.session_state["type"] is not None:
            cc1, cc2, cc3 = st.columns([1, 2, 1])

            with cc2:
                d = st.session_state["tumor_infos"]
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

                c1, c2 = st.columns(2)
                with c1:
                    # st.info(st.session_state["type"])
                    st.text_input(
                        "Tumor Type", value=st.session_state["type"], key="type-tumor", disabled=True)

                    for idx, k in enumerate(keys_list_1):
                        st.text_input(
                            k, value=d[k], key=k, disabled=True, help=helps[idx])
                with c2:
                    for idx, k in enumerate(keys_list_2):
                        st.text_input(
                            k, value=d[k], key=k, disabled=True, help=helps[idx])

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
            ######## END OF CLASSIFICATION #######################

            ############### SAVE PATIENT #########################
            with cc2:
                patients = st.session_state["doctor-patients"]
                _, __, _ = st.columns([1, 2, 1])
                with __:
                    with st.expander("Save medical record"):
                        with st.form("save-form", clear_on_submit=True):
                            patient_select = st.selectbox(
                                "Select a patient", options=patients, format_func=lambda x: x[1])

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

                                    if os.path.exists(f"uploads/{patient_select[0]}/results"):
                                        shutil.rmtree(
                                            f"uploads/{patient_select[0]}/results")

                                    os.makedirs(
                                        f"uploads/{patient_select[0]}/results/segmentation")

                                    shutil.move(
                                        f"temp/{id}/t2_nii", f"uploads/{patient_select[0]}/results/")

                                    nib.save(
                                        nifti, f"uploads/{patient_select[0]}/results/segmentation/segmentation.nii.gz")

                                json_str = json.dumps(
                                    st.session_state["tumor_infos"])

                                add_medical_record(
                                    patient_select[0], id, tumor_type, json_str, file_format)
                                st.success("Medical record saved")
                                st.session_state["prediction"] = None
                                shutil.rmtree(f"temp/{id}")
                                st.session_state["show_rating"] = True
                                st.experimental_rerun()
            ############### END OF SAVE ##########################

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

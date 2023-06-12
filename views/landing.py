import streamlit as st


def landing_page():

    # Set background color and styles
    st.markdown(
        """
        <style>
            body {
                background-color: #f5f5f5;
            }
            .stButton>button {
                background-color: #007bff !important;
                color: #ffffff !important;
                font-size: 16px !important;
                padding: 12px 24px !important;
                border-radius: 8px !important;
                border: none !important;
            }
            .stButton>button:hover {
                background-color: #0056b3 !important;
            }
            .stTitle {
                font-size: 48px !important;
                color: #007bff !important;
                margin-top: 100px !important;
                text-align: center !important;
            }
            .stText {
                font-size: 24px !important;
                margin-bottom: 50px !important;
                text-align: center !important;
            }
            .stImage {
                margin-top: 50px !important;
                text-align: center !important;
            }
            .stImage img {
                max-width: 800px;
                width: 100%;
                height: auto;
                border-radius: 8px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
            }
            .stButtonContainer {
                margin-top: 50px !important;
                text-align: center !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Display title
    st.title("Welcome to Medical Care")
    st.markdown("<p class='stText'>Providing Quality Healthcare Solutions</p>",
                unsafe_allow_html=True)

    # Display image
    st.markdown("<div class='stImage'><img src='medical_care_image.jpg'></div>",
                unsafe_allow_html=True)

    # Display description
    st.markdown(
        """
        <p class='stText'>At Medical Care, we are committed to delivering top-notch healthcare services.</p>
        <p class='stText'>Our platform offers innovative solutions to enhance patient care and improve outcomes.</p>
        """,
        unsafe_allow_html=True
    )

    # Display call to action button
    st.markdown("<div class='stButtonContainer'><button class='stButton'>Get Started</button></div>",
                unsafe_allow_html=True)

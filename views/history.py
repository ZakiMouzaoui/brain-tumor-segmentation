import streamlit as st
from db_manager import get_history, delete_activities


def history_page():
    def retrieve_history():
        activities = get_history()
        st.session_state["activities"] = activities

    st.markdown("<h1 style='text-align: center'>History</h1>",
                unsafe_allow_html=True)
    st.markdown(" ")

    retrieve_history()

    activities = st.session_state["activities"]

    ids = []

    if not "all-checked" in st.session_state:
        st.session_state["all-checked"] = False
    if not activities:
        st.markdown(
            "<h3 style='text-align: center'>Your history is empty 🗑️</h3>", unsafe_allow_html=True)

    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            check_all = st.checkbox("", key="delete-all")
            if check_all:
                st.session_state["all-checked"] = True
            else:
                st.session_state["all-checked"] = False
        with c2:
            st.write('Activity')
        with c3:
            st.write("Date")
        # st.markdown("***")
        st.write("<hr>", unsafe_allow_html=True)
        for i, activity in enumerate(activities):
            col1, col2, col3 = st.columns(3)
            with col1:
                checked = st.checkbox(
                    "", key=i, value=st.session_state["all-checked"])
                if checked:
                    ids.append(activity[0])
                else:
                    if activity[0] in ids:
                        ids.remove(activity[0])
            with col2:
                st.write(activity[1])
            with col3:
                st.write(activity[2])

        st.markdown(" ")
        st.markdown(" ")
        cc1, cc2, cc3 = st.columns([2, 1, 2])
        with cc2:
            delete = st.button("Delete", disabled=not ids,
                               use_container_width=True)
            if delete:
                delete_activities(ids)
                retrieve_history()
                st.session_state["all-checked"] = False
                ids = []
                st.experimental_rerun()

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
                # success = st.success("History deleted successfully")
                # time.sleep(1.5)
                # success.empty()

    # df  = pd.DataFrame(activities, columns=["Id", "Activity", "Date"])
    # df.drop("Id", inplace=True, axis=1)
    # gd = GridOptionsBuilder.from_dataframe(df)
    # gd.configure_pagination(enabled=True)
    # gd.configure_selection(selection_mode="multiple", use_checkbox=True)
    # gd.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=2)
    # gridOptions = gd.build()

    # custom_css = {
    #         ".ag-row": {"font-size": "1rem !important"},
    #         ".ag-header-cell-label": {"font-size": "1rem !important", "padding": "1em"},
    #         ".ag-root.ag-unselectable.ag-layout-normal": {
    #             "padding": "1rem"
    #         }
    #     }

    # _, __ = st.columns(2)
    # with _:
    #     AgGrid(
    #         df, gridOptions=gridOptions,
    #         columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
    #         custom_css=custom_css, update_mode=GridUpdateMode.MODEL_CHANGED,
    #         key="user-aggrid"
    #     )

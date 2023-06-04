import streamlit as st
from db_manager import mark_notification_as_read, delete_single_notification, delete_all_notifications

def notification_page():
    st.markdown("<h1 style='text-align: center'>Notifications 🔔</h1>", unsafe_allow_html=True)

    new = st.session_state["new_notifications"]
    old = st.session_state["old_notifications"]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("New")
        if not new:
            st.write("You dont have any new notification 🗑️")
        else:
            for notification in new:
                with st.expander(f"{notification[1]}  ({notification[3]})"):
                    st.write(f"{notification[2]}")
                    st.markdown("---")
                    
                    st.write(f"<p class='message-title'><span>Name </span> : {notification[5]}</p>", unsafe_allow_html=True)
                    st.write(f"<p class='message-title'><span>Age </span> : {notification[6]}</p>", unsafe_allow_html=True)
                    st.write(f"<p class='message-title'><span>Sex </span> : {notification[7]}</p>", unsafe_allow_html=True)
                    st.write(f"<p class='message-title'><span>Tumor </span> : {notification[8]}</p>", unsafe_allow_html=True)
                    st.markdown(" ")

                    _, __ = st.columns(2)
                    with _:
                        mark_read = st.button("Mark as read", key=f"mark-msg-read {notification[0]}")
                        if mark_read:
                            mark_notification_as_read(notification[0])
                            st.experimental_rerun()
    if old:
        with col2:
            st.subheader("Seen")
            for notification in old:
                with st.expander(f"{notification[1]} ({notification[3]})"):
                    st.write(notification[2])
                    st.markdown("---")
                    
                    st.write(f"<p class='message-title'><span>Name </span> : {notification[5]}</p>", unsafe_allow_html=True)
                    st.write(f"<p class='message-title'><span>Age </span> : {notification[6]}</p>", unsafe_allow_html=True)
                    st.write(f"<p class='message-title'><span>Sex </span> : {notification[7]}</p>", unsafe_allow_html=True)
                    st.write(f"<p class='message-title'><span>Tumor </span> : {notification[8]}</p>", unsafe_allow_html=True)
                    st.markdown(" ")

                    _, __ = st.columns(2)
                    with _:
                        delete = st.button("Delete", key=f"delete-notification {notification[0]}")
                        if delete:
                            delete_single_notification(notification[0])
                            st.experimental_rerun()
            st.markdown("#")
            delete_all_old = st.button("Delete all", key="delete-all-old")
            if delete_all_old:
                delete_all_notifications()
                st.experimental_rerun()
    
    st.markdown('''
            <style>
                div[data-testid="stMarkdownContainer"] > p {
                
                    font-size: 1.4rem;
                }
                .message-title > span{
                    
                    color: #265B94
                }
                
            </style>
        ''', unsafe_allow_html=True)
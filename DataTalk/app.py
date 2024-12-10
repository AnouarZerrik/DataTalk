import streamlit as st
from ui.connection_page import connection_page
from ui.query_interface import init_session_state , query_interface_page

st.set_page_config(page_title="Data Chat")

init_session_state()

if st.session_state.page == "page1":
    connection_page()
elif st.session_state.page == "page2":
    query_interface_page()

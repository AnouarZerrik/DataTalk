import duckdb
import streamlit as st
from core.connection import *
# from core.connection import connect_sqlite, connect_mysql, connect_sqlserver, load_file, load_multi_files
from streamlit_timeline import st_timeline
import google.generativeai as genai
import pandas as pd


genai.configure(api_key='AIzaSyD-0c5kq2lg9ahUWEURKTrPyzy03JjlIYk')
# genai.configure(api_key='AIzaSyBMOqioXZPOI-fcCLT1B0lwFtNznjVPstk')
# genai.configure(api_key='AIzaSyBLdPt9xCo9Ia1vpBuxfCl9EMq0FqXByyI')
# model = genai.GenerativeModel('gemini-1.5-pro-exp-0801')
model = genai.GenerativeModel('gemini-1.5-pro-002')
# model = genai.GenerativeModel('gemini-1.5-flash-002')
# model = genai.GenerativeModel('gemini-1.5-flash-exp-0827')



def init_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "history_chat_code" not in st.session_state:
        st.session_state.history_chat_code = []
    if "history_plot" not in st.session_state:
        st.session_state.history_plot = []
    if "model" not in st.session_state:
        st.session_state.model = genai.GenerativeModel(
            'gemini-1.5-flash-latest')
    if "DataFrame" not in st.session_state:
        st.session_state.DataFrame = pd.DataFrame()
    if "dataframes" not in st.session_state:
        st.session_state.dataframes = []
    if "df_is_changed" not in st.session_state:
        st.session_state.df_is_changed = False
    if "fig" not in st.session_state:
        st.session_state.fig = None
    if "error" not in st.session_state:
        st.session_state.error = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "notebook" not in st.session_state:
        st.session_state.notebook = []
    if "sql_plotly" not in st.session_state:
        st.session_state.sql_plotly = None
    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(
            history=st.session_state.history)
    if "chat_code" not in st.session_state:
        st.session_state.chat_code = model.start_chat(
            history=st.session_state.history_chat_code)
    if "chat_plot" not in st.session_state:
        st.session_state.chat_plot = model.start_chat(
            history=st.session_state.history_plot)
    if "connect" not in st.session_state:
        st.session_state.connect = False
    if "db_type" not in st.session_state:
        st.session_state.db_type = None
    if "db_details" not in st.session_state:
        st.session_state.db_details = None
    if "page" not in st.session_state:
        st.session_state.page = "page1"
    if "df" not in st.session_state:
        st.session_state.df = None

    if "local_namespace" not in st.session_state:
        st.session_state.local_namespace = {}

    if "local_namespace_tmp" not in st.session_state:
        st.session_state.local_namespace_tmp = {}

    if "plots" not in st.session_state:
        st.session_state.plots = []

    if 'dash_active' not in st.session_state:
        st.session_state.dash_active = False

    if 'activate_dashboard' not in st.session_state:
        st.session_state.activate_dashboard = True
    if 'conn' not in st.session_state:
        st.session_state.conn = duckdb.connect()
    if 'schema_changed' not in st.session_state:
        st.session_state.schema_changed = False
    if 'code_for_editor' not in st.session_state:
        st.session_state.code_for_editor = None
    if "code_of_editor" not in st.session_state:
        st.session_state.code_of_editor = None
    if "code_editor_lang" not in st.session_state:
        st.session_state.code_editor_lang = None
    if "call_code" not in st.session_state:
        st.session_state.call_code = False


def connection_page():
    st.title('Data Chat - Source Selection')
    init_session_state()

    source_type = st.selectbox(
        'Select Data Source Type', ('Database', 'File', 'Multi-files','History'))

    if source_type == 'Database':
        db_type = st.selectbox('Select Database Type',
                               ('MySQL', 'SQLite', 'SQL Server'))
        db, db_details = None, None

        if db_type == 'SQLite':
            db, db_details = connect_sqlite()
        elif db_type == 'MySQL':
            db, db_details = connect_mysql()
        elif db_type == 'SQL Server':
            db, db_details = connect_sqlserver()

        if st.button('Connect to Database'):
            if db and db_details:
                st.session_state.connect = True
                st.session_state.db_type = db_type
                st.session_state.db_details = db_details
                st.session_state.page = "page2"
            else:
                st.warning("Please provide all required connection details.")
    elif source_type == 'File':
        st.session_state.df = load_file()
        chat_button = st.button('Chat')
        if st.session_state.df is not None and chat_button:
            st.session_state.db_type = "File"
            st.session_state.page = "page2"
        else:
            st.warning('Select Your File(CSV - EXCEL)')
    elif source_type == 'Multi-files':
        load_multi_files()
        chat_button = st.button('Chat')
        if chat_button and conn_is_empty(st.session_state.conn) is not True:
            st.session_state.db_type = "Files"
            st.session_state.page = "page2"
        else:
            st.warning('Select Your File(CSV - EXCEL)')
    elif source_type == 'History':
        from streamlit_timeline import st_timeline

        items = [
            {"id": 1, "content": "2022-10-20", "start": "2022-10-20"},
            {"id": 2, "content": "2022-10-09", "start": "2022-10-09"},
            {"id": 3, "content": "2022-10-18", "start": "2022-10-18"},
            {"id": 4, "content": "2022-10-16", "start": "2022-10-16"},
            {"id": 5, "content": "2022-10-25", "start": "2022-10-25"},
            {"id": 6, "content": "2022-10-27", "start": "2022-10-27"},
        ]

        timeline = st_timeline(items, groups=[], options={}, height="270px")
        st.subheader("Selected item")
        st.write(timeline)







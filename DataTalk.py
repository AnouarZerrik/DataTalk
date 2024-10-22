from datetime import datetime
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from sqlalchemy.exc import SQLAlchemyError
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import pandas as pd
import re
import tempfile
import shutil
import os
import mysql.connector
import google.generativeai as genai
import sqlite3
import pyodbc
from pyodbc import ProgrammingError
from st_chat_message import message
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
import nbformat as nbf
import io
from contextlib import redirect_stdout
import json
import plotly.io as pio
import duckdb

st.set_page_config(
    page_title="Data Chat",
    # layout="wide"
)

genai.configure(api_key='AIzaSyD-0c5kq2lg9ahUWEURKTrPyzy03JjlIYk')
# genai.configure(api_key='AIzaSyBMOqioXZPOI-fcCLT1B0lwFtNznjVPstk')
# genai.configure(api_key='AIzaSyBLdPt9xCo9Ia1vpBuxfCl9EMq0FqXByyI')
# model = genai.GenerativeModel('gemini-1.5-pro-exp-0801')
model = genai.GenerativeModel('gemini-1.5-pro-002')
# model = genai.GenerativeModel('gemini-1.5-flash-002')
# model = genai.GenerativeModel('gemini-1.5-flash-exp-0827')


# Initialize session state variables
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


# SQLite connection function

def connect_sqlite():
    uploaded_file = st.file_uploader("Upload SQLite Database File")
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_file_path = temp_file.name
        db = SQLDatabase.from_uri(f"sqlite:///./{temp_file_path}")
        st.success(f'Connected to SQLite database: {uploaded_file.name}')
        return db, temp_file_path
    return None, None

# MySQL connection function


def connect_mysql():
    hostname = st.text_input('Hostname', value='localhost')
    user = st.text_input('Username', value='root')
    password = st.text_input('Password', type="password")

    if user and password and hostname:
        try:
            conn = mysql.connector.connect(
                host=hostname, user=user, password=password)
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [database[0] for database in cursor.fetchall()]

            db_options = st.selectbox(
                'Database', databases, index=None, placeholder="Select Database...")

            if db_options:
                mysql_uri = f'mysql+mysqlconnector://{user}:{
                    password}@{hostname}:3306/{db_options}'
                db = SQLDatabase.from_uri(mysql_uri)
                st.success(f'Connected to MySQL database: {db_options}')
                return db, mysql_uri
        except mysql.connector.Error as err:
            st.error(f"Error connecting to MySQL: {err}")
    return None, None

# SQL Server connection function


def connect_sqlserver():
    server = st.text_input('Server', value='ANZER\SQLEXPRESS')
    database = st.text_input('Database', value='AdventureWorksDW2019')
    user = st.text_input('Username')
    password = st.text_input('Password', type="password")

    if (server and database) or (user and password and server and database):
        try:
            sqlserver_uri = f'mssql+pyodbc://{user}:{password}@{
                server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
            db = SQLDatabase.from_uri(sqlserver_uri)
            st.success(f'Connected to SQL Server database: {database}')
            return db, sqlserver_uri
        except pyodbc.Error as err:
            st.error(f"Error connecting to SQL Server: {err}")
    return None, None

# Load CSV or Excel file


def load_file():
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success(f'Loaded file: {uploaded_file.name}')
            return df
        except Exception as e:
            st.error(f"Error loading file: {e}")
    return None


def convert_to_dataframe(file, file_name, file_type):
    """Converts uploaded file to a Pandas DataFrame."""
    try:
        if file_type == "csv":
            df = pd.read_csv(file)
        elif file_type in ("xls", "xlsx"):
            df = pd.read_excel(file)
        else:
            return None, "Unsupported file type"  # Handle unsupported types
        return df, "Success"
    except Exception as e:
        return None, f"Error: {e}"


def replace_special_chars(input_string):
    # Replace all non-alphanumeric characters (except underscores) with underscores
    sanitized_string = re.sub(r'[^a-zA-Z0-9_]', '_', input_string)
    return sanitized_string


def load_multi_files():
    # st.title("Multi-File Uploader with Data Editing")

    uploaded_files = st.file_uploader(
        "Choose CSV or Excel files", type=["csv", "xls", "xlsx"], accept_multiple_files=True
    )

    file_infos = []

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            file_type = os.path.splitext(file_name)[1][1:].lower()
            file_name = replace_special_chars(
                os.path.splitext(file_name)[0].lower())

            # Use expander for better organization
            with st.expander(f"File: {file_name}"):
                st.write(f"**Original Name:** {file_name}")
                new_name = st.text_input(
                    f"New Name (optional):", value=file_name, key=f"name_{file_name}")
                description = st.text_area(
                    "Description (optional):", key=f"desc_{file_name}")

                df, status = convert_to_dataframe(
                    uploaded_file, file_name, file_type)

                st.write(f"**Type:** {file_type}")
                st.write(f"**Conversion Status:** {status}")

                file_infos.append({
                    "original_name": file_name,  # Store the original name
                    "name": new_name,  # Store the potentially modified name
                    "type": file_type,
                    "description": description,
                    "status": status,
                    "dataframe": df,
                })

        if st.button("Submit"):
            if all(info["status"] == "Success" for info in file_infos):
                st.session_state.file_data = file_infos

                for i, table in enumerate(st.session_state.file_data):
                    # table_name = table['name']  # Create unique table names
                    st.session_state.conn.register(
                        table['name'], table['dataframe'])
                    print(f"DataFrame {i} registered as table '{
                          table['name']}'")

                # Example of accessing the updated information:
                # for info in st.session_state.file_data:
                #    st.write(f"Name: {info['name']}, Description: {info['description']}")
                for i, table in enumerate(st.session_state.file_data):
                    query = f"SELECT * FROM {table['name']} limit 5;"
                    st.write(st.session_state.conn.execute(
                        query).fetchdf().head())
                st.success("Files uploaded and converted successfully!")
            else:
                st.error("Some files failed to convert.")

        #     try:
        #         if uploaded_file.name.endswith('.csv'):
        #             df = pd.read_csv(uploaded_file)
        #         else:
        #             df = pd.read_excel(uploaded_file)
        #         st.success(f'Loaded file: {uploaded_file.name}')
        #         return df
        #     except Exception as e:
        #         st.error(f"Error loading file: {e}")
        # return None


def conn_is_empty(conn):
    table_count = conn.execute(
        "SELECT COUNT(*) FROM information_schema.tables").fetchone()[0]

    if table_count > 0:
        return False
    else:
        return True

# Connection page


def connection_page():
    st.title('Data Chat - Source Selection')
    init_session_state()

    source_type = st.selectbox(
        'Select Data Source Type', ('Database', 'File', 'Multi-files'))

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
    else:
        load_multi_files()
        chat_button = st.button('Chat')
        if chat_button and conn_is_empty(st.session_state.conn) is not True:
            st.session_state.db_type = "Files"
            st.session_state.page = "page2"
        else:
            st.warning('Select Your File(CSV - EXCEL)')
# Query Interface page


def query_interface_page():
    st.title('Data Chat - Query Interface')
    st.divider()

    with st.sidebar:
        if st.button('Refresh Chat'):
            st.session_state["messages"] = []
            st.session_state.history = []
            st.session_state.chat = model.start_chat(
                history=st.session_state.history)

        if st.button('Go Back to Data Source Selection'):
            init_session_state()
            st.session_state.page = "page1"
            connection_page()

    if st.session_state.connect or st.session_state.db_type == "File" or st.session_state.db_type == "Files":
        for msg in st.session_state.messages:

            render_message(msg)

            # if msg["role"] == 'ai':
            #     st.chat_message(msg["role"], avatar="🤖").markdown(
            #         msg["content"], unsafe_allow_html=True)
            # elif msg["role"] == 'assistant':
            #     if msg["content"][0] == 0:
            #         if msg["content"][1][1] == 1:
            #             st.chat_message("assistant").plotly_chart(
            #                 msg["content"][1][0], use_container_width=True, theme="streamlit")
            #         elif msg["content"][1][1] == 0:
            #             st.chat_message("assistant").error(
            #                 msg["content"][1][0])
            #         # else:
            #         #     st.chat_message("assistant").warning('No Plotly figure was generated.')
            #     else:
            #         if type(msg["content"][1]) != type(list()):
            #             if type(msg["content"][1]) == type(dict()):
            #                 st.chat_message("assistant").text(msg["content"][1]['result'])
            #             else:
            #                 st.chat_message("assistant").write(msg["content"][1])
            #         else:
            #             with st.chat_message("assistant"):
            #                 for x in list(msg["content"][1])[::-1]:
            #                     st.write(x)
            #                 # st.write(list(msg["content"][1])[0])

            # elif msg["role"] == 'user':
            #     st.chat_message(msg["role"]).write(msg["content"])

        prompt = st.chat_input(
            placeholder="`+` for data manipulation, `-` for plotly")

        if prompt and prompt != '':
            handle_user_input(prompt)
    else:
        st.warning("Please connect to a database or load a file first.")

    if st.session_state.dash_active:
        # Display the form
        options = [f"{fig['number']} - {fig['title']
                                        }" for fig in st.session_state.plots]
        with st.chat_message("assistant"):
            with st.form(key='user_form'):
                dash_plots = st.multiselect("Choose Your Plots", options)
                File_name = st.text_input("Dashboard Name")
                submitted = st.form_submit_button("Submit")
                Cancel = st.form_submit_button("Cancel")
                if submitted and File_name and dash_plots:
                    # Process the form submission
                    extract_numbers = [
                        int(re.search(r'\d+', text).group()
                            ) if re.search(r'\d+', text) else None
                        for text in dash_plots
                    ]
                    filtered_plots = [
                        d for d in st.session_state.plots if d['number'] in extract_numbers
                    ]
                    figures_list = [d['fig'] for d in filtered_plots]
                    fig_titles = [d['title'] for d in filtered_plots]
                    file_path = create_dashboard_html(
                        figures_list, 'Dashboard', fig_titles, File_name)
                    # Add the assistant's message with the markdown link
                    from pathlib import Path

                    # Get the absolute path of a folder
                    folder_path = Path(file_path).resolve()

                    st.session_state.messages.append({
                        "role": "ai",
                        "type": "dash_url",
                        "content": f"[Display {File_name}]({str(folder_path).replace('\\', '/')})"
                        # "content": f"[Display {File_name}](file:///C:/Users/UTENTE/Desktop/Projects/STR+GEMINI/Dash_2024-09-15_01-30-46.html)"
                    })
                    # Reset the flag
                    st.session_state.dash_active = False
                    st.rerun()
                elif Cancel:
                    st.session_state.dash_active = False
                    st.rerun()


def handle_user_input(prompt):
    if prompt[0] == "+":
        if st.session_state.db_type == "File":
            handle_dataframe_manipulation(prompt[1:].strip())
        elif st.session_state.db_type == "Files":
            handle_Files_query(prompt[1:].strip())
        else:
            handle_sql_query(prompt)
    elif prompt[0] == "*":
        handle_general_code_execution(prompt)
    elif prompt[0] == "-":
        handle_plotly_visualization(prompt)
    elif str(prompt).strip() == '/dash':
        st.session_state.dash_active = True
        st.rerun()
    elif str(prompt).strip().startswith('/replace'):
        table_name = str(prompt).replace("/replace", '').strip()
        st.session_state.conn = replace_view_or_table(
            st.session_state.conn, table_name, st.session_state.df)
    elif str(prompt).startswith('/NB'):
        if len(st.session_state.notebook) != 0:
            name_nb = str(prompt).replace("/NB", '').strip()
            convert_list_to_notebook(st.session_state.notebook, name_nb)
            st.success('NoteBook is Created')
        else:
            st.warning('Chat firsatble')
    elif st.session_state.sql_plotly in ['sql', 'plotly', 'dataframe', 'code', 'Files']:
        if st.session_state.sql_plotly == 'sql':
            handle_sql_query(prompt)
        elif st.session_state.sql_plotly == 'dataframe':
            handle_dataframe_manipulation(prompt)
        elif st.session_state.sql_plotly == 'code':
            handle_general_code_execution(prompt)
        elif st.session_state.sql_plotly == 'Files':
            handle_Files_query(prompt)
        else:
            handle_plotly_visualization(prompt)
    else:
        st.warning("Please Select + , - or *")


def handle_sql_query(prompt):
    prompt_template = f"""You are a SQL expert. Given an input question, create a syntactically correct {get_d()} query to run depending on the type of DBMS( {get_d()} ).

    <Restrictions>
    1. DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database. It is not our database.
    2. DO NOT use any SQL Clauses(IS, NOT, IN,..etc) like Aliases.
    </Restrictions>

    <Question>
    {prompt}
    </Question>

    <DATABASE_SCHEMA>
    {get_schema()}.
    </DATABASE_SCHEMA>

    ---

    SQL Query :
    """
    prompt_template_2 = f"""
    <Question>
    {prompt}
    </Question>

    ---

    SQL Query :
    """
    st.session_state.messages.append(
        {"role": "user", "type": "text", "content": prompt})
    if str(prompt).startswith('+'):
        st.chat_message("user").write(f"SQL / {prompt[1:].strip()}")
    else:
        st.chat_message("user").write(f"SQL / {prompt.strip()}")

    if len(st.session_state.messages) <= 2:
        sql = st.session_state.chat.send_message(prompt_template).text
    else:
        sql = st.session_state.chat.send_message(prompt_template_2).text

    query = extract_sql(sql)
    try:
        query = query.replace(";", "")
    except:
        pass

    sql = f"""```sql
    {query}```"""
    st.session_state.messages.append(
        {"role": "ai", "type": "sql", "content": sql})
    st.chat_message("ai", avatar="🤖").markdown(sql)

    df_message = return_df(query)

    if df_message is not None:
        st.session_state.df_is_changed = True

    sql = markdown_to_sql(sql)

    st.session_state.messages.append(
        {"role": "assistant", "type": "df", "content": df_message})
    st.chat_message("assistant").write(df_message)

    st.session_state.DataFrame = st.session_state.df = df_message
    st.session_state.sql_plotly = 'sql'


def get_duckdb_schema_for_llm(db_connection):
    """
    Extracts the DuckDB schema in a format suitable for LLMs.

    Args:
        db_connection: A DuckDB connection object.

    Returns:
        A JSON string representing the schema or None if the database is empty.
    """

    table_names = [row[0] for row in db_connection.execute(
        "PRAGMA show_tables").fetchall()]

    if not table_names:
        return None  # Database is empty

    schema = {}

    for table_name in table_names:
        table_info = db_connection.execute(
            f"PRAGMA table_info('{table_name}')").fetchall()
        columns = []

        for column in table_info:
            column_data = {
                "name": column[1],
                "type": column[2],
                # Convert notnull to nullable (easier for LLMs)
                "nullable": not column[3],
                # Handle potential None values
                "default_value": column[4] if column[4] is not None else None,
                "primary_key": bool(column[5])  # Convert int to boolean
            }
            columns.append(column_data)

        schema[table_name] = {"columns": columns}

    return json.dumps(schema, indent=4)


def handle_Files_query(prompt):
    prompt_template = f"""You are a SQL expert. Given an input question, create a syntactically correct DuckDB query.

    <Restrictions>
    1. DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database. It is not our database.
    2. DO NOT use any SQL Clauses(IS, NOT, IN,..etc) like Aliases.
    </Restrictions>

    <Question>

    {prompt}

    </Question>

    <DATABASE_SCHEMA>

    {get_duckdb_schema_for_llm(st.session_state.conn)}.

    </DATABASE_SCHEMA>

    ---

    SQL Query :
    """

    prompt_template_2 = f"""
    <Question>
    {prompt}
    </Question>



    ---

    SQL Query :
    """
    prompt_template_3 = f"""
    <NEW_DATABASE_SCHEMA>

    {get_duckdb_schema_for_llm(st.session_state.conn)}.

    </NEW_DATABASE_SCHEMA>

    <Question>
    {prompt}
    </Question>

    ---

    SQL Query :
    """
    st.session_state.messages.append(
        {"role": "user", "type": "text", "content": prompt})
    if str(prompt).startswith('+'):
        st.chat_message("user").write(f"SQL / {prompt[1:].strip()}")
    else:
        st.chat_message("user").write(f"SQL / {prompt.strip()}")

    if len(st.session_state.messages) <= 2:
        sql = st.session_state.chat.send_message(prompt_template).text
    if not st.session_state.schema_changed:
        sql = st.session_state.chat.send_message(prompt_template_2).text
    else:
        sql = st.session_state.chat.send_message(prompt_template_3).text
        st.session_state.schema_changed = False

    query = extract_sql(sql)
    try:
        query = query.replace(";", "")
    except:
        pass

    sql = f"""```sql
    {query}```"""
    st.session_state.messages.append(
        {"role": "ai", "type": "sql", "content": sql})
    st.chat_message("ai", avatar="🤖").markdown(sql)

    df_message = st.session_state.conn.execute(query).df()

    if df_message is not None:
        st.session_state.df_is_changed = True

    sql = markdown_to_sql(sql)

    st.session_state.messages.append(
        {"role": "assistant", "type": "df", "content": df_message})
    st.chat_message("assistant").write(df_message)

    st.session_state.DataFrame = st.session_state.df = df_message
    st.session_state.sql_plotly = 'Files'


def replace_view_or_table(con, table_name, df):
    """
    Replaces an existing view or table in DuckDB with a Pandas DataFrame.

    Args:
        con: The DuckDB connection object.
        table_name: The name of the view or table to replace (string).
        df: The Pandas DataFrame to replace the view/table with.
    """
    try:
        con.register(table_name, df)  # Replaces if exists, creates if not
        st.chat_message("ai", avatar="🤖").success(
            f"View/Table '{table_name}' replaced successfully.")
        st.session_state.schema_changed = True

    except Exception as e:  # Handle potential errors (e.g., invalid DataFrame)
        st.chat_message("ai", avatar="🤖").error(
            f"Error replacing view/table '{table_name}': {e}")
    finally:
        return con


def handle_dataframe_manipulation(prompt):
    prompt_template = f"""
    You are an intelligent data notebook that allows users to interact with and manipulate data using natural language.
    You are currently working with a DataFrame named 'df' that contains the following information:

    <DataFrame_info>
    {get_dataframe_info(st.session_state.df)}
    </DataFrame_info>

    The user has requested the following:

    <User_Request>
    {prompt}
    </User_Request>

    Your task is to generate Python code that fulfills the user's request. Adhere to the following guidelines:

    * **Assume the DataFrame 'df' is already loaded.** Do not include any code to load or save the DataFrame.
    * **Focus on data manipulation using pandas.** Avoid using other libraries or external functions.
    * **Provide clear and concise code.** Avoid unnecessary complexity or verbosity.
    * **Prioritize accuracy and efficiency.** Ensure the code produces the correct results and performs optimally.
    * **Comment your code to explain the logic and purpose of each step.** This will help the user understand the code and make modifications if needed.

    Based on the user's request and the DataFrame information, generate the Python code to manipulate the data as requested.

    ---

    # Python Code:
    # """

    # Handle the /backup command first
    if str(prompt) == "/backup":
        if st.session_state.local_namespace_tmp:
            st.session_state.local_namespace = st.session_state.local_namespace_tmp
            st.session_state.DataFrame = st.session_state.local_namespace.get(
                "df", None)
            # st.experimental_rerun()  # Rerun the script to reflect the changes

            st.success("Reverted to the previous result.")
        else:
            st.warning("No previous result to revert to.")
        return  # Exit the function after handling /backup
    if prompt.startswith("/"):
        command = prompt[1:]
        with st.chat_message("assistant"):
            if command == "head":
                st.session_state.messages.append({"role": "assistant", "content": (
                    1, [st.session_state.DataFrame.head(), "**DataFrame Head:**"])})
                st.write("**DataFrame Head:**")
                st.write(st.session_state.DataFrame.head())
            elif command == "describe":
                st.session_state.messages.append({"role": "assistant", "content": (
                    1, [st.session_state.DataFrame.describe(), "**DataFrame Description:**"])})
                st.write("**DataFrame Description:**")
                st.write(st.session_state.DataFrame.describe())
            elif command == "info":
                st.session_state.messages.append({"role": "assistant", "content": (
                    1, [st.session_state.DataFrame.info().to_string(), "**DataFrame Info:**"])})
                st.write("**DataFrame Info:**")
                st.write(st.session_state.DataFrame.info())
            elif command == "shape":
                st.session_state.messages.append({"role": "assistant", "content": (
                    1, [str(st.session_state.DataFrame.shape), "**DataFrame Shape:**"])})
                st.write("**DataFrame Shape:**")
                st.write(st.session_state.DataFrame.shape)
            elif command == "columns":
                st.session_state.messages.append({"role": "assistant", "content": (
                    1, [str(st.session_state.DataFrame.columns.tolist()), "**DataFrame Columns:**"])})
                st.write("**DataFrame Columns:**")
                st.write(st.session_state.DataFrame.columns)
            elif command == "dtypes":
                st.session_state.messages.append({"role": "assistant", "content": (
                    1, [st.session_state.DataFrame.dtypes, "**DataFrame Data Types:**"])})
                st.write("**DataFrame Data Types:**")
                st.write(st.session_state.DataFrame.dtypes)
            elif command == "tail":
                st.session_state.messages.append({"role": "assistant", "content": (
                    1, [st.session_state.DataFrame.tail(), "**DataFrame Tail:**"])})
                st.write("**DataFrame Tail:**")
                st.write(st.session_state.DataFrame.tail())
            elif command == "sample":
                st.session_state.messages.append({"role": "assistant", "content": (
                    1, [st.session_state.DataFrame.sample(), "**DataFrame Sample:**"])})
                st.write("**DataFrame Sample:**")
                st.write(st.session_state.DataFrame.sample())
            elif command == "isnull":
                st.session_state.messages.append({"role": "assistant", "content": (
                    1, [st.session_state.DataFrame.isnull().sum(), "**DataFrame Null Values:**"])})
                st.write("**DataFrame Null Values:**")
                st.write(st.session_state.DataFrame.isnull().sum())
            elif "value_counts" in command:
                column_name = prompt.split("=")[1]
                st.session_state.messages.append({"role": "assistant", "content": (
                    1, [st.session_state.DataFrame[column_name].value_counts(), "**DataFrame value_counts:**"])})
                st.write("**DataFrame Value Counts:**")
                st.write(
                    st.session_state.DataFrame[column_name].value_counts())
            else:
                st.warning("Invalid command.")
        return

    st.session_state.messages.append(
        {"role": "user", "type": "text", "content": prompt})
    if str(prompt).startswith('+'):
        st.chat_message("user").write(f"DataFrame / {prompt[1:].strip()}")
    else:
        st.chat_message("user").write(f"DataFrame / {prompt.strip()}")

    if len(st.session_state.messages) <= 2:
        code = st.session_state.chat.send_message(prompt_template).text
    elif not st.session_state.DataFrame.empty:  # Check if DataFrame is not empty
        prompt_template_2 = f"""
        <result_df_info>
        {get_dataframe_info(st.session_state.DataFrame)}
        </result_df_info>

        <User_Request>
        {prompt}
        </User_Request>

        Python Code:
        """
        code = st.session_state.chat.send_message(prompt_template_2).text
    # else:
    #     code = st.session_state.chat.send_message(prompt_template_2).text

    python_code = extract_code_without_blocks(code)

    # # Initialize local namespace for the first interaction
    # if "local_namespace" not in st.session_state:
    #     st.session_state.local_namespace = {}

    # Execute the code with the persistent local namespace
    result_df, st.session_state.local_namespace, st.session_state.local_namespace_tmp, error = execute_dataframe_code(
        python_code, st.session_state.df, st.session_state.local_namespace
    )

    # Store the backup in the session state
    # st.session_state.local_namespace_tmp = local_namespace_tmp

    if result_df is not None:
        st.session_state.df_is_changed = True

    st.session_state.messages.append(
        {"role": "ai", "type": "code", "content": f"```python\n{python_code}```"})
    st.chat_message("ai", avatar="🤖").markdown(f"```python\n{python_code}```")

    if error:
        st.session_state.messages.append(
            {"role": "assistant", "type": "error", "content": error})
        st.chat_message("assistant").error(error)
    else:
        st.session_state.dataframes.append(result_df)
        st.chat_message("assistant").write(
            f'DataFrame N° {len(st.session_state.dataframes)}')
        st.chat_message("assistant").write(result_df)
        st.session_state.messages.append({"role": "assistant", "type": "df", "content": (
            1, [result_df, f'DataFrame N° {len(st.session_state.dataframes)}'])})
        st.session_state.notebook.append(python_code)

        st.session_state.DataFrame = result_df
        st.session_state.sql_plotly = 'dataframe'


def handle_general_code_execution(prompt):

    if "excute_first_code_prompt" not in st.session_state:
        st.session_state.excute_first_code_prompt = False

    prompt_template = f"""You are an intelligent data notebook that allows users to interact with and manipulate data using Python code.
    You are currently working with a DataFrame named 'df' that contains the following information:

    <DataFrame_info>
    {get_dataframe_info(st.session_state.df)}
    </DataFrame_info>

    The user has requested the following:

    <User_Request>
    {prompt[1:].strip()}
    </User_Request>

    Your task is to generate Python code that fulfills the user's request. Adhere to the following guidelines:

    * **Assume the DataFrame 'df' is already loaded.** Do not include any code to load or save the DataFrame.
    * **Use pandas and other relevant libraries as needed.**
    * **Provide clear and concise code.** Avoid unnecessary complexity or verbosity.
    * **Prioritize accuracy and efficiency.** Ensure the code produces the correct results and performs optimally.
    * **Comment your code to explain the logic and purpose of each step.** This will help the user understand the code and make modifications if needed.

    Based on the user's request and the DataFrame information, generate the Python code to execute the requested operation.

    ---

    Python Code:
 """
    prompt_template_2 = f"""
        <result_df_info>
        {get_dataframe_info(st.session_state.df)}
        </result_df_info>

        <User_Request>
        {prompt}
        </User_Request>

        Python Code:
        """
    # prompt_template_2 = f"""
    #     <result_df_info>
    #     {get_dataframe_info(st.session_state.DataFrame)}
    #     </result_df_info>

    #     <User_Request>
    #     {prompt}
    #     </User_Request>

    #     Python Code:
    #     """

    if str(prompt) == "/backup":
        if st.session_state.local_namespace_tmp:
            st.session_state.local_namespace = st.session_state.local_namespace_tmp
            st.session_state.DataFrame = st.session_state.local_namespace.get(
                "df", None)
            # st.experimental_rerun()  # Rerun the script to reflect the changes

            st.success("Reverted to the previous result.")
        else:
            st.warning("No previous result to revert to.")
        return  # Exit the function after handling /backup

    st.session_state.messages.append(
        {"role": "user", "type": "text", "content": prompt})
    st.chat_message("user").write(f"Code / {prompt[1:].strip()}")

    if not st.session_state.excute_first_code_prompt:
        code = st.session_state.chat_code.send_message(prompt_template).text
        st.session_state.excute_first_code_prompt = True
    else:
        code = st.session_state.chat_code.send_message(prompt_template_2).text

    python_code = extract_code_without_blocks(code)

    result, st.session_state.local_namespace, st.session_state.local_namespace_tmp, error = execute_code(
        python_code, st.session_state.df, st.session_state.local_namespace)

    st.session_state.messages.append(
        {"role": "ai", "type": "code", "content": f"```python\n{python_code}```"})
    st.chat_message("ai", avatar="🤖").markdown(f"```python\n{python_code}```")

    if error:
        st.session_state.messages.append(
            {"role": "assistant", "type": "error", "content": error})
        st.chat_message("assistant").error(error)
    else:
        st.session_state.messages.append(
            {"role": "assistant", "type": "result", "content": result})
        st.chat_message("assistant").text(result)
        st.session_state.notebook.append(python_code)
        st.session_state.df = st.session_state.local_namespace.get('df')

    st.session_state.sql_plotly = 'code'


def handle_plotly_visualization(prompt: str):
    if type(st.session_state.DataFrame) == pd.core.frame.DataFrame:
        try:
            if str(prompt).startswith('-'):
                prompt = str(prompt[1:]).strip()

            prompt_template_plotly = f"""
            Your task is to generate Python code that creates a plot based on the provided dataframe information.

            <plot_type>
            {str(prompt)}
            </plot_type>

            <DataFrame_info>
            {get_dataframe_info(st.session_state.DataFrame)}
            </DataFrame_info>

            <steps>
            1. Carefully review the dataframe information provided in the <df_info> section to understand the structure and content of the dataframe.
            2. Generate Python code to create the specified plot type using the dataframe. Consider the following:
            - Import necessary libraries (e.g., pandas, plotly)
            - Use appropriate Plotly functions to generate the plot based on the <plot_type>
            - Customize the plot (e.g., title, labels, legend, colors) to enhance readability and aesthetics
            - Assign the plot figure to a variable named `fig`
            </steps>

            <restrictions>
            1. Assume that the dataframe is already loaded and accessible using the variable `df`. Do not include code to initialize or create the dataframe.
            2. Use the Plotly library for creating the plot.
            3. Do not include `fig.show()` in your code to display the plot.
            3. Do not include any functions of display or print.
            </restrictions>

            #################

            Here is the Python code :
            """
            prompt_template_2 = f"""
            <plot_type>
                {str(prompt)}
            </plot_type>

            #################

            Here is the Python code :
            """
            if st.session_state.df_is_changed == True:
                st.session_state.history_plot = []
                st.session_state.chat_plot = model.start_chat(
                    history=st.session_state.history_plot)
                res = st.session_state.chat_plot.send_message(
                    prompt_template_plotly)
                st.session_state.df_is_changed = False
            else:
                res = st.session_state.chat_plot.send_message(
                    prompt_template_2)

            code_python = extract_code_without_blocks(res.text)

            external_data = {"df": st.session_state.DataFrame}
            st.session_state.fig, st.session_state.error = generate_fig(
                res.text, external_data)

            st.session_state.messages.append(
                {"role": "user", "type": "text", "content": prompt})

            st.chat_message("user").write(f"Plotly / {str(prompt)}")

            st.session_state.messages.append(
                {"role": "ai", "type": "code", "content": f"""```python\n{code_python}"""})
            st.chat_message("ai", avatar="🤖").markdown(
                f"""```python\n{code_python}""")

            if st.session_state.error is not None:
                st.session_state.messages.append(
                    {"role": "assistant", "type": "erro", "content": st.session_state.error})
                st.chat_message("assistant").error(st.session_state.error)
            elif st.session_state.fig is not None:
                st.session_state.messages.append(
                    {"role": "assistant", "type": "plot", "content": st.session_state.fig})
                st.chat_message("assistant").plotly_chart(
                    st.session_state.fig, use_container_width=True, theme="streamlit")
                data_fig = {'fig': st.session_state.fig,
                            'title': st.session_state.fig.layout.title.text}

                next_number = st.session_state.plots[-1]['number'] + \
                    1 if st.session_state.plots else 1

                data_fig['number'] = next_number

                st.session_state.plots.append(data_fig)

                st.session_state.notebook.append(code_python)
            # else:
            #     st.chat_message("assistant").warning('No Plotly figure was generated.')

            st.session_state.sql_plotly = 'plotly'
        except Exception as e:
            st.warning(e)
    else:
        st.warning("Please Run SQL or PYTHON query result first")

# Helper functions


def get_schema():
    return db.get_table_info()


def get_d():
    global db
    if st.session_state.db_type == 'SQLite':
        db = SQLDatabase.from_uri(f"sqlite:///./{st.session_state.db_details}")
    elif st.session_state.db_type == 'MySQL':
        db = SQLDatabase.from_uri(f"{st.session_state.db_details}")
    elif st.session_state.db_type == 'SQL Server':
        db = SQLDatabase.from_uri(f"{st.session_state.db_details}")
    return db.dialect


def extract_sql(text):
    code_pattern = r'```(?:[^\n]*\n)+?([^`]+)(?:```|$)'
    match = re.search(code_pattern, text, re.DOTALL)
    return match.group(1) if match else None


def markdown_to_sql(markdown_code):
    code_pattern = r'```([a-zA-Z]+)\n(.*?)\n```'
    code_blocks = re.findall(code_pattern, markdown_code, re.DOTALL)
    sql_code_blocks = []
    for lang, code in code_blocks:
        sql_code_blocks.append(f'```sql\n{code}\n```')
    return '\n'.join(sql_code_blocks)


def return_df(query):
    try:
        if st.session_state.db_type == 'MySQL':
            data = pd.read_sql_query(str(query), st.session_state.db_details)
        elif st.session_state.db_type == 'SQLite':
            data = pd.read_sql_query(
                str(query), f"sqlite:///./{st.session_state.db_details}")
        elif st.session_state.db_type == 'SQL Server':
            data = pd.read_sql_query(str(query), st.session_state.db_details)
        df = pd.DataFrame(data)
        return df
    except SQLAlchemyError as e:
        st.chat_message("assistant").write(e)
    except ProgrammingError as e:
        st.chat_message("assistant").write(e)


def get_dataframe_info(df):
    info = {
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.to_dict(),
        "head": df.head().to_json(orient='records', lines=True),
        "isna": df.isna().sum().to_dict()
    }
    return info


def execute_python_code_plotly(code, external_data=None):
    # Create a local namespace
    local_namespace = {}

    # Add external data to the namespace
    if external_data is not None:
        local_namespace.update(external_data)

        # Store external data in a variable 'df'
        if "df" in external_data:
            local_namespace['df'] = external_data["df"]

    # Execute the code in a separate namespace
    try:
        exec(code, globals(), local_namespace)
    except Exception as e:
        error_msg = f"Error executing code: {type(e).__name__}: {str(e)}"
        return None, error_msg

    # Check if a Plotly figure exists
    fig = None
    if 'fig' in local_namespace and isinstance(local_namespace['fig'], go.Figure):
        fig = local_namespace['fig']
    elif any(isinstance(obj, go.Figure) for obj in local_namespace.values()):
        fig = next(obj for obj in local_namespace.values()
                   if isinstance(obj, go.Figure))
    if fig:
        return fig, None

    # No plot was generated
    return None, "No Plotly figure was generated"


def extract_code_without_blocks(string):
    code_pattern = r'```(?:[^\n]*\n)+?([^`]+)(?:```|$)'
    code_matches = re.findall(code_pattern, string)
    return '\n'.join(code_matches)


def generate_fig(code_python, external_data):
    code = extract_code_without_blocks(code_python)
    fig, error = execute_python_code_plotly(code, external_data)
    return fig, error


def render_message(message):
    role = message.get("role")
    msg_type = message.get("type")
    content = message.get("content")

    if role == 'user':
        st.chat_message("user").write(content)
    elif role in ['assistant', 'ai']:
        if msg_type == 'text':
            st.chat_message(role).write(content)
        elif msg_type == 'sql':
            st.chat_message(role).write(content)
        elif msg_type == 'dash_url':
            st.chat_message(role).write(content)
        elif msg_type == 'code':
            st.chat_message(role, avatar="🤖" if role == 'ai' else None).markdown(
                content, unsafe_allow_html=True)
        elif msg_type == 'plot':
            st.chat_message(role).plotly_chart(
                content, use_container_width=True)
        elif msg_type == 'df':
            st.chat_message(role).write(content)
        elif msg_type == 'result':
            st.chat_message(role).text(content)
        elif msg_type == 'error':
            st.chat_message(role).error(content)
        # Add more types as needed


# def execute_code(code, df):
#     local_namespace = {"df": df}
#     try:
#         exec(code, globals(), local_namespace)
#         # Capture printed output
#         import io
#         from contextlib import redirect_stdout
#         with io.StringIO() as buf, redirect_stdout(buf):
#             exec(code, globals(), local_namespace)
#             output = buf.getvalue()

#         # Return the captured output or the result of the last expression
#         if output:
#             return output, None
#         else:
#             return local_namespace.get('result', None), None
#     except Exception as e:
#         error_msg = f"Error executing code: {type(e).__name__}: {str(e)}"
#         return None, error_msg

def execute_code(code, df, local_namespace):
    if not local_namespace:
        local_namespace = {}
        local_namespace["df"] = df

    local_namespace["df"] = df
    local_namespace_tmp = local_namespace.copy()

    try:
        # exec(code, globals(), local_namespace)
        # Capture printed output

        with io.StringIO() as buf, redirect_stdout(buf):
            exec(code, globals(), local_namespace)
            output = buf.getvalue()

        # Return the captured output or the result of the last expression
        if output:
            return output, local_namespace, local_namespace_tmp, None
        else:
            return local_namespace.get('result', None), local_namespace, local_namespace_tmp, None
    except Exception as e:
        error_msg = f"Error executing code: {type(e).__name__}: {str(e)}"
        return None, local_namespace, local_namespace_tmp, error_msg


def execute_dataframe_code(code, df, local_namespace=None):
    if not local_namespace:
        local_namespace = {}
        local_namespace["df"] = df

    # Create a copy of the local namespace to serve as a temporary backup
    local_namespace_tmp = local_namespace.copy()

    # Add the current DataFrame to the local namespace
    # local_namespace["df"] = df

    try:
        exec(code, globals(), local_namespace)
        if 'df' in local_namespace:
            return local_namespace['df'], local_namespace, local_namespace_tmp, None
        else:
            return None, local_namespace, local_namespace_tmp, "Code execution did not produce a 'df'"
    except Exception as e:
        import traceback
        error_type = type(e).__name__
        error_msg = str(e)
        tb = traceback.extract_tb(e.__traceback__)
        line_no = tb[-1].lineno
        return None, local_namespace, local_namespace_tmp, f"Error Type: {error_type}\nLine {line_no}: {error_msg}"


def convert_list_to_notebook(code_list, notebook_name="example_notebook"):
    """
    Convert a list of Python code into a Jupyter Notebook.

    Parameters:
    code_list (list of str): List containing Python code as strings.
    notebook_name (str): The name of the output notebook file (default is "example_notebook.ipynb").
    """
    # Create a new Jupyter Notebook
    nb = nbf.v4.new_notebook()

    # Create code cells and add them to the notebook
    cells = [nbf.v4.new_code_cell(code) for code in code_list]
    nb.cells.extend(cells)

    # Write the notebook to a file
    with open(f'{notebook_name}.ipynb', "w") as f:
        nbf.write(nb, f)


# def create_dashboard_html(figures_list, dashboard_title='Dashboard', fig_titles=None, dashboard_name='Dashboard'):
#     """
#     Generates an enhanced HTML dashboard containing all the plots from the figures_list.

#     Parameters:
#     - figures_list: List of Plotly figure objects.
#     - dashboard_title: Title of the dashboard (default is 'Dashboard').
#     - fig_titles: Optional list of titles for each figure.

#     Returns:
#     - HTML string of the dashboard.
#     """
#     # Prepare data for each figure using to_html instead of to_json
#     figures_html = []
#     for fig in figures_list:
#         fig_html = pio.to_html(fig, include_plotlyjs=False, full_html=False)  # Convert figure to HTML
#         figures_html.append(fig_html)

#     # Determine if the number of figures is odd
#     total_figures = len(figures_list)
#     is_odd = total_figures % 2 != 0

#     # Build the HTML
#     html_parts = []
#     html_parts.append('<!DOCTYPE html>')
#     html_parts.append('<html lang="en">')
#     html_parts.append('<head>')
#     html_parts.append('<meta charset="UTF-8">')
#     html_parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
#     html_parts.append(f'<title>{dashboard_title}</title>')
#     # Include Plotly.js from CDN
#     html_parts.append('<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>')
#     # Include Google Fonts and Font Awesome
#     html_parts.append('<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">')
#     html_parts.append('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">')
#     # Include custom CSS for styling
#     html_parts.append('<style>')
#     # Include the full CSS styling here
#     html_parts.append('''
#     :root {
#         --primary-color: #4e54c8;
#         --secondary-color: #8f94fb;
#         --background-color: #f0f2f5;
#         --text-color: #333;
#         --header-height: 60px;
#         --gradient: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
#     }
#     [data-theme="dark"] {
#         --primary-color: #232526;
#         --secondary-color: #414345;
#         --background-color: #181818;
#         --text-color: #e0e0e0;
#         --gradient: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
#     }
#     body {
#         font-family: 'Roboto', sans-serif;
#         margin: 0;
#         padding: 0;
#         color: var(--text-color);
#         background-color: var(--background-color);
#         transition: background-color 0.3s, color 0.3s;
#     }
#     .header {
#         background: var(--gradient);
#         padding: 0 20px;
#         display: flex;
#         align-items: center;
#         justify-content: space-between;
#         color: white;
#         position: sticky;
#         top: 0;
#         height: var(--header-height);
#         z-index: 100;
#         box-shadow: 0 2px 5px rgba(0,0,0,0.1);
#     }
#     .header .logo {
#         font-size: 1.8em;
#         font-weight: bold;
#     }
#     .header .toggle-button {
#         background: none;
#         border: none;
#         color: white;
#         font-size: 1.5em;
#         cursor: pointer;
#         margin-left: 15px;
#         transition: transform 0.3s, color 0.3s;
#     }
#     .header .toggle-button:hover {
#         transform: scale(1.2);
#         color: #ffd700;
#     }
#     .sidebar {
#         position: fixed;
#         top: var(--header-height);
#         left: -260px;
#         width: 240px;
#         background: var(--gradient);
#         padding-top: 20px;
#         height: calc(100% - var(--header-height));
#         overflow-x: hidden;
#         transition: left 0.4s ease;
#         z-index: 99;
#         box-shadow: 2px 0 5px rgba(0,0,0,0.1);
#     }
#     .sidebar.active {
#         left: 0;
#     }
#     .sidebar .toggle-sidebar {
#         position: absolute;
#         top: 20px;
#         right: -35px;
#         background: var(--gradient);
#         color: white;
#         padding: 12px;
#         border-radius: 50%;
#         cursor: pointer;
#         box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
#         transition: transform 0.3s;
#     }
#     .sidebar .toggle-sidebar:hover {
#         transform: rotate(90deg);
#     }
#     .sidebar a {
#         padding: 15px 20px;
#         text-decoration: none;
#         font-size: 1em;
#         color: white;
#         display: flex;
#         align-items: center;
#         transition: background-color 0.2s, padding-left 0.3s;
#     }
#     .sidebar a:hover {
#         background-color: rgba(255, 255, 255, 0.1);
#         padding-left: 30px;
#     }
#     .sidebar a i {
#         margin-right: 10px;
#     }
#     .content {
#         margin-left: 20px;
#         padding: 80px 30px 30px 30px;
#         transition: margin-left 0.4s ease;
#     }
#     .content.shifted {
#         margin-left: 260px;
#     }
#     .figure {
#         margin-bottom: 50px;
#         background-color: white;
#         padding: 20px;
#         border-radius: 15px;
#         box-sizing: border-box;
#         box-shadow: 0 5px 15px rgba(0,0,0,0.1);
#         transition: background-color 0.3s, box-shadow 0.3s, transform 0.3s;
#     }
#     [data-theme="dark"] .figure {
#         background-color: #1e1e1e;
#     }
#     .figure:hover {
#         box-shadow: 0 8px 25px rgba(0,0,0,0.2);
#         transform: translateY(-5px);
#     }
#     .figure-title {
#         text-align: center;
#         font-weight: bold;
#         margin-bottom: 20px;
#         font-size: 1.5em;
#         color: var(--text-color);
#     }
#     .footer {
#         text-align: center;
#         padding: 20px;
#         background: var(--gradient);
#         color: white;
#         position: relative;
#     }
#     .footer::before {
#         content: "";
#         position: absolute;
#         top: -20px;
#         left: 0;
#         right: 0;
#         height: 20px;
#         background: linear-gradient(to top, rgba(0,0,0,0.1), transparent);
#     }
#     /* Two-column grid for figures */
#     .grid-container {
#         display: grid;
#         grid-template-columns: repeat(2, 1fr);
#         grid-gap: 20px;
#     }
#     /* Make last item span two columns if total number is odd */
#     .grid-container .full-width {
#         grid-column: span 2;
#     }
#     /* Adjust to one column on smaller screens */
#     @media screen and (max-width: 768px) {
#         .header {
#             flex-direction: column;
#             align-items: flex-start;
#             height: auto;
#             padding: 10px 20px;
#         }
#         .header .toggle-buttons {
#             margin-top: 10px;
#             width: 100%;
#             display: flex;
#             justify-content: space-between;
#         }
#         .content {
#             margin-left: 0;
#             padding: 100px 20px 20px 20px;
#         }
#         .sidebar {
#             width: 100%;
#             height: calc(100% - var(--header-height));
#             position: fixed;
#             top: var(--header-height);
#             left: -100%;
#         }
#         .sidebar.active {
#             left: 0;
#         }
#         .content.shifted {
#             margin-left: 0;
#         }
#         /* Change grid to one column on small screens */
#         .grid-container {
#             grid-template-columns: 1fr;
#         }
#         /* Ensure full-width items still occupy full width */
#         .grid-container .full-width {
#             grid-column: span 1;
#         }
#     }
#     ''')
#     html_parts.append('</style>')
#     html_parts.append('</head>')
#     html_parts.append('<body>')

#     # Header
#     html_parts.append(f'''
#     <div class="header">
#         <div class="logo">{dashboard_title}</div>
#         <div class="toggle-buttons">
#             <button class="toggle-button" onclick="toggleDarkMode()" title="Toggle Dark Mode">
#                 <i class="fas fa-adjust"></i>
#             </button>
#             <button class="toggle-button" onclick="toggleSidebar()" title="Toggle Sidebar">
#                 <i class="fas fa-bars"></i>
#             </button>
#         </div>
#     </div>
#     ''')

#     # Sidebar with navigation links
#     html_parts.append('<div class="sidebar" id="sidebar">')
#     html_parts.append('<div class="toggle-sidebar" onclick="toggleSidebar()" title="Close Sidebar"><i class="fas fa-times"></i></div>')
#     if fig_titles:
#         for i, title in enumerate(fig_titles):
#             html_parts.append(f'<a href="#figure-{i}"><i class="fas fa-chart-bar"></i> {title}</a>')
#     else:
#         for i in range(len(figures_list)):
#             html_parts.append(f'<a href="#figure-{i}"><i class="fas fa-chart-bar"></i> Figure {i+1}</a>')
#     html_parts.append('</div>')

#     # Main content
#     html_parts.append('<div class="content" id="content">')
#     html_parts.append('<div class="grid-container">')
#     for i in range(len(figures_html)):
#         # Determine if this is the last item and if total figures are odd
#         last_item = (i == total_figures - 1) and is_odd
#         figure_class = "figure"
#         if last_item:
#             figure_class += " full-width"
#         html_parts.append(f'<div class="{figure_class}" id="figure-{i}">')
#         if fig_titles and i < len(fig_titles):
#             html_parts.append(f'<div class="figure-title">{fig_titles[i]}</div>')
#         else:
#             html_parts.append(f'<div class="figure-title">Figure {i+1}</div>')
#         # Insert the figure HTML
#         html_parts.append(figures_html[i])
#         html_parts.append('</div>')
#     html_parts.append('</div>')  # Close grid-container
#     html_parts.append('</div>')  # Close content

#     # Footer
#     html_parts.append('<div class="footer">&copy; 2023 Your Company</div>')

#     # JavaScript for dark mode toggle and sidebar interactions
#     html_parts.append('''
#     <script>
#     // Function to toggle dark mode
#     function toggleDarkMode() {
#         var body = document.body;
#         if (body.getAttribute('data-theme') === 'dark') {
#             body.removeAttribute('data-theme');
#             localStorage.removeItem('theme');
#         } else {
#             body.setAttribute('data-theme', 'dark');
#             localStorage.setItem('theme', 'dark');
#         }
#     }

#     // Sidebar toggle
#     function toggleSidebar() {
#         var sidebar = document.getElementById('sidebar');
#         var content = document.getElementById('content');
#         sidebar.classList.toggle('active');
#         content.classList.toggle('shifted');
#     }

#     // Remember theme preference
#     window.onload = function() {
#         if (localStorage.getItem('theme') === 'dark') {
#             document.body.setAttribute('data-theme', 'dark');
#         }
#     }
#     </script>
#     ''')

#     html_parts.append('</body>')
#     html_parts.append('</html>')

#     html = '\n'.join(html_parts)

#     # Save HTML to file
#     now = datetime.now()
#     filename_date = now.strftime("%Y-%m-%d_%H-%M-%S")
#     file_name = f"{dashboard_name}_{filename_date}.html"

#     with open(file_name, 'w', encoding='utf-8') as f:
#         f.write(html)

#     return file_name


def create_dashboard_html(figures_list, dashboard_title='Dashboard', fig_titles=None, dashboard_name='Dashboard'):
    """
    Generates an enhanced HTML dashboard containing all the plots from the figures_list.

    Parameters:
    - figures_list: List of Plotly figure objects.
    - dashboard_title: Title of the dashboard (default is 'Dashboard').
    - fig_titles: Optional list of titles for each figure.

    Returns:
    - HTML string of the dashboard.
    """
    # Prepare data for each figure
    figures_data = []
    for fig in figures_list:
        fig_json_str = fig.to_json()  # Serialize the figure to JSON string
        # Convert JSON string to Python dict
        fig_json = json.loads(fig_json_str)
        figures_data.append(fig_json)

    # Determine if the number of figures is odd
    total_figures = len(figures_list)
    is_odd = total_figures % 2 != 0

    # Build the HTML
    html_parts = []
    html_parts.append('<!DOCTYPE html>')
    html_parts.append('<html lang="en">')
    html_parts.append('<head>')
    html_parts.append('<meta charset="UTF-8">')
    html_parts.append(
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html_parts.append(f'<title>{dashboard_title}</title>')
    # Include Plotly.js from CDN
    html_parts.append(
        '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>')
    # Include Google Fonts and Font Awesome
    html_parts.append(
        '<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">')
    html_parts.append(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">')
    # Include custom CSS for styling
    html_parts.append('<style>')
    # Include the full CSS styling here
    html_parts.append('''
    :root {
        --primary-color: #4e54c8;
        --secondary-color: #8f94fb;
        --background-color: #f0f2f5;
        --text-color: #333;
        --header-height: 60px;
        --gradient: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    }
    [data-theme="dark"] {
        --primary-color: #232526;
        --secondary-color: #414345;
        --background-color: #181818;
        --text-color: #e0e0e0;
        --gradient: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    }
    body {
        font-family: 'Roboto', sans-serif;
        margin: 0;
        padding: 0;
        color: var(--text-color);
        background-color: var(--background-color);
        transition: background-color 0.3s, color 0.3s;
    }
    .header {
        background: var(--gradient);
        padding: 0 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: white;
        position: sticky;
        top: 0;
        height: var(--header-height);
        z-index: 100;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .header .logo {
        font-size: 1.8em;
        font-weight: bold;
    }
    .header .toggle-button {
        background: none;
        border: none;
        color: white;
        font-size: 1.5em;
        cursor: pointer;
        margin-left: 15px;
        transition: transform 0.3s, color 0.3s;
    }
    .header .toggle-button:hover {
        transform: scale(1.2);
        color: #ffd700;
    }
    .sidebar {
        position: fixed;
        top: var(--header-height);
        left: -260px;
        width: 240px;
        background: var(--gradient);
        padding-top: 20px;
        height: calc(100% - var(--header-height));
        overflow-x: hidden;
        transition: left 0.4s ease;
        z-index: 99;
        box-shadow: 2px 0 5px rgba(0,0,0,0.1);
    }
    .sidebar.active {
        left: 0;
    }
    .sidebar .toggle-sidebar {
        position: absolute;
        top: 20px;
        right: -35px;
        background: var(--gradient);
        color: white;
        padding: 12px;
        border-radius: 50%;
        cursor: pointer;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        transition: transform 0.3s;
    }
    .sidebar .toggle-sidebar:hover {
        transform: rotate(90deg);
    }
    .sidebar a {
        padding: 15px 20px;
        text-decoration: none;
        font-size: 1em;
        color: white;
        display: flex;
        align-items: center;
        transition: background-color 0.2s, padding-left 0.3s;
    }
    .sidebar a:hover {
        background-color: rgba(255, 255, 255, 0.1);
        padding-left: 30px;
    }
    .sidebar a i {
        margin-right: 10px;
    }
    .content {
        margin-left: 20px;
        padding: 80px 30px 30px 30px;
        transition: margin-left 0.4s ease;
    }
    .content.shifted {
        margin-left: 260px;
    }
    .figure {
        margin-bottom: 50px;
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-sizing: border-box;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: background-color 0.3s, box-shadow 0.3s, transform 0.3s;
    }
    [data-theme="dark"] .figure {
        background-color: #1e1e1e;
    }
    .figure:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        transform: translateY(-5px);
    }
    .figure-title {
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
        font-size: 1.5em;
        color: var(--text-color);
    }
    .footer {
        text-align: center;
        padding: 20px;
        background: var(--gradient);
        color: white;
        position: relative;
    }
    .footer::before {
        content: "";
        position: absolute;
        top: -20px;
        left: 0;
        right: 0;
        height: 20px;
        background: linear-gradient(to top, rgba(0,0,0,0.1), transparent);
    }
    /* Two-column grid for figures */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        grid-gap: 20px;
    }
    /* Make last item span two columns if total number is odd */
    .grid-container .full-width {
        grid-column: span 2;
    }
    /* Adjust to one column on smaller screens */
    @media screen and (max-width: 768px) {
        .header {
            flex-direction: column;
            align-items: flex-start;
            height: auto;
            padding: 10px 20px;
        }
        .header .toggle-buttons {
            margin-top: 10px;
            width: 100%;
            display: flex;
            justify-content: space-between;
        }
        .content {
            margin-left: 0;
            padding: 100px 20px 20px 20px;
        }
        .sidebar {
            width: 100%;
            height: calc(100% - var(--header-height));
            position: fixed;
            top: var(--header-height);
            left: -100%;
        }
        .sidebar.active {
            left: 0;
        }
        .content.shifted {
            margin-left: 0;
        }
        /* Change grid to one column on small screens */
        .grid-container {
            grid-template-columns: 1fr;
        }
        /* Ensure full-width items still occupy full width */
        .grid-container .full-width {
            grid-column: span 1;
        }
    }
    ''')
    html_parts.append('</style>')
    html_parts.append('</head>')
    html_parts.append('<body>')
    # Header
    html_parts.append(f'''
    <div class="header">
        <div class="logo">{dashboard_title}</div>
        <div class="toggle-buttons">
            <button class="toggle-button" onclick="toggleDarkMode()" title="Toggle Dark Mode">
                <i class="fas fa-adjust"></i>
            </button>
            <button class="toggle-button" onclick="toggleSidebar()" title="Toggle Sidebar">
                <i class="fas fa-bars"></i>
            </button>
        </div>
    </div>
    ''')
    # Sidebar with navigation links
    html_parts.append('<div class="sidebar" id="sidebar">')
    html_parts.append(
        '<div class="toggle-sidebar" onclick="toggleSidebar()" title="Close Sidebar"><i class="fas fa-times"></i></div>')
    if fig_titles:
        for i, title in enumerate(fig_titles):
            html_parts.append(
                f'<a href="#figure-{i}"><i class="fas fa-chart-bar"></i> {title}</a>')
    else:
        for i in range(len(figures_list)):
            html_parts.append(
                f'<a href="#figure-{i}"><i class="fas fa-chart-bar"></i> Figure {i+1}</a>')
    html_parts.append('</div>')
    # Main content
    html_parts.append('<div class="content" id="content">')
    html_parts.append('<div class="grid-container">')
    for i in range(len(figures_data)):
        # Determine if this is the last item and if total figures are odd
        last_item = (i == total_figures - 1) and is_odd
        figure_class = "figure"
        if last_item:
            figure_class += " full-width"
        html_parts.append(f'<div class="{figure_class}" id="figure-{i}">')
        if fig_titles and i < len(fig_titles):
            html_parts.append(
                f'<div class="figure-title">{fig_titles[i]}</div>')
        elif not fig_titles:
            html_parts.append(f'<div class="figure-title">Figure {i+1}</div>')
        html_parts.append(f'<div id="plot-{i}"></div>')
        html_parts.append('</div>')
    html_parts.append('</div>')  # Close grid-container
    html_parts.append('</div>')  # Close content
    # Footer
    html_parts.append('<div class="footer">&copy; 2023 Your Company</div>')
    # JavaScript for interactivity and plots
    html_parts.append('<script>')
    # Include the plot data and layout
    html_parts.append('var figures = [];')
    for i, fig_json in enumerate(figures_data):
        fig_json_str = json.dumps(fig_json)
        html_parts.append(f'figures[{i}] = {fig_json_str};')
    html_parts.append('''
    // Function to render all plots
    function renderPlots(template) {
        for (var i = 0; i < figures.length; i++) {
            var fig = figures[i];
            var config = {responsive: true};
            // Apply the template
            if (!fig.layout) fig.layout = {};
            fig.layout.template = template;
            Plotly.newPlot('plot-' + i, fig.data, fig.layout, config);
        }
    }
    // Function to resize all plots
    function resizePlots() {
        for (var i = 0; i < figures.length; i++) {
            Plotly.Plots.resize(document.getElementById('plot-' + i));
        }
    }
    // Initial rendering of plots
    var initialTemplate = (localStorage.getItem('theme') === 'dark') ? 'plotly_dark' : 'plotly';
    renderPlots(initialTemplate);
    // Dark mode toggle
    function toggleDarkMode() {
        var body = document.body;
        var newTemplate = 'plotly';
        if (body.getAttribute('data-theme') === 'dark') {
            body.removeAttribute('data-theme');
            localStorage.removeItem('theme');
            newTemplate = 'plotly';
        } else {
            body.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            newTemplate = 'plotly_dark';
        }
        // Re-render plots with new template
        renderPlots(newTemplate);
    }
    // Remember theme preference
    window.onload = function() {
        if (localStorage.getItem('theme') === 'dark') {
            document.body.setAttribute('data-theme', 'dark');
        }
        var initialTemplate = (localStorage.getItem('theme') === 'dark') ? 'plotly_dark' : 'plotly';
        renderPlots(initialTemplate);
    }
    // Sidebar toggle
    function toggleSidebar() {
        var sidebar = document.getElementById('sidebar');
        var content = document.getElementById('content');
        sidebar.classList.toggle('active');
        content.classList.toggle('shifted');
        // Wait for the CSS transition to finish before resizing plots
        setTimeout(function() {
            resizePlots();
        }, 400);
    }
    // Resize plots on window resize
    window.addEventListener('resize', resizePlots);
    // Smooth scrolling
    document.querySelectorAll('.sidebar a').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            if (window.innerWidth <= 768) {
                toggleSidebar(); // Close sidebar on link click for mobile
            }
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
    </script>
    ''')
    html_parts.append('</body>')
    html_parts.append('</html>')

    html = '\n'.join(html_parts)
    from datetime import datetime

# Get current date and time
    now = datetime.now()

    # Format it in a suitable way for filenames (e.g., YYYY-MM-DD_HH-MM-SS)
    filename_date = now.strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{dashboard_name}_{filename_date}.html"
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(html)

    return file_name


# Main app logic


def main():
    init_session_state()

    if st.session_state.page == "page1":
        connection_page()
    elif st.session_state.page == "page2":
        query_interface_page()


if __name__ == "__main__":
    main()

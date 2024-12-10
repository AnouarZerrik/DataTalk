import tempfile
import pandas as pd
from langchain_community.utilities import SQLDatabase
import mysql.connector
import pyodbc
import re
import os
import sqlite3
import duckdb
import streamlit as st


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




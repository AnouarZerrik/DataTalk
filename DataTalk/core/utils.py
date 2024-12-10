import json
import re
import streamlit as st
from langchain_community.utilities import SQLDatabase



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

def get_dataframe_info(df):
    info = {
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.to_dict(),
        "head": df.head().to_json(orient='records', lines=True),
        "tail": df.tail().to_json(orient='records', lines=True),
        "isna": df.isna().sum().to_dict()
    }
    return info

def extract_code_without_blocks(string):
    code_pattern = r'```(?:[^\n]*\n)+?([^`]+)(?:```|$)'
    code_matches = re.findall(code_pattern, string)
    return '\n'.join(code_matches)

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












import pandas as pd
import io
from contextlib import redirect_stdout
import traceback
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError
from pyodbc import ProgrammingError
from core.utils import *




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
    
    
    
    
    

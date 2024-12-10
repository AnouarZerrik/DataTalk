import json
import google.generativeai as genai
from core.utils import *
from core.execution import *
from core.visualization import *
import streamlit as st
import google.generativeai as genai
import pandas as pd


genai.configure(api_key='AIzaSyD-0c5kq2lg9ahUWEURKTrPyzy03JjlIYk')
# genai.configure(api_key='AIzaSyBMOqioXZPOI-fcCLT1B0lwFtNznjVPstk')
# genai.configure(api_key='AIzaSyBLdPt9xCo9Ia1vpBuxfCl9EMq0FqXByyI')
# model = genai.GenerativeModel('gemini-1.5-pro-exp-0801')
model = genai.GenerativeModel('gemini-1.5-pro-002')
# model = genai.GenerativeModel('gemini-1.5-flash-002')
# model = genai.GenerativeModel('gemini-1.5-flash-exp-0827')


def handle_sql_query(prompt):
    # prompt_template = f"""You are a SQL expert. Given an input question, create a syntactically correct {get_d()} query to run depending on the type of DBMS( {get_d()} ).

    # <Restrictions>
    # 1. DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database. It is not our database.
    # 2. DO NOT use any SQL Clauses(IS, NOT, IN,..etc) like Aliases.
    # 3. Use Aliases for rename the tables.
    # 4. Always give a names for the result columns.
    # </Restrictions>

    # <Question>
    # {prompt}
    # </Question>

    # <DATABASE_SCHEMA>
    # {get_schema()}.
    # </DATABASE_SCHEMA>

    # ---

    # SQL Query :
    # """
    prompt_template = f"""You are a SQL expert. Create a syntactically correct {get_d()} query based on the input question.
    
    <CONTEXT>
    - Database Type: {get_d()}
    </CONTEXT>

    <VALIDATION_RULES>
    1. NO DML statements (INSERT, UPDATE, DELETE, DROP etc.)
    2. NO implicit SQL clauses (IS, NOT, IN) as aliases
    3. MUST use table aliases (e.g., SELECT t.column FROM table t)
    4. MUST provide column aliases for calculated fields
    5. AVOID using * - explicitly list needed columns
    6. Add comments for complex logic
    </VALIDATION_RULES>

    <FORMATTING>
    1. Use uppercase for SQL keywords
    2. Use proper indentation for readability
    3. Break long queries into multiple lines
    4. Example:
        SELECT 
            t.column_name AS field_name,
            COUNT(t.id) AS record_count
        FROM table_name t
        GROUP BY t.column_name
    </FORMATTING>

    <QUESTION>
    {prompt}
    </QUESTION>

    <DATABASE_SCHEMA>
    {get_schema()}
    </DATABASE_SCHEMA>

    SQL Query:
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
    sql_ai = sql
    query = extract_sql(sql)
    try:
        query = query.replace(";", "")
    except:
        pass
    
    
    try :
        sql = f"""```sql
        {query}```"""
        st.session_state.messages.append(
            {"role": "ai", "type": "sql", "content": sql})
        st.chat_message("ai", avatar="🤖").markdown(sql)

        df_message = return_df(query)

        if df_message is not None:
            st.session_state.df_is_changed = True

        sql = markdown_to_sql(sql)
        
        st.session_state.code_for_editor = query


        st.session_state.messages.append(
            {"role": "assistant", "type": "df", "content": df_message})
        st.chat_message("assistant").write(df_message)

        st.session_state.DataFrame = st.session_state.df = df_message
        st.session_state.sql_plotly = 'sql'
        st.session_state.code_editor_lang = 'sql'
    except Exception as e:
        st.chat_message("assistant").error(e)
        print(sql_ai)

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

            # prompt_template_plotly = f"""
            # Your task is to generate Python code that creates a plot based on the provided dataframe information.

            # <plot_type>
            # {str(prompt)}
            # </plot_type>

            # <DataFrame_info>
            # {get_dataframe_info(st.session_state.DataFrame)}
            # </DataFrame_info>

            # <steps>
            # 1. Carefully review the dataframe information provided in the <df_info> section to understand the structure and content of the dataframe.
            # 2. Generate Python code to create the specified plot type using the dataframe. Consider the following:
            # 3. Import necessary libraries (e.g., pandas, plotly)
            # 4. Use only import plotly.graph_objects as go for generate plots
            # 4. Use appropriate Plotly functions to generate the plot based on the <plot_type>
            # 5. Customize the plot (e.g., title, labels, legend, colors) to enhance readability and aesthetics
            # 6. Assign the plot figure to a variable named `fig`
            # </steps>

            # <restrictions>
            # 1. Assume that the dataframe is already loaded and accessible using the variable `df`. Do not include code to initialize or create the dataframe.
            # 2. Use the Plotly library for creating the plot.
            # 3. Do not include `fig.show()` in your code to display the plot.
            # 3. Do not include any functions of display or print.
            # </restrictions>

            # #################

            # Here is the Python code :
            # """
            
            prompt_template_plotly = f"""You are a Plotly visualization expert. Create a plot using the existing DataFrame.

    <CONTEXT>
    Current DataFrame Info:
    {get_dataframe_info(st.session_state.DataFrame)}
    </CONTEXT>

    <PLOT_REQUEST>
    {str(prompt)}
    </PLOT_REQUEST>

    <VALIDATION_RULES>
    1. Use ONLY the existing DataFrame 'df' - DO NOT create new data
    2. Use ONLY plotly.graph_objects as go
    3. Return ONLY the plot generation code
    4. All plots must be responsive and interactive
    5. Include hover data where appropriate
    6. Use consistent color schemes
    </VALIDATION_RULES>

    <PLOT_GUIDELINES>
    1. Add clear titles and axis labels
    2. Include units where applicable  
    3. Format numbers appropriately
    4. Add hover templates for interactivity
    5. Use appropriate chart types for data
    6. Consider colorblind-friendly palettes
    </PLOT_GUIDELINES>

    <CODE_STRUCTURE>
    1. Import statement: import plotly.graph_objects as go
    2. Create figure: fig = go.Figure()
    3. Add traces with existing df data
    4. Update layout with proper styling
    
    Example:
    ```python
    import plotly.graph_objects as go
    
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df['x_column'],
            y=df['y_column'],
            name='Series Name'
        )
    )
    fig.update_layout(
        title='Plot Title',
        xaxis_title='X Axis',
        yaxis_title='Y Axis'
    )
    ```
    </CODE_STRUCTURE>

    <RESTRICTIONS>
    1. DO NOT create sample data or new DataFrames
    2. DO NOT use df.show() or print statements
    3. DO NOT use fig.show()
    4. USE ONLY the existing 'df' DataFrame
    5. DO NOT import pandas or numpy
    6. DO NOT create helper functions
    </RESTRICTIONS>

    Generate the Python code:
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
            st.session_state.code_editor_lang = "plotly"
            st.session_state.code_for_editor = code_python
            
        except Exception as e:
            st.warning(e)
            print(res.text)
    else:
        st.warning("Please Run SQL or PYTHON query result first")


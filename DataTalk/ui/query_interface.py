import streamlit as st
from core.llm import *
from core.visualization import *
from core.execution import *
from core.utils import *
from code_editor import code_editor
from ui.connection_page import init_session_state, connection_page
import google.generativeai as genai
import json
import re
import time
import nbformat as nbf

genai.configure(api_key='AIzaSyD-0c5kq2lg9ahUWEURKTrPyzy03JjlIYk')
# genai.configure(api_key='AIzaSyBMOqioXZPOI-fcCLT1B0lwFtNznjVPstk')
# genai.configure(api_key='AIzaSyBLdPt9xCo9Ia1vpBuxfCl9EMq0FqXByyI')
# model = genai.GenerativeModel('gemini-1.5-pro-exp-0801')
model = genai.GenerativeModel('gemini-1.5-pro-002')


@st.fragment
def render_chat_history(messages):
    """Renders the chat history UI inside an st.fragment."""
    for msg in messages:
        render_message(msg)

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
        # for msg in st.session_state.messages:

        #     render_message(msg)
        
        render_chat_history(st.session_state.messages)

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
            placeholder="`+` for data manipulation, `-` for plotly and `*` for code handling")

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
                    # file_path = create_enhanced_dashboard(
                    #     figures_list, 'Dashboard', fig_titles, File_name)
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

    if st.session_state.call_code:
        if st.session_state.code_editor_lang == 'sql':
            display_code_editor(str(st.session_state.code_for_editor), "sql")
        elif st.session_state.code_editor_lang == 'plotly':
            display_code_editor(str(st.session_state.code_for_editor), "plotly")
        


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
    elif str(prompt).strip() == '/editor':
        st.session_state.call_code = True
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
            st.chat_message(role, avatar="👨‍💻" if role == 'ai' else None).markdown(
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


def display_code_editor(code: str = "", lang: str = "python"):
    """
    Displays and handles interactions with a code editor.
    """
    second_lang = lang
    if lang == "plotly":
        lang = "python"

    # Button settings for the code editor
    btn_settings_editor_btns = """
    [
      {
        "name": "Copy",
        "feather": "Copy",
        "hasText": true,
        "alwaysOn": true,
        "commands": [
          "copyAll",
          [
            "infoMessage",
            {
              "text": "Copied to clipboard!",
              "timeout": 2500,
              "classToggle": "show"
            }
          ]
        ],
        "style": {
          "top": "0rem",
          "right": "0.4rem"
        }
      },
      {
        "name": "Run",
        "feather": "Play",
        "primary": true,
        "hasText": true,
        "showWithIcon": true,
        "commands": [
          "submit"
        ],
        "style": {
          "bottom": "0.44rem",
          "right": "0.4rem"
        }
      },
      {
        "name": "Cancel",
        "feather": "XCircle",
        "primary": true,
        "hasText": true,
        "showWithIcon": true,
        "commands": [
          "cancel",
          [
            "response",
            "cancelled"
          ]
        ],
        "style": {
          "bottom": "3rem",
          "right": "0.4rem"
        }
      }
    ]
    """
    css_string = '''
background-color: #bee1e5;

body > #root .ace-streamlit-dark~& {
   background-color: #262830;
}

.ace-streamlit-dark~& span {
   color: #fff;
   opacity: 0.6;
}

span {
   color: #000;
   opacity: 0.5;
}

.code_editor-info.message {
   width: inherit;
   margin-right: 75px;
   order: 2;
   text-align: center;
   opacity: 0;
   transition: opacity 0.7s ease-out;
}

.code_editor-info.message.show {
   opacity: 0.6;
}

.ace-streamlit-dark~& .code_editor-info.message.show {
   opacity: 0.5;
}
'''
    info_bar = {
        "name": "language info",
        "css": css_string,
        "style": {
            "order": "1",
            "display": "flex",
            "flexDirection": "row",
            "alignItems": "center",
            "width": "100%",
            "height": "2.5rem",
            "padding": "0rem 0.75rem",
            "borderRadius": "8px 8px 0px 0px",
            "zIndex": "9993"
        },
        "info": [{
            "name": lang,
            "style": {"width": "100px"}
        }]
    }
    btns = json.loads(btn_settings_editor_btns)

#     initial_code = """# Enter your Python code here
# print("Hello from code editor!")
# """
    st.session_state.code_of_editor = code_editor(code, focus=True, lang=lang, height=(
        19, 22), buttons=btns, options={"wrap": True}, info=info_bar)

    if st.session_state.code_of_editor['type'] == "submit" and len(st.session_state.code_of_editor['text']) != 0:
        if second_lang == "plotly":
            lang = second_lang
            
            
        if lang == "sql":
            try:
                sql = f"""```sql
                {st.session_state.code_of_editor['text']}"""
                print(f"sql : {sql}")
                st.session_state.messages.append(
                    {"role": "ai", "type": "sql", "content": sql})
                st.chat_message("ai", avatar="👨‍💻").markdown(sql)

                df_message = return_df(st.session_state.code_of_editor['text'])

                if df_message is not None:
                    st.session_state.df_is_changed = True

                st.session_state.code_for_editor = st.session_state.code_of_editor['text']

                st.session_state.messages.append(
                    {"role": "assistant", "type": "df", "content": df_message})
                st.chat_message("assistant").write(df_message)

                st.session_state.DataFrame = st.session_state.df = df_message
                st.session_state.sql_plotly = 'sql'
            except Exception as e:
                st.chat_message("assistant").error(e)
                
                # print(sql_ai)
        elif lang == "plotly":
            # code_python = extract_code_without_blocks(res.text)
            code_with_block = f"""```python\n{st.session_state.code_of_editor['text']}```"""

            external_data = {"df": st.session_state.DataFrame}
            st.session_state.fig, st.session_state.error = generate_fig(
                code_with_block, external_data)

            # st.session_state.messages.append(
            #     {"role": "user", "type": "text", "content": prompt})

            # st.chat_message("user").write(f"Plotly / {str(prompt)}")

            st.session_state.messages.append(
                {"role": "ai", "type": "code", "content": f"""```python\n{st.session_state.code_of_editor['text']}"""})
            st.chat_message("ai", avatar="👨‍💻").markdown(
                f"""```python\n{st.session_state.code_of_editor['text']}""")

            if st.session_state.error is not None:
                st.session_state.messages.append(
                    {"role": "assistant", "type": "error", "content": st.session_state.error})
                st.chat_message("assistant").error(st.session_state.error)
                # print(st.session_state.error)
                # st.rerun()
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

                st.session_state.notebook.append(st.session_state.code_of_editor['text'])
            # else:
            #     st.chat_message("assistant").warning('No Plotly figure was generated.')

            st.session_state.sql_plotly = 'plotly'
            st.session_state.code_editor_lang = "plotly"
            st.session_state.code_for_editor = st.session_state.code_of_editor['text']        
            
        # with st.spinner('Processing...'):
        #     time.sleep(1)
        #     result, error_occurred = execute_code(st.session_state.code_of_editor['text'])
        #     if not error_occurred:
        #         st.session_state.messages.append({"sender": "You", "text": st.session_state.code_of_editor['text']})
        #         st.session_state.messages.append({"sender": "assistant", "text": result})
        #     else:
        #         st.session_state.messages.append({"sender": "assistant", "text": result})
        st.session_state.call_code = False
        st.rerun()
    elif st.session_state.code_of_editor['type'] == "cancelled":
        st.session_state.call_code = False
        st.rerun()

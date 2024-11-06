# import vertexai
# from vertexai.generative_models import GenerativeModel
# from rich.console import Console
# from rich.markdown import Markdown


# # TODO(developer): Update and un-comment below line
# project_id = "heroic-vial-438702-f5"

# vertexai.init(project=project_id, location="us-central1")

# model = GenerativeModel(model_name="gemini-1.5-pro-002")
# history = list()
# chat = model.start_chat(history=history)
# while True:
#     response = chat.send_message(input('You : '))
#     print("AI :")
#     md = Markdown(response.text)
#     console = Console()
#     console.print(md)
#     # print(f"AI : {response.text}")

# from anthropic import AnthropicVertex

# LOCATION="us-central1"

# client = AnthropicVertex(region=LOCATION, project_id="heroic-vial-438702-f5")

# message = client.messages.create(
#   max_tokens=1024,
#   messages=[
#     {
#       "role": "user",
#       "content": "Send me a recipe for banana bread.",
#     }
#   ],
#   model="claude-3-5-sonnet-v2@20241022",
# )
# print(message.model_dump_json(indent=2))


# import streamlit as st
# from code_editor import code_editor

# response_dict = code_editor('#your_code_string',lang= 'sql' , height=100)


# import streamlit as st

from streamlit_ace import st_ace
import io
import contextlib
# Spawn a new Ace editor
# content = st_ace(height=200,language='sql' , theme='twilight' , keybinding='emacs')

# Display editor's content as you type
# st.text(str(content))
# def execute_code(code):
#     """
#     Executes a given Python code string and returns the result as it would appear in the console.

#     Parameters:
#         code (str): The Python code to execute as a string.

#     Returns:
#         str: The output of the code execution.
#     """
#     # Create a StringIO buffer to capture output
#     output = io.StringIO()
    
#     try:
#         # Redirect stdout to the StringIO buffer
#         with contextlib.redirect_stdout(output):
#             exec(code)
#     except Exception as e:
#         return (f"An error occurred: {e}" , 0)
    
#     # Get the output from the buffer
#     return (output.getvalue() , 1)

# # import streamlit as st

# import streamlit as st
# from code_editor import code_editor
# import json
# import time
# response_dict = code_editor("&&")

# btn_settings_editor_btns = """[
#   {
#     "name": "Copy",
#     "feather": "Copy",
#     "hasText": true,
#     "alwaysOn": true,
#     "commands": [
#       "copyAll",
#       [
#         "infoMessage",
#         {
#           "text": "Copied to clipboard!",
#           "timeout": 2500,
#           "classToggle": "show"
#         }
#       ]
#     ],
#     "style": {
#       "top": "0rem",
#       "right": "0.4rem"
#     }
#   },
#   {
#     "name": "Shortcuts",
#     "feather": "Type",
#     "class": "shortcuts-button",
#     "hasText": true,
#     "commands": [
#       "toggleKeyboardShortcuts",
#       [
#         "conditionalExecute",
#         {
#           "targetQueryString": "#kbshortcutmenu",
#           "condition": true,
#           "command": [
#             "infoMessage",
#             {
#               "text": "VSCode keyboard shortcuts",
#               "timeout": 2500,
#               "classToggle": "show"
#             }
#           ]
#         }
#       ]
#     ],
#     "style": {
#       "bottom": "7rem",
#       "right": "0.4rem"
#     }
#   },
#   {
#     "name": "Save",
#     "feather": "Save",
#     "hasText": true,
#     "commands": [
#       "save-state",
#       [
#         "response",
#         "saved"
#       ]
#     ],
#     "response": "saved",
#     "style": {
#       "bottom": "10rem",
#       "right": "0.4rem"
#     }
#   },
#   {
#     "name": "Run",
#     "feather": "Play",
#     "primary": true,
#     "hasText": true,
#     "showWithIcon": true,
#     "commands": [
#       "submit"
#     ],
#     "style": {
#       "bottom": "0.44rem",
#       "right": "0.4rem"
#     }
#   },
#   {
#     "name": "Cancel",
#     "feather": "XCircle",
#     "primary": true,
#     "hasText": true,
#     "showWithIcon": true,
#     "commands": [
#       "cancel",
#       [
#         "response",
#         "cancelled"
#       ]
#     ],
#     "style": {
#       "bottom": "13rem",
#       "right": "0.4rem"
#     }
#   },
#   {
#     "name": "Command",
#     "feather": "Terminal",
#     "primary": true,
#     "hasText": true,
#     "commands": [
#       "openCommandPallete"
#     ],
#     "style": {
#       "bottom": "3.5rem",
#       "right": "0.4rem"
#     }
#   }
# ]"""

# btns = json.loads(btn_settings_editor_btns)

# # Initialize chat history in session state
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if "code" not in st.session_state:
#     st.session_state.code = None
# if "call_code" not in st.session_state:
#     st.session_state.call_code = False

# # Display the title
# st.title("Chat Application with History")

# # Display the chat history
# for message in st.session_state.messages:
#     sender, text = message["sender"], message["text"]
#     if sender =='You':
#       st.chat_message("user").code(f"""{text}""" , language='sql')
#     else:
#       st.chat_message("assistant").text(text)
    
# if st.session_state.call_code:
#       code_sql = """x = 5
# y = 10
# result = x + y
# print('The result is:', result)
#       """
#     #   st.session_state.code = code_editor(code_sql,focus=True , lang='sql' ,height=200,buttons=[{"name": "Copy", "feather": "Copy", "alwaysOn": True, "commands": ["copyAll"], "style": {"top": "0.46rem", "right": "0.4rem"}}])
#       st.session_state.code = code_editor(code_sql,focus=True , lang='python' ,height=(19,22),buttons=btns ,options={"wrap": True})
#     #   st.session_state.code = st_ace(value=code_sql,height=200,language='sql' , theme='twilight' , keybinding='emacs')
#     #   if st.session_state.code :
#       if st.session_state.code['type'] == "submit" and len(st.session_state.code['text']) != 0:
#         with st.spinner('Processing...'):
#           time.sleep(1)
#           result = execute_code(st.session_state.code['text'])
#           if result[1] == 1:
#             result = result[0]
#             st.session_state.messages.append({"sender": "You", "text": st.session_state.code['text']})
#             st.session_state.messages.append({"sender": "assistant", "text": result})
#             st.chat_message("user").code(f"""{st.session_state.code['text']}""" , language='sql')
#             st.chat_message("ai").text(result)
#             st.session_state.call_code = False
#             st.rerun()
#           else:
#             result = result[0]
#             st.chat_message("ai").error(result)
#         # st.session_state.messages.append({"sender": "You", "text": st.session_state.code['text']})
#         # st.session_state.messages.append({"sender": "assistant", "text": result})
#         # st.chat_message("user").code(f"""{st.session_state.code['text']}""" , language='sql')
#         # # st.chat_message("ai").text(result)
#         # st.session_state.call_code = False
#         # st.rerun()
#       elif st.session_state.code['type'] == "cancelled" :
#         st.session_state.call_code = False
#         st.rerun()


# # Capture user input using chat_input
# user_input = st.chat_input("Type your message here...")







# # Process the user input when entered
# if user_input:
#     if user_input=='/editor':
#         # st.session_state['code'] = st_ace(height=200,language='sql' , theme='twilight' , keybinding='emacs')
#         st.session_state.call_code = True
#         st.rerun()
#         # st.chat_message("user").write(st.session_state.code['text'])
#         # st.session_state.messages.append({"sender": "You", "text": st.session_state.code})
#     elif user_input=="/no_editor":
#       st.session_state.call_code = False
#       st.rerun()
#     else:
#       # Add user message to chat history
#       st.session_state.messages.append({"sender": "You", "text": user_input})
#       st.chat_message("user").write(user_input)

#       # Generate bot response (for now, an echo of the user input)
#       bot_response = f"Echo: {user_input}"

#       st.chat_message("assistant").write(bot_response)
#       # Add bot message to chat history
#       st.session_state.messages.append({"sender": "Bot", "text": bot_response})
#       st.session_state.call_code = False
#       st.rerun()
#       # st.rerun()
#     # Refresh to display new messages
    # 










# import streamlit as st
# from code_editor import code_editor

# if "code" not in st.session_state:
#     st.session_state.code = None
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for message in st.session_state.messages:
#   st.write(message)

# st.session_state.code = code_editor('' , lang='sql')

# if st.session_state.code['type'] == "submit" and len(st.session_state.code['text']) != 0:
#   st.write(st.session_state.code['text'])
#   st.session_state.messages.append(st.session_state.code['text'])





















import streamlit as st
from code_editor import code_editor
import json
import time

def execute_code(code):
    """
    Executes Python code and returns the console output.

    Args:
        code (str): The Python code to execute.

    Returns:
        tuple: A tuple containing the output (str) and an error flag (bool).
               The error flag is True if an error occurred, False otherwise.
    """
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            exec(code)
        return output.getvalue(), False
    except Exception as e:
        return f"An error occurred: {e}", True

def display_and_manipulate_code_editor(code: str = "", lang: str = "python"):
    """
    Displays and handles interactions with a code editor.
    """
    if "code" not in st.session_state:
        st.session_state.code = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "call_code" not in st.session_state:
        st.session_state.call_code = False

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

    # Display chat history
    for message in st.session_state.messages:
        sender, text = message["sender"], message["text"]
        if sender == 'You':
            st.chat_message("user").code(f"""{text}""", language='sql')
        else:
          with st.chat_message("assistant"):
            with st.container(height=250, border=False):
              st.text(text)

    # Code editor logic
    if st.session_state.call_code:
        initial_code = """# Enter your Python code here
print("Hello from code editor!")
"""
        st.session_state.code = code_editor(code, focus=True, lang='python', height=(19, 22), buttons=btns, options={"wrap": True}, info=info_bar)

        if st.session_state.code['type'] == "submit" and len(st.session_state.code['text']) != 0:
            with st.spinner('Processing...'):
                time.sleep(1)
                result, error_occurred = execute_code(st.session_state.code['text'])
                if not error_occurred:
                    st.session_state.messages.append({"sender": "You", "text": st.session_state.code['text']})
                    st.session_state.messages.append({"sender": "assistant", "text": result})
                    st.chat_message("user").code(f"""{st.session_state.code['text']}""", language='sql')
                    st.chat_message("ai").text(result)
                else:
                    st.chat_message("ai").error(result)
            st.session_state.call_code = False
            st.rerun()
        elif st.session_state.code['type'] == "cancelled":
            st.session_state.call_code = False
            st.rerun()

    # User input and chat logic
    user_input = st.chat_input("Type your message here...")
    if user_input:
        if user_input == '/editor':
            st.session_state.call_code = True
            st.rerun()
        else:
            st.session_state.messages.append({"sender": "You", "text": user_input})
            st.chat_message("user").write(user_input)
            bot_response = f"Echo: {user_input}"
            st.chat_message("assistant").write(bot_response)
            st.session_state.messages.append({"sender": "Bot", "text": bot_response})
            st.session_state.call_code = False
            st.rerun()

# Example usage:
display_and_manipulate_code_editor()
















# import streamlit as st
# from code_editor import code_editor
# import json
# import time
# import io
# import contextlib

# def execute_code(code):
#     """
#     Executes Python code and returns the console output.

#     Args:
#         code (str): The Python code to execute.

#     Returns:
#         tuple: A tuple containing the output (str) and an error flag (bool).
#                The error flag is True if an error occurred, False otherwise.
#     """
#     output = io.StringIO()
#     try:
#         with contextlib.redirect_stdout(output):
#             exec(code)
#         return output.getvalue(), False
#     except Exception as e:
#         return f"An error occurred: {e}", True

# def display_code_editor(code: str = "", lang: str = "python"):
#     """
#     Displays and handles interactions with a code editor.
#     """
#     if "code" not in st.session_state:
#         st.session_state.code = None

#     # Button settings for the code editor
#     btn_settings_editor_btns = """
#     [
#       {
#         "name": "Copy",
#         "feather": "Copy",
#         "hasText": true,
#         "alwaysOn": true,
#         "commands": [
#           "copyAll",
#           [
#             "infoMessage",
#             {
#               "text": "Copied to clipboard!",
#               "timeout": 2500,
#               "classToggle": "show"
#             }
#           ]
#         ],
#         "style": {
#           "top": "0rem",
#           "right": "0.4rem"
#         }
#       },
#       {
#         "name": "Run",
#         "feather": "Play",
#         "primary": true,
#         "hasText": true,
#         "showWithIcon": true,
#         "commands": [
#           "submit"
#         ],
#         "style": {
#           "bottom": "0.44rem",
#           "right": "0.4rem"
#         }
#       },
#       {
#         "name": "Cancel",
#         "feather": "XCircle",
#         "primary": true,
#         "hasText": true,
#         "showWithIcon": true,
#         "commands": [
#           "cancel",
#           [
#             "response",
#             "cancelled"
#           ]
#         ],
#         "style": {
#           "bottom": "3rem",
#           "right": "0.4rem"
#         }
#       }
#     ]
#     """
#     css_string = '''
# background-color: #bee1e5;

# body > #root .ace-streamlit-dark~& {
#    background-color: #262830;
# }

# .ace-streamlit-dark~& span {
#    color: #fff;
#    opacity: 0.6;
# }

# span {
#    color: #000;
#    opacity: 0.5;
# }

# .code_editor-info.message {
#    width: inherit;
#    margin-right: 75px;
#    order: 2;
#    text-align: center;
#    opacity: 0;
#    transition: opacity 0.7s ease-out;
# }

# .code_editor-info.message.show {
#    opacity: 0.6;
# }

# .ace-streamlit-dark~& .code_editor-info.message.show {
#    opacity: 0.5;
# }
# '''
#     info_bar = {
#   "name": "language info",
#   "css": css_string,
#   "style": {
#             "order": "1",
#             "display": "flex",
#             "flexDirection": "row",
#             "alignItems": "center",
#             "width": "100%",
#             "height": "2.5rem",
#             "padding": "0rem 0.75rem",
#             "borderRadius": "8px 8px 0px 0px",
#             "zIndex": "9993"
#            },
#   "info": [{
#             "name": lang,
#             "style": {"width": "100px"}
#            }]
# }
#     btns = json.loads(btn_settings_editor_btns)

#     initial_code = """# Enter your Python code here
# print("Hello from code editor!")
# """
#     st.session_state.code = code_editor(code, focus=True, lang='python', height=(19, 22), buttons=btns, options={"wrap": True}, info=info_bar)

#     if st.session_state.code['type'] == "submit" and len(st.session_state.code['text']) != 0:
#         with st.spinner('Processing...'):
#             time.sleep(1)
#             result, error_occurred = execute_code(st.session_state.code['text'])
#             if not error_occurred:
#                 st.session_state.messages.append({"sender": "You", "text": st.session_state.code['text']})
#                 st.session_state.messages.append({"sender": "assistant", "text": result})
#             else:
#                 st.session_state.messages.append({"sender": "assistant", "text": result})
#         st.rerun()
#     elif st.session_state.code['type'] == "cancelled":
#         st.rerun()

# def display_chat_history():
#     """Displays the chat history."""
#     for message in st.session_state.messages:
#         sender, text = message["sender"], message["text"]
#         with st.fragment(key=text):  # Use st.fragment to prevent re-rendering
#             if sender == 'You':
#                 st.chat_message("user").code(f"""{text}""", language='sql')
#             else:
#                 with st.chat_message("assistant"):
#                     with st.container(height=250, border=False):
#                         st.text(text)

# def main():
#     """Main function to run the Streamlit application."""
#     if "messages" not in st.session_state:
#         st.session_state.messages = []
#     if "call_code" not in st.session_state:
#         st.session_state.call_code = False

#     display_chat_history()

#     user_input = st.chat_input("Type your message here...")
#     if user_input:
#         if user_input == '/editor':
#             st.session_state.call_code = True
#             st.rerun()
#         else:
#             st.session_state.messages.append({"sender": "You", "text": user_input})
#             bot_response = f"Echo: {user_input}"
#             st.session_state.messages.append({"sender": "Bot", "text": bot_response})
#             st.session_state.call_code = False
#             st.rerun()

#     if st.session_state.call_code:
#         display_code_editor()

# if __name__ == "__main__":
#     main()

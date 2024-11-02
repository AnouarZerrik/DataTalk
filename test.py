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

# Spawn a new Ace editor
# content = st_ace(height=200,language='sql' , theme='twilight' , keybinding='emacs')

# Display editor's content as you type
# st.text(str(content))


# import streamlit as st

import streamlit as st
from code_editor import code_editor
import json
# response_dict = code_editor("&&")

btn_settings_editor_btns = """[
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
    "name": "Shortcuts",
    "feather": "Type",
    "class": "shortcuts-button",
    "hasText": true,
    "commands": [
      "toggleKeyboardShortcuts",
      [
        "conditionalExecute",
        {
          "targetQueryString": "#kbshortcutmenu",
          "condition": true,
          "command": [
            "infoMessage",
            {
              "text": "VSCode keyboard shortcuts",
              "timeout": 2500,
              "classToggle": "show"
            }
          ]
        }
      ]
    ],
    "style": {
      "bottom": "7rem",
      "right": "0.4rem"
    }
  },
  {
    "name": "Save",
    "feather": "Save",
    "hasText": true,
    "commands": [
      "save-state",
      [
        "response",
        "saved"
      ]
    ],
    "response": "saved",
    "style": {
      "bottom": "10rem",
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
    "name": "Command",
    "feather": "Terminal",
    "primary": true,
    "hasText": true,
    "commands": [
      "openCommandPallete"
    ],
    "style": {
      "bottom": "3.5rem",
      "right": "0.4rem"
    }
  }
]"""

btns = json.loads(btn_settings_editor_btns)

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "code" not in st.session_state:
    st.session_state.code = None
if "call_code" not in st.session_state:
    st.session_state.call_code = False

# Display the title
st.title("Chat Application with History")

# Display the chat history
for message in st.session_state.messages:
    sender, text = message["sender"], message["text"]
    if sender =='You':
      st.chat_message("user").code(f"""{text}""" , language='sql')
    else:
      st.chat_message("assistant").write(text)
    
if st.session_state.call_code:
      code_sql = """SELECT 
    c.customer_id,
    c.name AS customer_name,
    c.email,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_spent,
    AVG(o.total_amount) AS avg_order_value,
    MAX(o.order_date) AS last_purchase_date
    
FROM 
    customers c
JOIN 
    orders o ON c.customer_id = o.customer_id
LEFT JOIN 
    order_items oi ON o.order_id = oi.order_id
LEFT JOIN 
    products p ON oi.product_id = p.product_id

WHERE 
    o.order_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)  -- filter for orders in the last year

GROUP BY 
    c.customer_id, c.name, c.email

ORDER BY 
    total_spent DESC
LIMIT 50;"""
    #   st.session_state.code = code_editor(code_sql,focus=True , lang='sql' ,height=200,buttons=[{"name": "Copy", "feather": "Copy", "alwaysOn": True, "commands": ["copyAll"], "style": {"top": "0.46rem", "right": "0.4rem"}}])
      st.session_state.code = code_editor(code_sql,focus=True , lang='sql' ,height=(19,22),buttons=btns ,options={"wrap": True})
    #   st.session_state.code = st_ace(value=code_sql,height=200,language='sql' , theme='twilight' , keybinding='emacs')
    #   if st.session_state.code :
      if st.session_state.code['type'] == "submit" and len(st.session_state.code['text']) != 0:
        st.session_state.messages.append({"sender": "You", "text": st.session_state.code['text']})
        st.chat_message("user").code(f"""{st.session_state.code['text']}""" , language='sql')
        st.session_state.call_code = False
        st.rerun()

# Capture user input using chat_input
user_input = st.chat_input("Type your message here...")

# Process the user input when entered
if user_input:
    if user_input=='editor':
        # st.session_state['code'] = st_ace(height=200,language='sql' , theme='twilight' , keybinding='emacs')
        st.session_state.call_code = True
        st.rerun()
        # st.chat_message("user").write(st.session_state.code['text'])
        # st.session_state.messages.append({"sender": "You", "text": st.session_state.code})
    else:
      # Add user message to chat history
      st.session_state.messages.append({"sender": "You", "text": user_input})
      st.chat_message("user").write(user_input)

      # Generate bot response (for now, an echo of the user input)
      bot_response = f"Echo: {user_input}"

      st.chat_message("assistant").write(bot_response)
      # Add bot message to chat history
      st.session_state.messages.append({"sender": "Bot", "text": bot_response})
      # st.rerun()
    # Refresh to display new messages
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
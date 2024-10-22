import vertexai
from vertexai.generative_models import GenerativeModel
from rich.console import Console
from rich.markdown import Markdown


# TODO(developer): Update and un-comment below line
project_id = "heroic-vial-438702-f5"

vertexai.init(project=project_id, location="us-central1")

model = GenerativeModel(model_name="gemini-1.5-pro-002")
history = list()
chat = model.start_chat(history=history)
while True:
    response = chat.send_message(input('You : '))
    print("AI :")
    md = Markdown(response.text)
    console = Console()
    console.print(md)
    # print(f"AI : {response.text}")
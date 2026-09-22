from pathlib import Path
from ollama import chat

question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

selected_files = [
    "knowledge/password_changes.txt",
    "knowledge/wifi_setup.txt",
    "knowledge/service_status.txt"
]

context = ""

## Write a for loop to go through all the files in selected_files and read their contents into the context variable.
for file_path in selected_files:
    context += Path(file_path).read_text()
    context += "\n\n"

## Call Qwen with the student's question and the context you created above.
messages = [
    {'role': 'system', 'content': 'You are a helpful IT support assistant.'},
    {'role': 'user', 'content': f"Context:\n{context}\n\nQuestion: {question}"}
]
response = chat(model='qwen', messages=messages)

print("Context characters:", len(context))
print(response.message.content)

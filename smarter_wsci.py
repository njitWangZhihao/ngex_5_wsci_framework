from pathlib import Path
from ollama import chat
import json

question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

## WRITE ##
service_status = {
    "wifi": "operational"
}

state = {
    "problem": question,
    "wi_fi status": "operational",
    "wi-fi_check": True
}

with open("state.json", "w") as file:
    json.dump(state, file, indent=2)

with open("state.json", "r") as file:
    state = json.load(file)

print(state)

## SELECT CONTEXT FILES BASED ON QUESTION
def select_context(question):
    """
    根据问题中的关键词选择相关知识库文件。
    返回文件路径列表。
    """
    question_lower = question.lower()
    selected = []
    if 'password' in question_lower or 'credentials' in question_lower:
        selected.append('knowledge/password_changes.txt')
    if 'wi-fi' in question_lower or 'wifi' in question_lower or 'eduroam' in question_lower:
        selected.append('knowledge/wifi_setup.txt')
    if 'service' in question_lower or 'status' in question_lower or 'phone' in question_lower:
        selected.append('knowledge/service_status.txt')
    return list(set(selected))

selected_files = select_context(question)
print("Selected files:", selected_files)

## READ SELECTED FILES and add their contents to the context variable.
context = ""
for file_path in selected_files:
    context += Path(file_path).read_text()
    context += "\n\n"

## COMPRESS CONTEXT
def compress_context(context, question):
    """
    调用 Qwen 压缩上下文，只保留与问题相关的信息。
    """
    prompt = f"""You are given a context and a user question. Extract only the information from the context that is relevant to answering the question. Return the compressed context as plain text. Do not add any new information.

Context:
{context}

Question:
{question}

Compressed context:"""
    response = chat(model='qwen', messages=[{'role': 'user', 'content': prompt}])
    return response.message.content

compressed_context = compress_context(context, question)

## Print the length of the compressed context
print("Compressed context length:", len(compressed_context))
print("Compressed context:", compressed_context)

## Now, call Qwen again with the compressed context and the student's question.
## Ensure the model produces a structured output.
messages = [
    {'role': 'system', 'content': 'You are a helpful IT support assistant. Provide your answer in JSON format with keys: "diagnosis", "solution", "steps".'},
    {'role': 'user', 'content': f"Compressed context:\n{compressed_context}\n\nQuestion: {question}"}
]
response = chat(model='qwen', messages=messages)

print(response.message.content)

## WRITE the above output in an artifact called "state"
## Update the rest of the code so that it uses the "state" artifact as part of the context.
try:
    structured_output = json.loads(response.message.content)
except json.JSONDecodeError:
    structured_output = {"raw_response": response.message.content}

state.update({
    "diagnosis": structured_output.get("diagnosis", ""),
    "solution": structured_output.get("solution", ""),
    "steps": structured_output.get("steps", []),
    "compressed_context": compressed_context
})

with open("state.json", "w") as file:
    json.dump(state, file, indent=2)

print("State saved to state.json")
print(json.dumps(state, indent=2))

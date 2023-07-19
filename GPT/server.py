import openai
from flask import Flask, request
import os

openai.api_key = "*"

app = Flask(__name__)

@app.route("/gpt_answer", methods=["POST"])
def gpt_answer():
    content = request.json
    system = {"role":"system","content":content["system_text"]}
    history = content["history"]
    messages = [system]
    new_prompt = content["new_prompt"]
    for message in history:
        messages.append({"role":"user","content":message[0]})
        messages.append({"role":"assistant","content":message[1]})
    messages.append({"role": "user", "content": new_prompt})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    result = "".join(choice.message.content for choice in response.choices)
    return {"respone":result}

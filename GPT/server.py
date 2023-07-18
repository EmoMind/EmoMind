import openai
from flask import Flask, request
import os

openai.api_key = "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"

app = Flask(__name__)

@app.route("/gpt_answer", methods=["POST"])
def gpt_answer():
    content = request.json
    system = {"role":"system","content":content["system_text"]}
    user = content["user_text"]
    bot = content["bot_text"]
    messages = [system]
    if bot:
        messages.append({"role":"user","content":user[0]})
    else:
        for i in range(len(bot)):
            messages.append({"role":"user","content":user[i]})
            messages.append({"role":"bot","content":bot[i]})
        messages.append({"role": "user", "content": user[len(user)-1]})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    result = "".join(choice.message.content for choice in response.choices)
    return {"respone":result}

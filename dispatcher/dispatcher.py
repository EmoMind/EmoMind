from flask import Flask, request
from r_client import RedisClient
import requests
import torch

app = Flask(__name__)
rc = RedisClient("localhost", "6379")

@app.route("/query", methods=["POST"])
def query():
    def stt(audio, s_r):
        request = {"sample_rate": s_r, "audio": audio.tolist()[0]}
        text = requests.post("http://127.0.0.1:5005/speech_recognize", json=request)
        return (text.json()["text"])
    def emotion(audio, s_r):
        emotion_request = {"audio": audio.tolist(), "sample_rate": s_r}
        emotion = requests.post("http://127.0.0.1:5006/get_emotion", json=emotion_request)
        return (emotion.json()["emotion"])
    def gpt(system_text, user_text, bot_text):
        request_bot = {"system_text": f"Настроение пользователя - {system_text}", "user_text": user_text, "bot_text": bot_text}
        bot_ans = requests.post("http://127.0.0.1:5007/gpt_answer", json=request_bot)
        return (bot_ans.json()["respone"])
    def tts(text, speaker_id):
        request_tts = {"text": bot_ans, "speaker_id": speaker_id}
        audio_ans = requests.post("http://127.0.0.1:5008/speech_synthesize", json=request_tts)
        return audio_ans.json()
        
    content = request.json
    user_id = content["user_id"]
    if not rc.user_exists(user_id):
        rc.add_user(user_id, "yodrick")
    audio = content["audio"]
    s_r = content["sample_rate"]
    personage = rc.get_character(user_id)
    
    voice = torch.tensor(audio)
    prompts = rc.get_messages(user_id)
    prompts.append(stt(voice, s_r))
    prompt = ". ".join(prompts)
    
    mood = emotion(voice, s_r)
    rc.update_emotion(user_id, mood)
    bot_ans = gpt(f". Настроение пользователя - {mood}.", prompt, [None])
    rc.add_message(user_id, bot_ans)
    tts_audio = tts(bot_ans, personage)
    return tts_audio

@app.route("/web_query", methods=["POST"])
def web_query():
    content = request.json

@app.route("/change_character", methods=["POST"])
def change_character():
    content = request.json
    user_id = content["user_id"]
    if not rc.user_exists(user_id):
        rc.add_user(user_id, "yodrick")
    character = content["character"]
    rc.update_character(user_id, character)
    return
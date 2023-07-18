from flask import Flask, request
from r_client import RedisClient
import requests
import torch

app = Flask(__name__)
rc = RedisClient("localhost", "6379")

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
    request_tts = {"text": text, "speaker_id": speaker_id}
    audio_ans = requests.post("http://127.0.0.1:5008/speech_synthesize", json=request_tts)
    return audio_ans.json()

@app.route("/query", methods=["POST"])
def query():
    content = request.json
    user_id = content["user_id"]
    if not rc.user_exists(user_id):
        rc.add_user(user_id, content["personage"])
        
    audio = content["audio"]
    s_r = content["sample_rate"]
    personage = rc.get_character(user_id)
    
    voice = torch.tensor(audio)
    prompts = rc.get_messages(user_id)
    prompts.append(stt(voice, s_r))
    prompt = ". ".join(prompts)
    
    mood = emotion(voice, s_r)
    rc.update_emotion(user_id, mood)
    
    
    bot_ans = gpt(mood, prompt, [None])
    rc.add_message(user_id, bot_ans)
    
    tts_audio = tts(bot_ans, "eugene")
    
    return tts_audio

@app.route("/text_query", methods=["POST"])
def text_query():
    content = request.json
    user_id = content["user_id"]
    if not rc.user_exists(user_id):
        rc.add_user(user_id, content["personage"])
        
    text = content["text"]
    personage = rc.get_character(user_id)
    
    prompts = rc.get_messages(user_id)
    prompts.append(text)
    prompt = ". ".join(prompts)
    
    #mood = emotion(voice, s_r)
    mood = "neutral"
    rc.update_emotion(user_id, mood)
    
    bot_ans = gpt(mood, prompt, [None])
    rc.add_message(user_id, bot_ans)
    
    tts_audio = tts(bot_ans, "eugene")
    
    return tts_audio
    

@app.route("/change_character", methods=["POST"])
def change_character():
    content = request.json
    user_id = content["user_id"]
    character = content["character"]
    rc.update_character(user_id, character)
    return

@app.route("/change_emotion", methods=["POST"])
def change_emotion():
    content = request.json
    user_id = content["user_id"]
    emotion = content["emotion"]
    rc.update_emotion(user_id, emotion)
    return

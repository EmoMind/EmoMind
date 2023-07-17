from flask import Flask, request
import requests
import torch

app = Flask(__name__)

@app.route("/query", methods=["POST"])
def query():
    def stt(audio, s_r):
        request = {"sample_rate": s_r, "audio": audio.tolist()[0]}
        text = requests.post("http://127.0.0.1:5010/speech_recognize", json=request)
        return (text.json()["text"])
    def emotion(audio, s_r):
        emotion_request = {"audio": audio.tolist(), "sample_rate": s_r}
        emotion = requests.post("http://127.0.0.1:5008/get_emotion", json=emotion_request)
        return (emotion.json()["emotion"])
    def gpt(system_text, user_text, bot_text):
        request_bot = {"system_text": f"Настроение пользователя - {system_text}", "user_text": user_text, "bot_text": bot_text}
        bot_ans = requests.post("http://127.0.0.1:5006/gpt_answer", json=request_bot)
        return (bot_ans.json()["respone"])
    def tts(text, speaker_id):
        request_tts = {"text": bot_ans, "speaker_id": "eugene"}
        audio_ans = requests.post("http://127.0.0.1:5011/speech_synthesize", json=request_tts)
        return audio_ans.json()
        
    content = request.json
    user_id = content["user_id"]
    audio = content["audio"]
    s_r = content["sample_rate"]
    personage = content["personage"]
    
    voice = torch.tensor(audio)
    prompt = stt(voice, s_r)
    mood = emotion(voice, s_r)
    bot_ans = gpt(mood, prompt, [None])
    tts_audio = tts(bot_ans, 1)
    
    return tts_audio
    

@app.route("/change_character", methods=["POST"])
def change_character():
    return 

@app.route("/change_emotion", methods=["POST"])
def change_emotion():
    return

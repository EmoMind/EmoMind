from flask import Flask, request, abort
from r_client import RedisClient
from firfir import generate_capybara_sounds, text_limit
import requests
from requests.exceptions import RequestException
import torch
import sys
import logging

logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s')

app = Flask(__name__)
rc = RedisClient("localhost", "6379")

sys_prompt = {
"yodrick":"", 
"capybara":"",
"olimpia": ""
}

def log_requests(func):
    def wrapper(*args, **kwargs):
        try: 
            result = func(*args, **kwargs)
            return result
        except RequestException as e:
            logging.error(f"{func.__name__} {e}")
            abort(500)
            return None
    return wrapper

@log_requests
def stt(audio, s_r):
    request = {"sample_rate": s_r, "audio": audio.tolist()[0]}
    text = requests.post("http://127.0.0.1:5005/speech_recognize", json=request)
    return (text.json()["text"])
@log_requests
def emotion(audio, s_r):
    emotion_request = {"audio": audio.tolist(), "sample_rate": s_r}
    emotion = requests.post("http://127.0.0.1:5006/get_emotion", json=emotion_request)
    return (emotion.json()["emotion"])
@log_requests
def gpt(system_text, history, new_prompt):
    request_bot = {"system_text": f"Настроение пользователя - {system_text}", "history": history, "new_prompt": new_prompt}
    bot_ans = requests.post("http://127.0.0.1:5007/gpt_answer", json=request_bot)
    return (bot_ans.json()["respone"])
@log_requests
def tts(text, speaker_id):
    request_tts = {"text": text, "speaker_id": speaker_id}
    audio_ans = requests.post("http://127.0.0.1:5008/speech_synthesize", json=request_tts)
    return audio_ans.json()

@app.route("/query", methods=["POST"])
def query():
    content = request.json
    user_id = content["user_id"]
    if not rc.user_exists(user_id):
        rc.add_user(user_id, "yodrick")
        
    audio = content["audio"]
    s_r = content["sample_rate"]
    personage = rc.get_character(user_id)
    
    voice = torch.tensor(audio)
    history = rc.get_messages(user_id)
    prompt = stt(voice, s_r)
    
    mood = emotion(voice, s_r)
    previous_mood = rc.get_emotion(user_id)
    rc.update_emotion(user_id, mood)
    
    if previous_mood == mood:
        bot_ans = gpt(f"{sys_prompt[personage]}. Настроение пользователя - {mood}.", history, prompt)
    else:
        bot_ans = gpt(f"{sys_prompt[personage]}. Настроение пользователя изменилось с {previous_mood} на {mood}.", history, prompt)
    print(f"{sys_prompt[personage]}. Настроение пользователя - {mood}.", file=sys.stderr)
    print(prompt, file=sys.stderr)
    if personage == 'capybara':
        sounds = generate_capybara_sounds(bot_ans)
        rc.add_message(user_id, prompt,sounds + f'({bot_ans})')
        bot_ans = text_limit(sounds)
        tts_audio = tts(bot_ans, 'capybara')
    else:
        rc.add_message(user_id, prompt, bot_ans)
        tts_audio = tts(bot_ans, personage)
    logging.info(f"{U: {prompt} B: {bot_ans}")
    return tts_audio


@app.route("/web_query", methods=["POST"])
def web_query():
    content = request.json
    content = request.json
    user_id = content["user_id"]
    if not rc.user_exists(user_id):
        rc.add_user(user_id, "yodrick")
    audio = content["audio"]
    s_r = content["sample_rate"]
    personage = rc.get_character(user_id)
    voice = torch.tensor(audio)
    user_message = stt(voice, s_r)
    prompts = rc.get_messages(user_id)
    prompts.append(user_message)
    prompt = ". ".join(prompts)
    
    mood = emotion(voice, s_r)
    rc.update_emotion(user_id, mood)
    bot_ans = gpt(f". Настроение пользователя - {mood}.", prompt, [None])
    rc.add_message(user_id, bot_ans)
    tts_audio = tts(bot_ans, personage)
    return [tts_audio,user_message,bot_ans]
@app.route("/change_character", methods=["POST"])
def change_character():
    content = request.json
    user_id = content["user_id"]
    if not rc.user_exists(user_id):
        rc.add_user(user_id, "yodrick")
    character = content["character"]
    rc.update_character(user_id, character)
    return "200"

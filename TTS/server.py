from flask import Flask, request, jsonify
import os.path
import torch
import sys

app = Flask(__name__)

language = 'ru'
model_id = 'v3_1_ru'
device = torch.device('cpu')
torch.hub.set_dir(".")

tts_model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                     model='silero_tts',
                                     language=language,
                                     speaker=model_id)
tts_model.to(device)
default_speakers = tts_model.speakers

def text_to_speech(text:str, speaker_id:str) -> list:
    sample_rate = 48000

    print(speaker_id, file=sys.stderr)
    print(default_speakers, file=sys.stderr)
    
    if speaker_id in default_speakers:
        audio = tts_model.apply_tts(text=text,
                                speaker=speaker_id,
                                sample_rate=sample_rate,
                                put_accent=True,
                                put_yo=True)
        return audio.tolist()
    
    fname = f"custom_speakers/{speaker_id}.pt"
    if os.path.isfile(fname):
        audio = tts_model.apply_tts(text=text,
                        speaker="random",
                        sample_rate=sample_rate,
                        voice_path=fname)
        return audio.tolist()
    
    audio = tts_model.apply_tts(text=text,
                        speaker="random",
                        sample_rate=sample_rate)
    return audio.tolist()

@app.route("/speech_synthesize", methods=["POST"])
def speech_synthesize():
    content = request.json
    text = content["text"]
    speaker_id = content["speaker_id"]
    audio = text_to_speech(text, speaker_id)
    return {"audio": audio}

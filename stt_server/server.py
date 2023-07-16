from flask import Flask, request
import torch
import numpy as np
import torchaudio
import transformers
from faster_whisper import WhisperModel


torch.set_num_threads(1)
stt_model = WhisperModel("medium")

def speech_to_text(audio: np.ndarray) -> str:
  segments, info = stt_model.transcribe(audio)
  text = ' '.join([segment.text for segment in segments])
  return text

app = Flask(__name__)

@app.route("/speech_recognize", methods=["POST"])
def speech_recognize():
    content = request.json
    sample_rate = content["sample_rate"]
    audio = torch.tensor(content["audio"])
    audio = torchaudio.functional.resample(sample_rate, 16000)
    audio = audio.numpy()
    text = speech_to_text(audio)
    return {"text": text}
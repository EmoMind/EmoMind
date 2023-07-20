from flask import Flask, request
import torch
import numpy as np
import torchaudio
import transformers
from faster_whisper import WhisperModel
import time
import sys

torch.set_num_threads(1)
stt_model = WhisperModel("medium", device="cuda", compute_type="float16")

def speech_to_text(audio: np.ndarray) -> str:
  segments, info = stt_model.transcribe(audio)
  text = ' '.join([segment.text for segment in segments])
  return text

app = Flask(__name__)

@app.route("/speech_recognize", methods=["POST"])
def speech_recognize():
    content = request.json
    now1 = time.time()
    sample_rate = content["sample_rate"]
    audio = torch.tensor(content["audio"])
    audio = torchaudio.functional.resample(audio, sample_rate, 16000)
    audio = audio.numpy()
    now2 = time.time()
    text = speech_to_text(audio)
    print("stt model", time.time()-now2, file=sys.stderr)
    print("all method", time.time()-now1, file=sys.stderr)
    return {"text": text}

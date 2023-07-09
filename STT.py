import torch
import torchaudio
import transformers
import datasets
import librosa
import jiwer
import warnings

import pandas as pd
import matplotlib.pyplot as plt

from tqdm.auto import tqdm
from IPython.display import Audio, display

torch.set_num_threads(1)
warnings.filterwarnings("ignore")

from faster_whisper import WhisperModel
stt_model = WhisperModel("medium")

target_audio = "Путь к аудио"
def STT(audio):
  segments, info = stt_model.transcribe(audio)
  for segment in segments:
      return segment.text
enter_prompt = STT(target_audio)

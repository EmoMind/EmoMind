# -*- coding: utf-8 -*-
"""tts.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rFCYZ9OCFdIXRUf6l_DRkwqy81tJo2N7
"""

import torch
from pprint import pprint
from omegaconf import OmegaConf
from IPython.display import Audio, display

torch.hub.download_url_to_file('https://raw.githubusercontent.com/snakers4/silero-models/master/models.yml',
                               'latest_silero_models.yml',
                               progress=False)
models = OmegaConf.load('latest_silero_models.yml')
language = 'ru'
model_id = 'v3_1_ru'
device = torch.device('cpu')

tts_model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                     model='silero_tts',
                                     language=language,
                                     speaker=model_id)
tts_model.to(device)
def text_to_speech(output):
    sample_rate = 48000
    speaker = 'xenia'
    put_accent=True
    put_yo=True

    audio = tts_model.apply_tts(text=output,
                            speaker=speaker,
                            sample_rate=sample_rate,
                            put_accent=put_accent,
                            put_yo=put_yo)
    return audio
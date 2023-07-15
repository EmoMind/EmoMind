import torch
language = 'ru'
model_id = 'v3_1_ru'
torch.hub.set_dir(".")
torch.hub.load(repo_or_dir='snakers4/silero-models',
                                     model='silero_tts',
                                     language=language,
                                     speaker=model_id)
# -*- coding: utf-8 -*-
"""app.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1RarMWgJDSZizlOeeqJY6cxVuixPA-oJZ
"""

from stt import speech_to_text
from bot import chat_bot
from tts import text_to_speech
from IPython.display import Audio, display
audio_files = ["audio_1.ogg", "audio_2.ogg"]
for i in audio_files:
    enter_prompt = speech_to_text(i)
    bot_ans = chat_bot(enter_prompt)
    audio = text_to_speech(bot_ans)
    display(Audio(audio, rate=48000))
from aiogram import Bot, Dispatcher, executor, types
import os
import tempfile
import torchaudio
import requests
import torch
import opuspy
import numpy as np



bot = Bot(token='6294998264:AAGGTSpHfFGabeZGafEB8PxmEMi2uC4t7kU')
dp = Dispatcher(bot)

chars = {"mage":"Волшебник","jedi":"Джедай","capybara":"😎Капибара😎"}

personage_voice = {"Волшебник": "olimpia", "Джедай": "yodrick", "😎Капибара😎": "capybara"}

@dp.message_handler(commands=['start','change_person','cp','cc','change_char','change_character'])
async def char_change(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Волшебник", callback_data="char_mage"))
    keyboard.add(types.InlineKeyboardButton(text="Джедай", callback_data="char_jedi"))
    keyboard.add(types.InlineKeyboardButton(text="😎Капибара😎", callback_data="char_capybara"))
    await message.answer('Выбери персонажа, с которым ты хочешь пообщаться', reply_markup=keyboard)

@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Кнопка помощи 1", callback_data="help_1"))
    keyboard.add(types.InlineKeyboardButton(text="Кнопка помощи 2", callback_data="help_2"))
    await message.answer('Тут будет помощь.', reply_markup=keyboard)

@dp.message_handler(content_types=[types.ContentType.VOICE])
async def voice_message_handler(message: types.Message):
    await message.answer_chat_action(types.ChatActions.RECORD_AUDIO)
    with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        print(file_path)
        print(temp_file.name)
        await bot.download_file(file_path, temp_file.name)
        audio, s_r = torchaudio.load(temp_file)
    request_disp = {"user_id": message.chat.id, "audio": audio.tolist(), "sample_rate": s_r}
    tts_answer = requests.post("http://127.0.0.1:5001/query", json=request_disp)
    with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
        voice = torch.tensor(tts_answer.json()["audio"]).unsqueeze(0)
        print(voice.shape)
        torchaudio.save(temp_file.name, voice, 48000)
        await message.answer_voice(voice=types.InputFile(temp_file.name, "r"))

@dp.callback_query_handler(text_startswith="char")
async def char_changed(call: types.CallbackQuery):
    char_id = call.data.split("_")[1]
    character = chars[char_id]
    request_disp = {"user_id": call.message.chat.id, "character": personage_voice[character]}
    print(call.message.chat.id)
    requests.post("http://127.0.0.1:5001/change_character", json=request_disp)
    await call.message.edit_text(f"Вы выбрали персонажа {character}")
    await call.answer()

@dp.message_handler(commands=['end'])
async def char_change(message: types.Message):
    await message.answer('Все. Это конец. Продолжения не будет.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

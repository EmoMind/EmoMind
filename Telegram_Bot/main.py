from aiogram import Bot, Dispatcher, executor, types
import os
import tempfile
import torchaudio
import requests
import torch
import opuspy
import numpy as np
import subprocess



bot = Bot(token='6294998264:AAGGTSpHfFGabeZGafEB8PxmEMi2uC4t7kU')
dp = Dispatcher(bot)

chars = {"mage":"Олимпия из Хогвартса","jedi":"Йодрик внук Йоды","capybara":"😎Капибара😎"}

personage_voice = {"Олимпия из Хогвартса": "olimpia", "Йодрик внук Йоды": "yodrick", "😎Капибара😎": "capybara"}
char_info = {
    'mage': 'Привет! Я учусь в Хогвартсе, очень люблю разговоры об учебе, спорте и мечтах о будущем! А ты собираешь карточки из-под шокладных лягушек?',
    'jedi': 'Джедай я великий, Йодрик. Мудрость великую тебе расскажу. Знаю все, за последние было несколько лет что. Расскажу тебе величие джедаев всё, ситхов подлость всю.',
    'capybara': 'Фыр фыр-фыр фыр-фыр фыр-фыр фыр, фыр.(Здравствуй, мой молодой путник. Я открою тебе все тайны прошлого, настоящего, будущего. Не забывай о доброте, друг мой!)'
}

@dp.message_handler(commands=['start','change_person','cp','cc','change_char','change_character'])
async def char_change(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Олимпия из Хогвартса", callback_data="char_mage"))
    keyboard.add(types.InlineKeyboardButton(text="Йодрик внук Йоды", callback_data="char_jedi"))
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
    with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        print(file_path)
        print(temp_file.name)
        await bot.download_file(file_path, temp_file.name)
        audio, s_r = torchaudio.load(temp_file)
    request_disp = {"user_id": message.chat.id, "audio": audio.tolist(), "sample_rate": s_r}
    await message.answer_chat_action(types.ChatActions.RECORD_AUDIO)
    tts_answer = requests.post("http://127.0.0.1:5001/query", json=request_disp)
    with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
        voice = torch.tensor(tts_answer.json()["audio"]).unsqueeze(0)
        torchaudio.save(temp_file.name, voice, 48000)
        result_file = temp_file.name.replace('wav', 'ogg')
        convert_to_voice_cmd = f"ffmpeg -i {temp_file.name} -c:a libopus {result_file}"
        subprocess.run(f"{convert_to_voice_cmd}", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        await message.answer_voice(voice=types.InputFile(result_file, "r"))
        await message.answer(tts_answer.json()["text_answer"])
        os.remove(result_file)

@dp.callback_query_handler(text_startswith="char")
async def char_changed(call: types.CallbackQuery):
    char_id = call.data.split("_")[1]
    character = chars[char_id]
    request_disp = {"user_id": call.message.chat.id, "character": personage_voice[character]}
    print(call.message.chat.id)
    requests.post("http://127.0.0.1:5001/change_character", json=request_disp)
    await call.message.edit_text(f"Вы выбрали персонажа {character}")
    await call.message.answer(char_info[char_id])
    if char_id == 'capybara':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Песня 1", callback_data="song1"))
        keyboard.add(types.InlineKeyboardButton(text="Песня 2", callback_data="song2"))
        # keyboard.add(types.InlineKeyboardButton(text="Гифка", callback_data="gif"))
        await call.message.answer('Я могу спеть тебе песню!', reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(text_startswith="song")
async def mood_changed(call: types.CallbackQuery):
    song_type = call.data
    await call.message.answer_voice(voice=types.InputFile(f'{song_type}.opus', "r"))
    await call.message.edit_text(f'Держи песенку!')
    await call.message.answer_animation(animation=types.InputFile('capy.gif'))


@dp.message_handler(commands=['end'])
async def char_change(message: types.Message):
    await message.answer('Все. Это конец. Продолжения не будет.')


@dp.message_handler(content_types="text")
async def text_message_handler(message: types.Message):
    if message.is_command():
        return

    request_disp = {"user_id": message.from_user.id, "text": message.text}
    tts_answer = requests.post("http://127.0.0.1:5001/text_query", json=request_disp)
    with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
        voice = torch.tensor(tts_answer.json()["audio"]).unsqueeze(0)
        torchaudio.save(temp_file.name, voice, 48000)
        result_file = temp_file.name.replace('wav', 'ogg')
        convert_to_voice_cmd = f"ffmpeg -i {temp_file.name} -c:a libopus {result_file}"
        subprocess.run(f"{convert_to_voice_cmd}", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        await message.answer_voice(voice=types.InputFile(result_file, "r"))
        await message.answer(tts_answer.json()["text_answer"])
        os.remove(result_file)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

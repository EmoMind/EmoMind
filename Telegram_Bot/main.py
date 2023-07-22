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
    'mage': 'Привет! Я ученица факультета Хаффлпафф школы магии и волшебства - Хогвартс. Как капитан команды по квиддичу я здесь, чтобы всегда вдохновлять тебя на достижение больших целей - будь то спорт или учеба!',
    'jedi': 'Привет! Я - Йодрик, троюродный внук самого магистра Йоды, наставником джедаев я являюсь. Готов указать путь решения твоих проблем любых, даже если в безвыходном положении, тебе кажется, ты оказался.',
    'capybara': 'Фыр фыр-фыр фыр-фыр фыр-фыр фыр, фыр.(Привет, мой дорогой друг! Уверена, тебе уже известно, кто я. Я - великая капибара, которая живет уже более миллиарда лет и видела великие события. Обращайся ко мне, когда будет казаться, что мир вокруг стал сложным и слишком большим. Я всегда помогу тебе найти гармионию и успокоиться.)'
}

help_dict = {
     'help_1': 'Привет, друг! Я расскажу тебе, что умею.'+
     '\nТы можешь отправить мне текстовое или голосовое сообщение.'+
     ' \nЯ могу посоветовать тебе фильм, песню, просто поболтать с тобой. Удачи!',
     'help_2': 'Для начала общения, выбери персонажа. Для этого нажми на одну из предложенных кнопок.'+
     '\nДалее, запиши мне голосовое сообщение или напиши свою просьбу текстом.'+
     '\nЕсли ты хочешь прекратить общение, нажми на кнопку «/end» в меню. Удачи!'
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
    keyboard.add(types.InlineKeyboardButton(text="Общая информация", callback_data="help_1"))
    keyboard.add(types.InlineKeyboardButton(text="Взаимодействие", callback_data="help_2"))
    await message.answer('Помощь', reply_markup=keyboard)

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
        if "audio" in tts_answer.json():
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
    await call.message.answer_voice(voice=types.InputFile(f'{personage_voice[character]}_welcome.opus', "r"))
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


@dp.callback_query_handler(text_startswith="help")
async def mood_changed(call: types.CallbackQuery):
     help_type = call.data
     await call.message.edit_text(f'{help_dict[help_type]}')


@dp.message_handler(commands=['end'])
async def char_change(message: types.Message):
    await message.answer('Все. Это конец. Продолжения не будет.')


@dp.message_handler(content_types="text")
async def text_message_handler(message: types.Message):
    if message.is_command():
        return

    request_disp = {"user_id": message.from_user.id, "text": message.text}
    await message.answer_chat_action(types.ChatActions.RECORD_AUDIO)
    tts_answer = requests.post("http://127.0.0.1:5001/text_query", json=request_disp)
    with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
        if "audio" in tts_answer.json():
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

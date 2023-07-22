import sys
import datetime

filename = '/logging/server.log'

def write_log(message):
    with open(filename, 'a') as handler:
        rich_msg = f"{datetime.datetime.now().strftime('%H:%M:%S')} | {message}\n"
        handler.write(rich_msg)

def log(user, message, answer):
    write_log(f'User: {user}, message: {message}, bot_answer: {answer}')

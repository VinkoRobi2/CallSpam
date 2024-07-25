import telebot
import requests
import time
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path='twas.env')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

user_states = {}  

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hola, Soy el bot spammer de NAZICRO, un gusto en poder ayudarte")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    if chat_id not in user_states:
        bot.reply_to(message, "Hola, Soy el bot spammer de NAZICRO, un gusto en poder ayudarte")
        bot.reply_to(message, "Ingresa un número para poder hacerle el flood: ejemplo:+593993451234")
        user_states[chat_id] = 'greeted'
        return
    
    phone_number = message.text.strip()
    if phone_number.startswith('+') and len(phone_number) >= 10:
        bot.reply_to(message, f"Llamando al número {phone_number}...")
        url = f'https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Calls.json'
        data = {
            'To': phone_number,
            'From': TWILIO_NUMBER,
            'Url': 'http://demo.twilio.com/docs/voice.xml'  
        }
        auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        response = requests.post(url, data=data, auth=auth)
        if response.status_code == 201:
            call_sid = response.json().get('sid')
            bot.reply_to(message, f"La llamada se ha realizado con éxito. La llamada se finalizará en 10 segundos.")
            time.sleep(10)
            end_call_url = f'https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Calls/{call_sid}.json'
            end_call_response = requests.post(end_call_url, data={'Status': 'completed'}, auth=auth)
            if end_call_response.status_code == 204:
                bot.reply_to(message, "La llamada se ha finalizado con éxito.")
            else:
                bot.reply_to(message, f"Hubo un problema al finalizar la llamada: {end_call_response.text}")
        else:
            bot.reply_to(message, f"Hubo un problema al realizar la llamada: {response.text}")
    else:
        bot.reply_to(message, "Por favor, ingresa un número de teléfono en formato internacional válido.")

if __name__ == '__main__':
    bot.polling()
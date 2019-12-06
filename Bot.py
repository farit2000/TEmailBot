import os
import telebot
from flask import Flask, request
import requests

TOKEN = '922619910:AAFPTr4Op9SangO9HWkrNx6nvW9otnApiyU'
bot = telebot.TeleBot(token=TOKEN)
server = Flask(__name__)
# Bot's Functionalities
json_str = ''


def send_message(message, text):
    bot.send_message(message.chat.id, text)


# This method will send a message formatted in HTML to the user whenever it starts the bot with the /start command,
# feel free to add as many commands' handlers as you want
@bot.message_handler(commands=['start'])
def send_info(message):
    # update = str(request.stream.read().decode("utf-8"))
    text = (
    "<b>Welcome to the TEmailBot 💎🤖!</b>\n"
    "Say Hello to the bot to get a reply from it!"
    )
    myobj = {'key': json_str}
    resp = requests.post('https://postman-echo.com/post', data=myobj)
    bot.send_message(message.chat.id, resp.text)
    bot.send_message(message.chat.id, text, parse_mode='HTML')


# This method will fire whenever the bot receives a message from a user,
# it will check that there is actually a not empty string in it and, in this case,
# it will check if there is the 'hello' word in it, if so it will reply with the message we defined
@bot.message_handler(func=lambda msg: msg.text is not None)
def reply_to_message(message):
    if 'hello' in message.text.lower():
        send_message(message, 'Hello! How are you doing today?')


# SERVER SIDE
@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    global json_str
    json_str = request.stream.read().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://protected-garden-46141.herokuapp.com/' + TOKEN)
    return "!", 200


def return_update_string(update_str):
    update_request = update_str


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8443)))

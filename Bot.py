import os
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import json

TOKEN = '1064096992:AAEEvJ2RH1Rx9DYcnltlKSP-PNBYCmPd9hw'
bot = telebot.TeleBot(token=TOKEN)
server = Flask(__name__)
json_str = ''


def send_message(message, text):
    bot.send_message(message.chat.id, text)


def make_request(message, update_value):
    mes = str(message)
    username = str(update_value.from_user.username)
    first_name = str(update_value.from_user.first_name)
    last_name = str(update_value.from_user.last_name)
    user_id = str(update_value.from_user.id)
    update_string = {'Message': mes, 'UserId': user_id, 'Username': username, 'FirstName': first_name,
                     'LastName': last_name}
    resp = requests.post('https://temail.azurewebsites.net/api/message/update', json=update_string)
    data_from_server = json.loads(str(resp.text))
    return data_from_server


def gen_markup(button_count, buttons):
    markup = InlineKeyboardMarkup()
    markup.row_width = button_count
    for button in buttons:
        markup.add(InlineKeyboardButton(str(button), callback_data=str(button)))
    return markup


def send_messages_from_server(chat_id, data_from_server):
    if data_from_server["buttons"]:
        bot.send_message(chat_id, str(data_from_server["messages"][0]),
                         reply_markup=gen_markup(len(data_from_server),
                                                 data_from_server["buttons"]))
        return
    if not(data_from_server["buttons"]):
        for item in data_from_server["messages"]:
            bot.send_message(chat_id, str(item))


def edit_preview_messages(call, data_from_server):
    if data_from_server["buttons"]:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="тру-ту-ту",
                              reply_markup=gen_markup(len(data_from_server), data_from_server["buttons"]))
        # bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, call.message.inline_message_id,
        #                               reply_markup=gen_markup(len(data_from_server), data_from_server["buttons"]))
        # bot.edit_message_text(str(data_from_server["messages"][0]), call.message.chat.id, call.message.,
        #                       reply_markup=gen_markup(len(data_from_server), data_from_server["buttons"]))


# This method will send a message formatted in HTML to the user whenever it starts the bot with the /start command,
# feel free to add as many commands' handlers as you want
@bot.message_handler(commands=['start'])
def send_start_info(message):
    bot.send_message(message.chat.id, """
    \
Hi there, I am 💎<b>TemailBot</b>💎.
Here you can create new temporary emails, as well as add lifetime for temporary emails and remove its.
<b>Available commands:</b>
/start - Show instructions for using Temail bot
/cancel - Cancel the current command
/new - Create new temporary email address
/list -  Show created emails
/remove - Remove created email
/change - Rename destination email
/addtime - Add the lifetime of the email
\
""", parse_mode="HTML")


@bot.message_handler(commands=['new', 'change', 'addtime', 'list', 'cancel'])
def send_answers_from_server(message):
    update = telebot.types.Update.de_json(json_str)
    data_from_server = make_request(message.text, update.message)
    send_messages_from_server(message.chat.id, data_from_server)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data_from_server = make_request(str(call.data), call)
    try:
        edit_preview_messages(call, data_from_server)
    except:
        send_messages_from_server(call.message.chat.id, data_from_server)


# This method will fire whenever the bot receives a message from a user,
# it will check that there is actually a not empty string in it and, in this case,
# it will check if there is the 'hello' word in it, if so it will reply with the message we defined
@bot.message_handler(func=lambda msg: msg.text is not None)
def reply_to_message(message):
    update = telebot.types.Update.de_json(json_str)
    data_from_server = make_request(message.text, update.message)
    send_messages_from_server(message.chat.id, data_from_server)


# SERVER SIDE
@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    global json_str
    json_str = request.stream.read().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def web_hook():
    bot.remove_webhook()
    bot.set_webhook(url='https://temail-bot.herokuapp.com/' + TOKEN)
    return "!", 200


def return_update_string(update_str):
    update_request = update_str


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8443)))

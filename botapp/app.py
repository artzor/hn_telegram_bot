import telegram
import telegram.update
import user
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from flask import Flask, Response, request
from settings import settings
import redis
import pymongo
import time

app = Flask(__name__)


def start(bot, update):
    keyboard = [[InlineKeyboardButton("👌 Subscribe", callback_data='sub')],
                [InlineKeyboardButton("😐 Unsubscribe", callback_data='unsub')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Receive notifications about new posts on news.ycombinator.com:',
                              reply_markup=reply_markup)


def help(bot, update):
    reply_markup = telegram.ReplyKeyboardRemove()

    bot.send_message(chat_id=update.message.chat_id,
                     text="help text",
                     reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query

    if query.data == 'sub':
        bot.edit_message_text(text="/subscribe",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)

        user.user_subscribe(bot, query.message.chat_id)

    elif query.data == 'unsub':
        bot.edit_message_text(text="/unsubscribe",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)

        user.user_unsubscribe(bot, query.message.chat_id)


def subscribe(bot, update):
    user.user_subscribe(bot, update.message.chat_id)


def unsubscribe(bot, update):
    user.user_unsubscribe(bot, update.message.chat_id)


def error(bot, update, error):
    print('Update "%s" caused error "%s"', update, error)


def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Sorry, I didn't understand that command.")


def handle_request(bot, update):
    dispatcher = Dispatcher(bot, None)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('subscribe', subscribe))
    dispatcher.add_handler(CommandHandler('unsubscribe', unsubscribe))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_error_handler(error)
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))
    dispatcher.process_update(update)


@app.route(f"/{settings.api_token}", methods=['POST'])
def updates():
    if request.method == 'POST':
        bot = telegram.Bot(settings.api_token)
        update = telegram.update.Update.de_json(request.get_json(), bot)
        handle_request(bot, update)
        response = Response(response='hello',
                            status=200,
                            mimetype='application/json')
        return response


@app.route("/")
def index():
    return 'All work and no play makes jack a dull boy'


def get_hit_count(cache):
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


@app.route("/wh")
def setup_webhook():
    hn_bot = telegram.Bot(settings.api_token)
    time.sleep(0.3)
    certificate = None
    if settings.cert_file:
        certificate =open(settings.cert_file, 'rb')

    ret = hn_bot.set_webhook(url=f'https://{settings.host}/{settings.api_token}',
                             certificate=certificate)

    if ret:
        return f"<h1>Webhook was set to {settings.host}/your_api_token</h1>"
    else:
        return "<h1>Webhook was not set</h1>"


if __name__ == "__main__":
    context = (settings.cert_file, settings.cert_key)
    app.run(host='0.0.0.0',
            port=5000, debug=True,
            ssl_context=context)

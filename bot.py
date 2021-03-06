import logging
import json
import pymorphy2
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from nltk.stem.porter import PorterStemmer
from utils import get_saying

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

morph = pymorphy2.MorphAnalyzer()
porter = PorterStemmer()

# here should be config json with bot_token and database_url
with open('config.json') as f:
    CONFIG = json.load(f)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! I\'m Bobby The Sayer. Tell me one any word like `/tell word` and see my greatness.')


def tell(bot, update, args):
    word = ' '.join(args)
    word = morph.parse(word)[0].normalized[0] # normalize russian
    word = porter.stem(word)
    saying = get_saying(word, CONFIG['database_url'])
    update.message.reply_text(saying)


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    token = CONFIG['bot_token']
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("tell", tell, pass_args=True))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

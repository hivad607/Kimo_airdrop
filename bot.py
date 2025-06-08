

import telegram
from telegram.ext import Updater, CommandHandler

# Replace with your bot token
TOKEN = 'YOUR_BOT_TOKEN'

def start(update, context):
    update.message.reply_text("سلام، خوش آمدی!")

def main():
    updater = Updater(TOKEN, use_context=True)

    # Add a command handler
    updater.dispatcher.add_handler(CommandHandler("start", start))

    # Start the bot
    updater.start_polling()

    # Run until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()

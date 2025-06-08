KIMO Bot Code

import logging
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Connect to SQLite DB
conn = sqlite3.connect('kimo_bot.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    balance INTEGER DEFAULT 0,
    last_claim TEXT
)""")
conn.commit()

# Constants
REWARD = 1  # 1 KIMO per day
COOLDOWN_HOURS = 24

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (user_id, username, balance, last_claim) VALUES (?, ?, ?, ?)",
                       (user_id, username, 0, None))
        conn.commit()
    keyboard = [[InlineKeyboardButton("🔥 Claim KIMO", callback_data='claim')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome to KIMO PowerTap!", reply_markup=reply_markup)

# Balance command
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    bal = result[0] if result else 0
    await update.message.reply_text(f"💰 Your current balance: {bal} KIMO")

# Claim callback
async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    cursor.execute("SELECT balance, last_claim FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    now = datetime.utcnow()
    if user:
        last_claim_str = user[1]
        if last_claim_str:
            last_claim = datetime.strptime(last_claim_str, "%Y-%m-%d %H:%M:%S")
            if now - last_claim < timedelta(hours=COOLDOWN_HOURS):
                remaining = timedelta(hours=COOLDOWN_HOURS) - (now - last_claim)
                await query.answer(text=f"⏳ You already claimed! Try again in {str(remaining).split('.')[0]}")
                return
        new_balance = user[0] + REWARD
        cursor.execute("UPDATE users SET balance=?, last_claim=? WHERE user_id=?",
                       (new_balance, now.strftime("%Y-%m-%d %H:%M:%S"), user_id))
        conn.commit()
        await query.answer(text="✅ KIMO Claimed!")
        await query.edit_message_text(f"You received {REWARD} KIMO! 💸")
    else:
        await query.answer(text="❗ Please use /start first.")

# Main
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CallbackQueryHandler(claim, pattern='^claim$'))
    app.run_polling()



import logging
import asyncio
import os
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from flask import Flask, request

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")  # ست کن در Railway
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # آدرس کامل URL (مثلاً: https://yourapp.up.railway.app)

PORT = int(os.environ.get('PORT', 8443))  # پورت که Railway ارائه میده

user_data = {}
app_flask = Flask(__name__)  # Flask app برای Webhook

telegram_app = Application.builder().token(TOKEN).build()

# ------------------ فرمان‌ها ------------------ #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفاً اطلاعات رو طبق فرمت وارد کن...")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("پیام دریافت شد.")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ------------------ Webhook route ------------------ #
@app_flask.post(f"/webhook/{TOKEN}")
def webhook():
    telegram_app.update_queue.put_nowait(Update.de_json(request.get_json(force=True), telegram_app.bot))
    return "ok"

# ------------------ راه‌اندازی ------------------ #
async def set_webhook():
    await telegram_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook/{TOKEN}")
    print(f"Webhook set to {WEBHOOK_URL}/webhook/{TOKEN}")

def run():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())
    app_flask.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    run()

import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import math

# خواندن توکن از متغیر محیطی
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set")

# تابع محاسبه شانس و ریسک به ریوارد
def calculate_odds(prizes: dict, total_tickets: int, ticket_price: float):
    """
    prizes: dict جایزه و تعداد، مثل {'10': 5, '15': 3}
    total_tickets: تعداد کل بلیت‌ها (تیکت‌ها)
    ticket_price: قیمت هر تیکت
    """
    total_value = 0
    total_prizes = 0
    for price_str, count in prizes.items():
        price = float(price_str)
        total_value += price * count
        total_prizes += count

    # احتمال بردن حداقل یک جایزه:
    # فرض می‌کنیم هر بلیت شانس یکسان داره و بدون جایگزینی کشیده می‌شه.
    # احتمال برنده نشدن = (تعداد تیکت‌های غیر جایزه) / کل تیکت‌ها = (total_tickets - total_prizes)/total_tickets
    # احتمال برد = 1 - احتمال برنده نشدن
    if total_tickets == 0:
        win_prob = 0
    else:
        win_prob = total_prizes / total_tickets

    # ریسک به ریوارد = (کل هزینه خرید بلیت‌ها برای بردن یک جایزه) / ارزش جایزه
    # میانگین هزینه برای بردن یک جایزه = ticket_price / win_prob
    # risk_to_reward = هزینه / ارزش میانگین جایزه
    avg_prize_value = total_value / total_prizes if total_prizes > 0 else 0

    if win_prob == 0:
        risk_to_reward = math.inf
    else:
        risk_to_reward = (ticket_price / win_prob) / avg_prize_value if avg_prize_value > 0 else math.inf

    return win_prob, risk_to_reward

# دستورات ربات

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! برای محاسبه شانس و ریسک به ریوارد قرعه‌کشی، لطفاً اطلاعات رو به این شکل وارد کن:\n\n"
        "format:\n"
        "قیمت_جایزه:تعداد, قیمت_جایزه:تعداد,...\n"
        "تعداد_کل_تیکت\n"
        "قیمت_هر_تیکت\n\n"
        "مثال:\n"
        "10:5,15:3\n"
        "100\n"
        "0.2\n\n"
        "اکنون اطلاعات را ارسال کن."
    )

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lines = text.split("\n")
    if len(lines) != 3:
        await update.message.reply_text("خطا: لطفاً دقیقاً سه خط اطلاعات ارسال کن.")
        return

    try:
        # پردازش جایزه‌ها
        prizes_raw = lines[0].split(",")
        prizes = {}
        for item in prizes_raw:
            price, count = item.split(":")
            prizes[price.strip()] = int(count.strip())

        total_tickets = int(lines[1].strip())
        ticket_price = float(lines[2].strip())

        win_prob, risk_to_reward = calculate_odds(prizes, total_tickets, ticket_price)

        text = (
            f"📊 نتیجه محاسبه:\n"
            f"🔸 احتمال برد حداقل یک جایزه: {win_prob*100:.2f}%\n"
            f"🔸 ریسک به ریوارد (کمتر بهتر): {risk_to_reward:.2f}\n\n"
            f"(ریسک به ریوارد = هزینه متوسط برای بردن یک جایزه / ارزش میانگین جایزه)"
        )
        await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text(f"خطا در پردازش داده‌ها: {e}\nلطفاً فرمت ورودی را دوباره بررسی کن.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("calc", calculate))
    app.add_handler(CommandHandler("calculate", calculate))

    # برای دریافت پیام متنی کاربر که حاوی اطلاعات است:
    app.add_handler(CommandHandler("calculate", calculate))
    app.add_handler(CommandHandler("calc", calculate))
    app.add_handler(CommandHandler("start", start))

    # پیام متنی معمولی را به تابع calculate وصل می‌کنیم (اگر می‌خواهی فقط متن عادی)
    app.add_handler(CommandHandler("calculate", calculate))
    app.add_handler(CommandHandler("calc", calculate))

    from telegram.ext import MessageHandler, filters
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()

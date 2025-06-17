import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set")

def calculate_odds(prizes: dict, total_tickets: int, ticket_price: float):
    total_value = 0
    total_prizes = 0
    for price_str, count in prizes.items():
        price = float(price_str)
        total_value += price * count
        total_prizes += count

    win_prob = total_prizes / total_tickets if total_tickets else 0
    avg_prize_value = total_value / total_prizes if total_prizes else 0

    risk_to_reward = (ticket_price / win_prob) / avg_prize_value if win_prob and avg_prize_value else float("inf")
    return win_prob, risk_to_reward

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! لطفاً اطلاعات قرعه‌کشی را در ۳ خط بفرست:\n"
        "مثال:\n"
        "10:5,15:3\n"
        "100\n"
        "0.2"
    )

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = update.message.text.strip().split("\n")
    if len(lines) != 3:
        await update.message.reply_text("فرمت اشتباه است. لطفاً دقیقاً ۳ خط وارد کن.")
        return

    try:
        prizes_raw = lines[0].split(",")
        prizes = {price.strip(): int(count.strip()) for price, count in (item.split(":") for item in prizes_raw)}
        total_tickets = int(lines[1].strip())
        ticket_price = float(lines[2].strip())

        win_prob, risk_to_reward = calculate_odds(prizes, total_tickets, ticket_price)

        await update.message.reply_text(
            f"📊 احتمال برد: {win_prob * 100:.2f}%\n"
            f"📉 ریسک به ریوارد: {risk_to_reward:.2f}"
        )
    except Exception as e:
        await update.message.reply_text(f"خطا: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))
    app.run_polling()

if __name__ == "__main__":
    main()
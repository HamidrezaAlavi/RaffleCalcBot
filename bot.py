import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")

def analyze_lottery(prizes, total_tickets, ticket_price):
    total_prizes = sum([count for count, _ in prizes])
    total_value = sum([count * value for count, value in prizes])

    p_win = total_prizes / total_tickets
    ev = total_value / total_tickets
    rr = ticket_price / ev if ev != 0 else float('inf')

    return {
        'probability_of_winning': round(p_win * 100, 2),
        'expected_value': round(ev, 4),
        'risk_to_reward': round(rr, 2)
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! فرمت پیام:\n\nجوایز: 5x10,3x15\nتعداد تیکت: 1000\nقیمت تیکت: 0.2")

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        lines = update.message.text.split('\n')
        prize_line = next(l for l in lines if 'x' in l)
        ticket_line = next(l for l in lines if 'تیکت' in l)
        price_line = next(l for l in lines if 'قیمت' in l)

        prizes = [(int(p.split('x')[0]), float(p.split('x')[1])) for p in prize_line.split(':')[1].split(',')]
        total_tickets = int(ticket_line.split(':')[1])
        ticket_price = float(price_line.split(':')[1])

        result = analyze_lottery(prizes, total_tickets, ticket_price)

        await update.message.reply_text(
            f"📌 احتمال برد: {result['probability_of_winning']}٪\n"
            f"💰 ارزش مورد انتظار: {result['expected_value']} $\n"
            f"⚖️ ریسک به ریوارد: {result['risk_to_reward']}"
        )
    except:
        await update.message.reply_text("❌ فرمت اشتباهه! فرمت نمونه:\nجوایز: 5x10,3x15\nتعداد تیکت: 1000\nقیمت تیکت: 0.2")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    app.run_polling()

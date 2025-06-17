import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 به ربات محاسبه‌گر شانس قرعه‌کشی خوش اومدی!\n\n"
        "این ربات بهت کمک می‌کنه که شانس بردن در قرعه‌کشی‌های تلگرامی رو حساب کنی و ببینی آیا ارزش شرکت کردن داره یا نه.\n\n"
        "🔢 لطفاً اطلاعات قرعه‌کشی رو در **سه خط جداگانه** ارسال کن به این شکل:\n\n"
        "`10:5,15:3`\n"
        "`100`\n"
        "`0.2`\n\n"
        "📌 توضیحات:\n"
        "1️⃣ خط اول: لیست جوایز به فرمت `قیمت:تعداد` جدا شده با کاما (،)\n"
        "2️⃣ خط دوم: تعداد کل تیکت‌هایی که همه شرکت‌کننده‌ها خریدن\n"
        "3️⃣ خط سوم: قیمت هر تیکت (به دلار)\n\n"
        "بعد از اون، ازت می‌پرسم چندتا تیکت می‌خوای بخری، و نتیجه‌ی دقیق رو بهت می‌گم. 😊"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message = update.message.text.strip()

    if chat_id not in user_data:
        user_data[chat_id] = {"step": 1, "inputs": []}

    data = user_data[chat_id]

    if data["step"] <= 3:
        data["inputs"].append(message)
        data["step"] += 1

    if data["step"] == 4:
        try:
            prizes_line, total_tickets_line, ticket_price_line = data["inputs"]
            prize_parts = prizes_line.split(",")

            prizes = []
            total_reward_value = 0
            total_prizes = 0

            for part in prize_parts:
                value, count = map(float, part.strip().split(":"))
                prizes.append((value, int(count)))
                total_reward_value += value * int(count)
                total_prizes += int(count)

            total_tickets = int(total_tickets_line)
            ticket_price = float(ticket_price_line)

            chance_per_ticket = total_prizes / total_tickets
            expected_return_per_ticket = total_reward_value / total_tickets
            risk_to_reward = expected_return_per_ticket / ticket_price

            data["results"] = {
                "chance_per_ticket": chance_per_ticket,
                "risk_to_reward": risk_to_reward,
                "ticket_price": ticket_price
            }

            await update.message.reply_text(
                f"📊 احتمال برد هر تیکت: **{chance_per_ticket * 100:.2f}%**\n"
                f"📉 نسبت ریسک به ریوارد: **{risk_to_reward:.2f}**\n\n"
                "🎟️ حالا بگو چندتا تیکت می‌خوای بخری؟"
            )
            data["step"] = 5

        except Exception as e:
            await update.message.reply_text("⚠️ فرمت اطلاعاتی که دادی نادرسته. لطفاً با دستور /start دوباره شروع کن.")
            user_data.pop(chat_id)

    elif data["step"] == 5:
        try:
            count = int(message)
            chance = data["results"]["chance_per_ticket"]
            rtr = data["results"]["risk_to_reward"]
            price = data["results"]["ticket_price"]

            total_chance = 1 - ((1 - chance) ** count)
            total_cost = count * price
            expected_gain = count * chance * (rtr * price)

            await update.message.reply_text(
                f"🎟️ تعداد تیکت: **{count}**\n\n"
                f"✅ شانس برد کلی: **{total_chance * 100:.2f}%**\n"
                f"📉 نسبت ریسک به ریوارد: **{rtr:.2f}**\n"
                f"💸 مجموع هزینه: **{total_cost:.2f}$**\n"
            )
            user_data.pop(chat_id)

        except:
            await update.message.reply_text("❌ لطفاً فقط یک عدد معتبر برای تعداد تیکت وارد کن.")

app = ApplicationBuilder().token("توکن بات اینجا").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
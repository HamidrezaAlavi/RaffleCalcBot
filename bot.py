import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 به ربات محاسبه‌گر شانس قرعه‌کشی خوش اومدی!\n\n"
        "این ربات بهت کمک می‌کنه که شانس بردن در قرعه‌کشی‌های تلگرامی رو حساب کنی و ببینی آیا ارزش شرکت کردن داره یا نه.\n\n"
        "🔢 لطفاً اطلاعات قرعه‌کشی رو در *سه خط جداگانه* ارسال کن به این شکل:\n\n"
        "`10:5,15:3`\n"
        "`100`\n"
        "`0.2`\n\n"
        "📌 توضیحات:\n"
        "1️⃣ خط اول: لیست جوایز به فرمت `قیمت:تعداد` جدا شده با کاما (،)\n"
        "2️⃣ خط دوم: تعداد کل تیکت‌هایی که همه شرکت‌کننده‌ها خریدن\n"
        "3️⃣ خط سوم: قیمت هر تیکت\n\n"
        "بعد از اون، ازت می‌پرسم چندتا تیکت می‌خوای بخری، و نتیجه‌ی دقیق رو بهت می‌گم. 😊",
        parse_mode='Markdown'
    )

async def reset_user_data(chat_id):
    if chat_id in user_data:
        user_data.pop(chat_id)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message = update.message.text.strip()

    if chat_id not in user_data:
        user_data[chat_id] = {"step": 1, "inputs": []}

    data = user_data[chat_id]

    if data["step"] <= 3:
        data["inputs"].append(message)

        if data["step"] == 1:
            await update.message.reply_text("✅ جوایز دریافت شد. حالا تعداد کل تیکت‌ها رو وارد کن:")
        elif data["step"] == 2:
            await update.message.reply_text("✅ تعداد کل تیکت‌ها دریافت شد. حالا قیمت هر تیکت رو وارد کن:")

        data["step"] += 1

    elif data["step"] == 4:
        try:
            prizes_line, total_tickets_line, ticket_price_line = data["inputs"]
            prize_parts = prizes_line.replace("،", ",").split(",")
            prizes = []
            total_reward_value = 0
            total_prizes = 0

            for part in prize_parts:
                if ":" not in part:
                    raise ValueError("فرمت جایزه نادرست")
                value_str, count_str = part.strip().split(":")
                value = float(value_str)
                count = int(count_str)
                prizes.append((value, count))
                total_reward_value += value * count
                total_prizes += count

            total_tickets = int(total_tickets_line)
            ticket_price = float(ticket_price_line)

            if total_tickets <= 0 or ticket_price <= 0 or total_prizes <= 0:
                raise ValueError("مقادیر باید مثبت باشند")

            if total_prizes > total_tickets:
                raise ValueError("تعداد جوایز نمی‌تواند بیشتر از تعداد کل تیکت‌ها باشد")

            chance_per_ticket = total_prizes / total_tickets
            expected_return_per_ticket = total_reward_value / total_tickets
            risk_to_reward = expected_return_per_ticket / ticket_price

            data["results"] = {
                "chance_per_ticket": chance_per_ticket,
                "risk_to_reward": risk_to_reward,
                "ticket_price": ticket_price,
                "expected_return_per_ticket": expected_return_per_ticket,
                "total_tickets": total_tickets,
                "total_prizes": total_prizes,
                "total_reward_value": total_reward_value
            }

            evaluation = ""
            if risk_to_reward > 1.0:
                evaluation = "🟢 *عالی!* احتمالاً سودآور است"
            elif risk_to_reward > 0.7:
                evaluation = "🟡 *متوسط* - ممکن است ارزش داشته باشد"
            else:
                evaluation = "🔴 *ریسکی* - احتمالاً زیان‌آور است"

            await update.message.reply_text(
                f"📊 *نتایج تحلیل:*\n\n"
                f"🎯 احتمال برد هر تیکت: *{chance_per_ticket * 100:.2f}%*\n"
                f"💰 بازگشت متوقع هر تیکت: *${expected_return_per_ticket:.3f}*\n"
                f"📈 نسبت ریسک به ریوارد: *{risk_to_reward:.2f}*\n\n"
                f"{evaluation}\n\n"
                f"🎟️ حالا بگو چندتا تیکت می‌خوای بخری؟\n"
                f"_(یا /start برای شروع دوباره)_",
                parse_mode='Markdown'
            )
            data["step"] = 5

        except ValueError as ve:
            await update.message.reply_text(
                f"⚠️ خطا در داده‌ها: {str(ve)}\n"
                "لطفاً با دستور /start دوباره شروع کن.",
                parse_mode='Markdown'
            )
            await reset_user_data(chat_id)
        except Exception:
            await update.message.reply_text(
                "⚠️ فرمت اطلاعاتی که دادی نادرسته.\n"
                "مثال صحیح:\n"
                "`10:5,15:3`\n`100`\n`0.2`\n\n"
                "لطفاً با دستور /start دوباره شروع کن.",
                parse_mode='Markdown'
            )
            await reset_user_data(chat_id)

    elif data["step"] == 5:
        try:
            count = int(message)
            if count <= 0:
                await update.message.reply_text("❌ تعداد تیکت باید عدد مثبت باشد!")
                return

            results = data["results"]
            chance = results["chance_per_ticket"]
            rtr = results["risk_to_reward"]
            price = results["ticket_price"]
            expected_return = results["expected_return_per_ticket"]

            total_chance = 1 - ((1 - chance) ** count)
            total_cost = count * price
            expected_total_return = count * expected_return
            expected_profit = expected_total_return - total_cost

            status_emoji = "🟢" if expected_profit > 0 else "🔴"
            profit_text = f"سود متوقع: *${expected_profit:.2f}*" if expected_profit > 0 else f"زیان متوقع: *${abs(expected_profit):.2f}*"

            await update.message.reply_text(
                f"🎟️ *نتیجه نهایی برای {count} تیکت:*\n\n"
                f"✅ شانس برد کلی: *{total_chance * 100:.2f}%*\n"
                f"💸 مجموع هزینه: *${total_cost:.2f}*\n"
                f"💰 بازگشت متوقع: *${expected_total_return:.2f}*\n"
                f"{status_emoji} {profit_text}\n"
                f"📈 نسبت ریسک به ریوارد: *{rtr:.2f}*\n\n"
                f"_برای قرعه‌کشی جدید از /start استفاده کن_",
                parse_mode='Markdown'
            )

            await reset_user_data(chat_id)

        except ValueError:
            await update.message.reply_text(
                "❌ لطفاً فقط یک عدد صحیح معتبر برای تعداد تیکت وارد کن.\n"
                "مثال: `5`",
                parse_mode='Markdown'
            )
        except Exception:
            await update.message.reply_text("❌ خطا در پردازش. لطفاً دوباره تلاش کن.")

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await reset_user_data(chat_id)
    await start(update, context)

async def main():
    app = Application.builder().token("7740910314:AAEzgnRxolPt3h-El0PHdfJFYBvc9cqiGIU").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 ربات شروع شد...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

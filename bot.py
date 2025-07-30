import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

API_TOKEN = os.getenv("API_TOKEN")
BOT_MAIN_CHANNEL = os.getenv("BOT_MAIN_CHANNEL")

bot = telebot.TeleBot(API_TOKEN)
group_channels = {}  # تخزين مؤقت

def is_user_subscribed(user_id, channel_username):
    try:
        member = bot.get_chat_member(channel_username, user_id)
        return member.status in ['member', 'creator', 'administrator']
    except:
        return False

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    if is_user_subscribed(user_id, BOT_MAIN_CHANNEL):
        bot.send_message(message.chat.id, "مرحبًا بك! يمكنك الآن استخدام البوت وإضافته إلى مجموعتك.")
    else:
        markup = InlineKeyboardMarkup()
        join_button = InlineKeyboardButton(
            text="🟢 يجب عليك الاشتراك في قناة البوت لاستخدامه",
            url=f"https://t.me/{BOT_MAIN_CHANNEL[1:]}"
        )
        check_button = InlineKeyboardButton(text="✅ تحقق من الاشتراك", callback_data="check_subscription")
        markup.add(join_button)
        markup.add(check_button)
        bot.send_message(message.chat.id,
                         f"""📢 يعمل هذا البوت على زيادة الاشتراكات وتعزيز التفاعل في القنوات والمجموعات من خلال الاشتراك الإجباري وأدوات إدارة الأعضاء.

🚸| عذراً عزيزي .
🔰| عليك الاشتراك في قناة البوت لتتمكن من استخدامه: https://t.me/{BOT_MAIN_CHANNEL[1:]}
‼️| اشترك ثم أرسل /start""", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def callback_check_subscription(call):
    user_id = call.from_user.id
    if is_user_subscribed(user_id, BOT_MAIN_CHANNEL):
        bot.answer_callback_query(call.id, "✅ تم التحقق! أنت مشترك.", show_alert=True)
        bot.send_message(call.message.chat.id, "شكرًا لاشتراكك! يمكنك الآن استخدام البوت.")
    else:
        bot.answer_callback_query(call.id, "🚫 لم يتم العثور على اشتراكك في القناة.", show_alert=True)

@bot.message_handler(commands=['setchannel'])
def set_channel(message):
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "❌ هذا الأمر يستخدم فقط داخل المجموعات.")
        return
    args = message.text.split()
    if len(args) != 2 or not args[1].startswith('@'):
        bot.reply_to(message, "❗ استخدم الأمر بالشكل الصحيح: /setchannel @channelname")
        return
    group_channels[message.chat.id] = args[1]
    bot.reply_to(message, f"✅ تم تعيين قناة الاشتراك لهذه المجموعة: {args[1]}")

@bot.message_handler(content_types=['new_chat_members'])
def new_member_handler(message):
    chat_id = message.chat.id
    channel = group_channels.get(chat_id)
    for new_member in message.new_chat_members:
        if not channel:
            continue
        if not is_user_subscribed(new_member.id, channel):
            try:
                bot.restrict_chat_member(chat_id, new_member.id, can_send_messages=False)
                bot.send_message(chat_id,
                                 f"🚫 مرحبًا {new_member.first_name}، يجب عليك الاشتراك في القناة {channel} قبل المشاركة.")
            except Exception as e:
                print(f"خطأ أثناء تقييد العضو: {e}")

bot.infinity_polling()

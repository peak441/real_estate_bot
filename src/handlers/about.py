from telebot import types

def register(bot):

    @bot.message_handler(func=lambda m: m.text == "ℹ️ About Us")
    def about_us(message):
        text = """
🏠 *Real Estate Bot*
Your trusted partner in finding the perfect home.

📍 *Address:* 123 Business Ave, Phnom Penh
📞 *Phone:* +855 12 345 678
📧 *Email:* info@realestatebot.com

We specialize in Houses, Apartments, Land, and Villas.
        """
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🏠 View Properties", "🔍 Search Property")
        markup.add("📞 Contact Agent", "ℹ️ About Us")

        bot.send_message(
            message.chat.id,
            text,
            parse_mode="Markdown",
            reply_markup=markup
        )
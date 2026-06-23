from telebot import types
from src.services.user_service import create_user

def start(bot, message):
    try:
        with bot.flask_app.app_context():
            create_user(
                message.from_user.id,
                message.from_user.username
            )

            keyboard = types.ReplyKeyboardMarkup(
                resize_keyboard=True
            )

            keyboard.add(
                "🏠 View Properties",
                "🔍 Search Property"
            )

            keyboard.add(
                "⭐ Favorites",
                "📞 Contact Agent"
            )

            keyboard.add("Language", "ℹ️ About Us")

            bot.send_message(
                message.chat.id,
                "Welcome to Real Estate Bot 🏠",
                reply_markup=keyboard
            )

    except Exception as e:
        print(f"Error in start handler: {e}")
        bot.send_message(
            message.chat.id,
            "An error occurred while initializing your account. Please try again later."
        )

def register(bot):
    @bot.message_handler(commands=["start"])
    def handle_start(message):
        start(bot, message)
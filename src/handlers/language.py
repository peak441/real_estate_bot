from database.db import db
from database.models import User

def register(bot):

    @bot.message_handler(
        commands=["language"]
    )
    def language_menu(message):

        bot.send_message(
            message.chat.id,
            """
Choose Language

1. English
2. Khmer
"""
        )


    @bot.message_handler(
        func=lambda m:
        m.text in [
            "English",
            "Khmer"
        ]
    )
    def set_language(message):

        user = db.session.query(User).filter_by(telegram_id=message.from_user.id).first()

        if not user:
            bot.send_message(
                message.chat.id,
                "Please type /start first."
            )
            return

        if message.text == "Khmer":
            user.language = "km"
        else:
            user.language = "en"

        db.session.commit()

        bot.send_message(
            message.chat.id,
            "Language updated."
        )
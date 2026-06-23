from telebot import types

from database.db import db

from database.models import (
    User,
    Favorite,
    Property
)

def register(bot):

    @bot.callback_query_handler(
        func=lambda c:
        c.data.startswith("save_")
    )
    def save_property(call):
        with bot.flask_app.app_context():
            property_id = int(
                call.data.split("_")[1]
            )

            user = db.session.query(User).filter_by(telegram_id=call.from_user.id).first()

            if not user:
                bot.answer_callback_query(
                    call.id,
                    "Please /start the bot first."
                )
                return

            # Verify property exists before saving
            prop = db.session.get(Property, property_id)
            if not prop:
                bot.answer_callback_query(call.id, "Property not found.")
                return

            existing = db.session.query(Favorite).filter_by(user_id=user.id, property_id=property_id).first()

            if existing:

                bot.answer_callback_query(
                    call.id,
                    "Already saved."
                )
                return

            fav = Favorite(
                user_id=user.id,
                property_id=property_id
            )

            db.session.add(fav)

            db.session.commit()

            bot.answer_callback_query(
                call.id,
                "Saved successfully ⭐"
            )

    @bot.callback_query_handler(func=lambda c: c.data.startswith("unsave_"))
    def unsave_property(call):
        with bot.flask_app.app_context():
            parts = call.data.split("_")
            property_id = int(parts[1])
            # Check if the request came from the favorites list to trigger a list refresh
            is_from_list = len(parts) > 2 and parts[2] == "list"

            user = db.session.query(User).filter_by(telegram_id=call.from_user.id).first()
            if not user:
                bot.answer_callback_query(call.id, "User not found.")
                return

            fav = db.session.query(Favorite).filter_by(
                user_id=user.id, 
                property_id=property_id
            ).first()

            if fav:
                db.session.delete(fav)
                db.session.commit()
                bot.answer_callback_query(call.id, "Removed from favorites.")
            else:
                bot.answer_callback_query(call.id, "Not in favorites.")

            if is_from_list:
                # Refresh the favorites list
                show_favorites_logic(call.message, call.from_user.id, edit=True)
            else:
                # Refresh property details (toggle button)
                from src.handlers.property import property_details
                property_details(call)

    @bot.message_handler(
        func=lambda m:
        m.text == "⭐ Favorites"
    )
    def show_favorites(message):
        show_favorites_logic(message, message.from_user.id)

    def show_favorites_logic(message, telegram_id, edit=False):
        with bot.flask_app.app_context():
            user = db.session.query(User).filter_by(telegram_id=telegram_id).first()

            if not user:
                text = "Please type /start first to register your account."
                if edit:
                    bot.edit_message_text(text, message.chat.id, message.message_id)
                else:
                    bot.send_message(message.chat.id, text)
                return

            favorites = db.session.query(Favorite).filter_by(user_id=user.id).all()

            if not favorites:
                text = "No favorites yet. Go find your dream home! 🏠"
                if edit:
                    bot.edit_message_text(text, message.chat.id, message.message_id)
                else:
                    bot.send_message(message.chat.id, text)
                return

            text = "⭐ Favorite Properties\n\n"
            markup = types.InlineKeyboardMarkup()

            for fav in favorites:
                prop = db.session.get(Property, fav.property_id)
                if prop:
                    markup.row(
                        types.InlineKeyboardButton(f"🏠 {prop.title}", callback_data=f"property_{prop.id}"),
                        types.InlineKeyboardButton("❌ Remove", callback_data=f"unsave_{prop.id}_list")
                    )

            if edit:
                try:
                    bot.edit_message_text(text, message.chat.id, message.message_id, reply_markup=markup)
                except Exception:
                    pass # Message might be identical if nothing changed
            else:
                bot.send_message(message.chat.id, text, reply_markup=markup)
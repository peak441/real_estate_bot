from database.db import db
from database.models import Property
from telebot import types

def register(bot):

    @bot.message_handler(
        func=lambda m:
        m.text == "🔍 Search Property"
    )
    def search_prompt(message):

        msg = bot.send_message(
            message.chat.id,
            "Enter location or your maximum budget (e.g., Phnom Penh or 50000):"
        )

        bot.register_next_step_handler(
            msg,
            search_location
        )


    def search_location(message):
        with bot.flask_app.app_context():
            search_query = message.text
            
            try:
                # Check if user entered a budget
                budget = float(search_query.replace('$', '').replace(',', ''))
                results = db.session.query(Property).filter(Property.price <= budget).all()
                search_type = f"budget under ${budget:,.0f}"
            except ValueError:
                # Search by location
                results = db.session.query(Property).filter(
                    Property.location.ilike(f"%{search_query}%")
                ).all()
                search_type = f"location '{search_query}'"

            if not results:
                bot.send_message(
                    message.chat.id,
                    f"No properties found matching {search_type}."
                )
                return

            markup = types.InlineKeyboardMarkup()
            for p in results:
                markup.add(
                    types.InlineKeyboardButton(
                        f"🏠 {p.title} - ${p.price}",
                        callback_data=f"property_{p.id}"
                    )
                )

            bot.send_message(
                message.chat.id,
                f"🔍 Found {len(results)} matching properties for {search_type}:",
                reply_markup=markup
            )
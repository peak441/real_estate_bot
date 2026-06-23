from flask import current_app
from database.db import db
from database.models import (
    User,
    Inquiry
)

pending_property = {}


def register(bot):

    @bot.message_handler(func=lambda m: m.text == "📞 Contact Agent")
    def contact_agent_general(message):
        pending_property[message.from_user.id] = None
        msg = bot.send_message(
            message.chat.id,
            "Enter your phone number:"
        )
        bot.register_next_step_handler(
            msg,
            save_phone
        )

    @bot.callback_query_handler(
        func=lambda c:
        c.data.startswith("contact_")
    )
    def contact_property(call):

        property_id = int(
            call.data.split("_")[1]
        )

        pending_property[
            call.from_user.id
        ] = property_id

        msg = bot.send_message(
            call.message.chat.id,
            "Enter your phone number:"
        )

        bot.register_next_step_handler(
            msg,
            save_phone
        )


    def save_phone(message):

        user_id = message.from_user.id

        phone = message.text

        msg = bot.send_message(
            message.chat.id,
            "Enter your message:"
        )

        bot.register_next_step_handler(
            msg,
            lambda m:
            save_inquiry(
                m,
                phone
            )
        )


    def save_inquiry(
            message,
            phone
    ):

        telegram_id = message.from_user.id

        with bot.flask_app.app_context():
            user = db.session.query(User).filter_by(telegram_id=telegram_id).first()

            if not user:
                bot.send_message(
                    message.chat.id,
                    "Please type /start first to register."
                )
                return

            # Pop the pending property to clean up memory
            property_id = pending_property.pop(telegram_id, "EXPIRED")

            if property_id == "EXPIRED":
                bot.send_message(
                    message.chat.id,
                    "❌ Error: Your request has expired. Please try contacting the agent again from the property details."
                )
                return

            inquiry = Inquiry(
                user_id=user.id,
                property_id=property_id,
                phone=phone,
                message=message.text
            )

            db.session.add(inquiry)
            db.session.commit()

            bot.send_message(
                message.chat.id,
                "✅ Inquiry sent successfully."
            )
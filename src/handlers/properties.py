from telebot import types
from src.services.property_service import get_properties_with_thumbnails

def register(bot):
    @bot.message_handler(func=lambda message: message.text == "🏠 View Properties")
    def view_properties(message):
        try:
            with bot.flask_app.app_context():
                properties = get_properties_with_thumbnails()

                if not properties:
                    bot.send_message(message.chat.id, "No properties found at the moment.")
                    return

                for prop in properties:
                    caption = (
                        f"🏢 *{prop.title}*\n"
                        f"🏙 *Area:* {prop.province if prop.province else 'Phnom Penh'}\n"
                        f"📍 {prop.location}\n\n"
                        f"Use the search menu for more details."
                    )

                    # If an image_url exists from the JOIN, send it as a photo
                    if prop.image_url:
                        bot.send_photo(
                            message.chat.id,
                            prop.image_url,
                            caption=caption,
                            parse_mode="Markdown"
                        )
                    else:
                        # Fallback if no image is found
                        bot.send_message(
                            message.chat.id,
                            caption,
                            parse_mode="Markdown"
                        )
        except Exception as e:
            print(f"Error in view_properties: {e}")
            bot.send_message(message.chat.id, "An error occurred while fetching properties.")
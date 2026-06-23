from telebot import types
from telebot.types import (
    InputMediaPhoto
)
from database.db import db
from database.models import Property, PropertyImage, User, Favorite
from sqlalchemy.orm import joinedload

# Default image URL to show if a property has no images in the database
PLACEHOLDER_IMAGE = "https://placehold.co/600x400?text=No+Image+Available"

def register(bot):

    def get_category_markup():
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.row(
            types.InlineKeyboardButton("🏠 House", callback_data="type_House"),
            types.InlineKeyboardButton("🏢 Apartment", callback_data="type_Apartment")
        )
        markup.row(
            types.InlineKeyboardButton(" Land", callback_data="type_Land"),
            types.InlineKeyboardButton("🏡 Villa", callback_data="type_Villa")
        )
        markup.add(
            types.InlineKeyboardButton("📋 All Properties", callback_data="type_all"),
            types.InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")
        )
        return markup

    @bot.message_handler(func=lambda m: m.text == "🏠 View Properties")
    def choose_type(message):
        markup = get_category_markup()
        
        bot.send_message(
            message.chat.id,
            "🏢 *Property Categories*\n\nSelect the type of property you are looking for:",
            parse_mode="Markdown",
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda c: c.data == "back_to_main")
    def back_to_main(call):
        bot.answer_callback_query(call.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # Trigger the start command to refresh the reply keyboard UI
        from src.handlers.start import start
        start(bot, call.message)

    @bot.callback_query_handler(func=lambda c: c.data.startswith("type_"))
    def list_by_type(call):
        bot.answer_callback_query(call.id)
        p_type = call.data.split("_")[1]
        
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("🏙 Phnom Penh", callback_data=f"loc_{p_type}_Phnom Penh"),
            types.InlineKeyboardButton("🏡 Other Provinces", callback_data=f"loc_{p_type}_Provinces")
        )
        markup.add(types.InlineKeyboardButton("🌍 All Locations", callback_data=f"loc_{p_type}_all"))
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_to_types"))

        display_name = p_type if p_type != "all" else "All"
        try:
            bot.edit_message_text(
                f"📍 *Location Selection*\n\nCategory: *{display_name}*\n\nSelect a location to filter results:",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=markup
            )
        except Exception:
            pass

    @bot.callback_query_handler(func=lambda c: c.data == "back_to_types")
    def back_to_types(call):
        bot.answer_callback_query(call.id)
        markup = get_category_markup()
        try:
            bot.edit_message_text(
                "🏢 *Property Categories*\n\nSelect the type of property you are looking for:",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=markup
            )
        except Exception:
            pass

    @bot.callback_query_handler(func=lambda c: c.data.startswith("loc_"))
    def list_by_location(call):
        bot.answer_callback_query(call.id)
        parts = call.data.split("_")
        p_type = parts[1]
        location = parts[2]
        display_properties(call.message, page=1, p_type=p_type, location=location, edit=True)

    def display_properties(message, page=1, p_type="all", location="all", edit=False):
        with bot.flask_app.app_context():
            query = db.session.query(Property)
            if p_type != "all":
                query = query.filter_by(property_type=p_type)
            
            if location == "Phnom Penh":
                query = query.filter(
                    (Property.province.ilike("Phnom Penh")) | 
                    (Property.location.ilike("%Phnom Penh%"))
                )
            elif location == "Provinces":
                query = query.filter(
                    (Property.province.is_(None) | Property.province.notilike("Phnom Penh")) &
                    (~Property.location.ilike("%Phnom Penh%"))
                )
            
            per_page = 5
            total = query.count()
            items = query.offset((page - 1) * per_page).limit(per_page).all()
            has_next = (page * per_page) < total
            has_prev = page > 1

            if not items:
                display_type = p_type if p_type != 'all' else 'properties'
                loc_text = f" in {location}" if location != "all" else ""
                text = f"No {display_type} found{loc_text}."
                
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🔙 Back to Categories", callback_data="back_to_types"))
                
                if edit and message.content_type == 'text':
                    bot.edit_message_text(text, message.chat.id, message.message_id, reply_markup=markup)
                else:
                    bot.send_message(message.chat.id, text, reply_markup=markup)
                return

            markup = types.InlineKeyboardMarkup()
            for prop in items:
                markup.add(
                    types.InlineKeyboardButton(
                        f"🏠 {prop.title} | ${prop.price:,.0f}" if prop.price else prop.title,
                        callback_data=f"property_{prop.id}"
                    )
                )
            
            nav_buttons = []
            if has_prev:
                nav_buttons.append(types.InlineKeyboardButton("⬅️ Prev", callback_data=f"page_{page-1}_{p_type}_{location}"))
            if has_next:
                nav_buttons.append(types.InlineKeyboardButton("Next ➡️", callback_data=f"page_{page+1}_{p_type}_{location}"))
            
            if nav_buttons:
                markup.row(*nav_buttons)

            display_type = p_type if p_type != 'all' else 'All'
            loc_title = f" in {location}" if location != "all" else ""
            title = f"Available {display_type} Properties{loc_title}"

            if edit and message.content_type == 'text':
                try:
                    bot.edit_message_text(title, message.chat.id, message.message_id, reply_markup=markup)
                    return
                except Exception:
                    pass
            
            bot.send_message(
                message.chat.id,
                title,
                reply_markup=markup
            )

    @bot.callback_query_handler(
        func=lambda c:
        c.data.startswith("page_")
    )
    def pagination(call):
        bot.answer_callback_query(call.id)
        parts = call.data.split("_")
        page = int(parts[1])
        p_type = parts[2] if len(parts) > 2 else "all"
        location = parts[3] if len(parts) > 3 else "all"
        display_properties(call.message, page=page, p_type=p_type, location=location, edit=True)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("imgnav_"))
    def property_image_nav(call):
        # Format: imgnav_{property_id}_{index}
        try:
            parts = call.data.split("_")
            index = int(parts[2])
        except (IndexError, ValueError):
            index = 0
            
        bot.answer_callback_query(call.id) # Remove the loading spinner
        property_details(call, nav_index=index)

    @bot.callback_query_handler(func=lambda call: call.data == "ignore")
    def ignore_callback(call):
        bot.answer_callback_query(call.id)

    def safe_send_media(func, **kwargs):
        """Helper to send media with a fallback for Markdown parsing errors."""
        try:
            # If we are editing media, the 'media' object contains the caption/parse_mode
            if 'media' in kwargs and hasattr(kwargs['media'], 'parse_mode'):
                try:
                    return func(**kwargs)
                except Exception:
                    kwargs['media'].parse_mode = None
                    return func(**kwargs)
            
            return func(**kwargs)
        except Exception as e:
            if "parse_mode" in kwargs:
                kwargs.pop("parse_mode")
                return func(**kwargs)
            raise e

    @bot.callback_query_handler(func=lambda call: call.data.startswith("property_"))
    def property_details_handler(call):
        bot.answer_callback_query(call.id)
        property_details(call)

    def property_details(call, nav_index=0):
        with bot.flask_app.app_context():
            # Extract ID from property_{id} or imgnav_{id}_{idx}
            parts = call.data.split("_")
            property_id = int(parts[1])
            
            # Fetch property directly from database
            prop = db.session.get(Property, property_id)

            if not prop:
                bot.answer_callback_query(call.id, "Property not found.")
                return

            # Fetch images directly, prioritizing the thumbnail
            query = db.session.query(PropertyImage).filter_by(property_id=property_id)
            
            # Check if is_thumbnail exists to prevent AttributeError during migration
            if hasattr(PropertyImage, 'is_thumbnail'):
                images = query.order_by(PropertyImage.is_thumbnail.desc()).all()
            else:
                images = query.all()
                print("⚠️ Warning: is_thumbnail column is missing from PropertyImage model.")

            image_urls = [img.image_url for img in images]

            # Fallback to placeholder if no images found in database
            if not image_urls:
                image_urls = [PLACEHOLDER_IMAGE]

            # Handle potential None values for new properties
            beds = prop.bedrooms if prop.bedrooms else "N/A"
            baths = prop.bathrooms if prop.bathrooms else "N/A"
            size = prop.size if prop.size else "N/A"
            
            try:
                price = f"{float(prop.price):,.2f}" if prop.price else "Contact for Price"
            except (ValueError, TypeError):
                price = "Contact for Price"

            text = f"""
🏠 *{prop.title}*


📍 *Location:* {prop.location}
 
💰 *Price:* ${price}

🛏 *Bedrooms:* {beds}

🛁 *Bathrooms:* {baths}

📏 *Size:* {size}

📄 *Description:* 
{prop.description}
"""

            # Check if property is already in favorites
            user = db.session.query(User).filter_by(telegram_id=call.from_user.id).first()
            is_fav = False
            if user:
                is_fav = db.session.query(Favorite).filter_by(user_id=user.id, property_id=property_id).first() is not None
            
            save_btn_text = "⭐ Unsave" if is_fav else "⭐ Save"
            save_btn_callback = f"unsave_{prop.id}" if is_fav else f"save_{prop.id}"

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton(save_btn_text, callback_data=save_btn_callback),
                types.InlineKeyboardButton("📞 Contact Agent", callback_data=f"contact_{prop.id}")
            )

            if hasattr(prop, 'latitude') and prop.latitude and prop.longitude:
                markup.add(
                    types.InlineKeyboardButton(
                        "📍 View Map",
                        url=f"https://maps.google.com/?q={prop.latitude},{prop.longitude}"
                    )
                )
            
            # Add Image Navigation Row if multiple images exist
            if len(image_urls) > 1:
                prev_idx = (nav_index - 1) % len(image_urls)
                next_idx = (nav_index + 1) % len(image_urls)
                markup.row(
                    types.InlineKeyboardButton("⬅️ Prev", callback_data=f"imgnav_{property_id}_{prev_idx}"),
                    types.InlineKeyboardButton(f"🖼 {nav_index + 1} / {len(image_urls)}", callback_data="ignore"),
                    types.InlineKeyboardButton("Next ➡️", callback_data=f"imgnav_{property_id}_{next_idx}")
                )
            
            # Calculate back button location group
            loc_group = "all"
            if prop.province:
                loc_group = "Phnom Penh" if prop.province == "Phnom Penh" else "Provinces"

            markup.add(
                types.InlineKeyboardButton(
                    "🔙 Back to List",
                    callback_data=f"page_1_{prop.property_type if prop.property_type else 'all'}_{loc_group}"
                )
            )

            # Determine if the text exceeds Telegram's 1024-character caption limit
            is_truncated = len(text) > 1024
            caption_text = text[:1021] + "..." if is_truncated else text

            # Image selection based on navigation index
            target_url = image_urls[nav_index] if nav_index < len(image_urls) else image_urls[0]
            
            try:
                if call.data.startswith("imgnav_") and call.message.content_type == 'photo':
                    # Only edit if the existing message is actually a photo
                    safe_send_media(
                        bot.edit_message_media,
                        chat_id=call.message.chat.id,
                        media=InputMediaPhoto(target_url, caption=caption_text, parse_mode="Markdown"),
                        message_id=call.message.message_id,
                        reply_markup=markup
                    )
                else:
                    # Send a fresh photo message for initial view or if previous was text
                    safe_send_media(
                        bot.send_photo,
                        chat_id=call.message.chat.id,
                        photo=target_url,
                        caption=caption_text,
                        parse_mode="Markdown",
                        reply_markup=markup
                    )
            except Exception as e:
                print(f"Display Error: {e}")
                bot.send_message(
                    call.message.chat.id,
                    f"{text}\n\n⚠️ _Note: Image failed to load._",
                    parse_mode="Markdown",
                    reply_markup=markup
                )

            # Send full description if truncated (only on initial load)
            if is_truncated and not call.data.startswith("imgnav_"):
                bot.send_message(
                    call.message.chat.id,
                    "📑 *Full Property Description:*\n\n" + text,
                    parse_mode="Markdown"
                )
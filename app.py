import time
from flask import Flask
import telebot
from telebot import apihelper



# Enable middleware support before initializing the bot
apihelper.ENABLE_MIDDLEWARE = True
# Increase global session timeout to handle slow connections
apihelper.SESSION_TIME_OUT = 30

from config import BOT_TOKEN
from config import DATABASE_URL

from database.db import db
from src.handlers.property import register as property_register

from src.handlers.start import register as start_register

from src.handlers.search import register as search_register

from src.handlers.favorites import register as favorite_register


from src.handlers.contact import register as contact_register

from src.handlers.language import register as language_register

from src.handlers.about import register as about_register

app = Flask(__name__)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = DATABASE_URL or "sqlite:///realestate.db"

db.init_app(app)

bot = telebot.TeleBot(BOT_TOKEN)
# Attach app to bot to make context accessible in all handlers
bot.flask_app = app

# Ensure all handlers are registered
property_register(bot)
search_register(bot)
favorite_register(bot)
contact_register(bot)
language_register(bot)
about_register(bot)
start_register(bot)

if __name__ == "__main__":
    # 1. Initialize DB tables inside a temporary context
    with app.app_context():
        db.create_all()
        
        # Simple migration to add missing columns to existing tables
        try:
            from sqlalchemy import text
            # Add province to properties table
            db.session.execute(text("ALTER TABLE properties ADD COLUMN IF NOT EXISTS province VARCHAR(100)"))
            # Add is_thumbnail to property_images table
            db.session.execute(text("ALTER TABLE property_images ADD COLUMN IF NOT EXISTS is_thumbnail BOOLEAN DEFAULT FALSE"))
            db.session.commit()
            print("Database migration completed successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Migration notice (normal if columns exist): {e}")
    # # render.com
    # keep_alive() # បើក Web server 
    # bot.polling() # ឬ bot.run() ទៅតាមប្រភេទកូដរបស់អ្នក
    # print("Starting Real Estate Bot...")

    try:
        # 2. Clean up any existing connection with retries
        connected = False
        for i in range(3):
            try:
                bot.remove_webhook()
                connected = True
                break
            except Exception as e:
                print(f"Connection attempt {i+1} failed: {e}. Retrying...")
                time.sleep(5)
        
        if not connected:
            raise Exception("Could not connect to Telegram servers after multiple attempts.")
        
        print("Bot is now polling. Press Ctrl+C to stop.")
        bot.infinity_polling(skip_pending=True, timeout=90, long_polling_timeout=30)
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        print("If you see 'Conflict: terminated by other getUpdates', please check Task Manager/Activity Monitor and kill any existing Python processes.")
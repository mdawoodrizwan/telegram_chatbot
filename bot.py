import telegram.ext
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the token from the environment variable
TOKEN = os.getenv("TOKEN")

# Create the Application
application = Application.builder().token(TOKEN).build()

# Print a message when the bot starts
print("Bot is starting...")

# Define async functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! Welcome to Dogar_bot!....")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("""
    The following commands are available:
    
    /start -> Welcome to the bot
    /help -> This message
    /content -> Simplilearn offers various courses free of charge through Skillup by Simplilearn
    /Python -> The first video from the Python Playlist
    /SQL -> The first video from the SQL Playlist
    /Java -> The first video from the Java Playlist
    /contact -> Contact information 
    """)

async def content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("We have various playlists and articles available!")

async def python(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Tutorial link: https://youtu.be/Tm5u97I7OrM")

async def sql(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Tutorial link: https://youtu.be/pFq1pgli0OQ")

async def java(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Tutorial link: https://youtu.be/i6AZdFxTK9I")

async def skillup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Tutorial link: https://www.simplilearn.com/?&utm_source=google&utm_medium=cpc&utm_term=%2Bwww%20%2Bsimplilearn%20%2Bcom&utm_content=803350713-40537012023-467574577661&utm_device=c&utm_campaign=Search-Brand-Broad-IN-AllDevice-adgroup-brand-navigation&gclid=Cj0KCQjw0oyYBhDGARIsAMZEuMv5mA9EysZZ5NfhK65Cb5OU0Q0TVC4con6DQzHF502-dfgA7QQFCgQaAu5sEALw_wcB")

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("You can contact us at the official email id.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"You said: {update.message.text}, use the commands using /")

# Add handlers to the application
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('help', help_command))
application.add_handler(CommandHandler('content', content))
application.add_handler(CommandHandler('Python', python))
application.add_handler(CommandHandler('SQL', sql))
application.add_handler(CommandHandler('Java', java))
application.add_handler(CommandHandler('Skillup', skillup))
application.add_handler(CommandHandler('contact', contact))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Print message when bot starts
print("Bot has started successfully. Now polling...")

# Start polling
application.run_polling(timeout=10)

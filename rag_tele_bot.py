import os
import soundfile as sf
from transformers import pipeline
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
from rag_without_LLM import rag_chain  # Import your RAG-related logic

# Load environment variables from .env file (Telegram bot token)
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Initialize the Telegram bot application
application = Application.builder().token(TOKEN).build()

# Initialize Whisper model for speech-to-text
whisper_model = pipeline("automatic-speech-recognition", model="openai/whisper-small", device='cpu')

# Function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! Welcome to Dogar_bot!")

# Function to handle the /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("""
    The following commands are available:
    
    /start -> Welcome to the Dogar bot!
    /help -> This message
    /Python -> The first video from the Python Playlist
    /SQL -> The first video from the SQL Playlist
    /Java -> The first video from the Java Playlist
                                    
    """)


async def python(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Tutorial link: https://youtu.be/Tm5u97I7OrM")

async def sql(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Tutorial link: https://youtu.be/pFq1pgli0OQ")

async def java(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Tutorial link: https://youtu.be/i6AZdFxTK9I")



# Function to handle voice messages and transcribe them using Whisper
async def audio_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Download the voice message from Telegram
    audio_file = await update.message.voice.get_file()
    file_path = await audio_file.download_to_drive("query.ogg")  # Save the file as .ogg
    
    # Load the saved audio file into a numpy array for Whisper
    audio, sample_rate = sf.read(file_path)
    
    # Transcribe the audio to text
    transcription = whisper_model({"array": audio, "sampling_rate": sample_rate})["text"]
    
    # Query the RAG model with the transcription
    result = rag_chain(transcription)
    
    # Format the response
    response_message = (
        f"🎙 **Voice Transcription**:\n"
        f"_{transcription}_\n\n"
        f"🧠 **RAG Response**:\n"
        f"{result}"
    )
    
    # Send both transcription and RAG result to the user
    await update.message.reply_text(response_message, parse_mode='Markdown')

# Function to handle text queries and query the RAG chain
async def text_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.message.text  # Get the user's text message
    result = rag_chain(query)  # Query the RAG model
    
    # Format the response
    response_message = (
        f"💬 **Query**:\n"
        f"_{query}_\n\n"
        f"🧠 **RAG Response**:\n"
        f"{result}"
    )
    
    # Send the formatted result back to the user
    await update.message.reply_text(response_message, parse_mode='Markdown')


# Set up the bot with handlers
def main():
    # Command to handle the /start and /help commands
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('Python', python))
    application.add_handler(CommandHandler('SQL', sql))
    application.add_handler(CommandHandler('Java', java))


    # Command to handle text queries
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_query))

    # Command to handle audio/voice queries
    application.add_handler(MessageHandler(filters.VOICE, audio_query))

    # Start the bot
    print("Telegram bot with RAG and Whisper STT is running...")
    application.run_polling(timeout=10)

if __name__ == "__main__":
    main()

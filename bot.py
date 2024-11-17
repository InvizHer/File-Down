import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, BASE_URL
from database import Database

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to File Download Bot!\n\n"
        "Send me any file (up to 50MB) and I'll generate a download link for you.\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/help - Show help message"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 How to use this bot:\n\n"
        "1. Send any file to the bot\n"
        "2. The bot will process it and generate a download link\n"
        "3. Click the link to download the file\n\n"
        "Supported file types: Any file up to 50MB"
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    
    if not hasattr(message, 'document'):
        await message.reply_text("Please send a file.")
        return

    file = message.document
    
    if file.file_size > MAX_FILE_SIZE:
        await message.reply_text("File is too large. Maximum size is 50MB.")
        return

    # Get file information
    file_info = await db.save_file_info(
        file_id=file.file_id,
        file_name=file.file_name,
        file_size=file.file_size,
        mime_type=file.mime_type,
        user_id=message.from_user.id
    )
    
    # Generate download link
    download_link = f"{BASE_URL}/download/{file.file_id}"
    
    await message.reply_text(
        f"✅ File processed successfully!\n\n"
        f"📁 File name: {file.file_name}\n"
        f"📊 Size: {file.file_size / 1024 / 1024:.2f}MB\n"
        f"🔗 Download link:\n{download_link}"
    )

def run_bot():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    
    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, BASE_URL, MAX_FILE_SIZE
from database import Database
import humanize

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)
db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to File Download Bot!\n\n"
        "Send me any file (up to 2GB) and I'll generate a download link for you.\n\n"
        "Supported features:\n"
        "• Files up to 2GB\n"
        "• All file types supported\n"
        "• Permanent download links\n"
        "• Download tracking\n\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/help - Show help message\n"
        "/stats - Show your upload statistics"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 How to use this bot:\n\n"
        "1. Send any file to the bot (up to 2GB)\n"
        "2. Wait for processing (larger files take longer)\n"
        "3. Receive your download link\n"
        "4. Share the link with anyone\n\n"
        "Supported file types:\n"
        "• Videos (MP4, MKV, AVI, etc.)\n"
        "• Documents (PDF, DOC, etc.)\n"
        "• Archives (ZIP, RAR, etc.)\n"
        "• Images (JPG, PNG, etc.)\n"
        "• Audio files (MP3, WAV, etc.)\n"
        "And many more!"
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    files = await db.collection.find({"user_id": user_id}).to_list(length=None)
    
    total_files = len(files)
    total_size = sum(f.get('file_size', 0) for f in files)
    total_downloads = sum(f.get('download_count', 0) for f in files)
    
    await update.message.reply_text(
        f"📊 Your Statistics:\n\n"
        f"Total files uploaded: {total_files}\n"
        f"Total storage used: {humanize.naturalsize(total_size)}\n"
        f"Total downloads: {total_downloads}"
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    
    # Handle both documents and videos
    file = message.document or message.video
    
    if not file:
        await message.reply_text("Please send a file or video.")
        return

    if file.file_size > MAX_FILE_SIZE:
        await message.reply_text("File is too large. Maximum size is 2GB.")
        return

    try:
        # Send "processing" message
        status_message = await message.reply_text("📂 Processing your file...")

        # Get file information
        file_unique_id = file.file_unique_id
        
        # Save file info to database
        file_info = await db.save_file_info(
            file_id=file.file_id,
            file_unique_id=file_unique_id,
            file_name=getattr(file, 'file_name', 'video.mp4'),
            file_size=file.file_size,
            mime_type=getattr(file, 'mime_type', 'video/mp4'),
            user_id=message.from_user.id
        )
        
        # Generate download link
        download_link = f"{BASE_URL}/download/{file.file_id}"
        
        # Update status message with success
        await status_message.edit_text(
            f"✅ File processed successfully!\n\n"
            f"📁 File name: {getattr(file, 'file_name', 'video.mp4')}\n"
            f"📊 Size: {humanize.naturalsize(file.file_size)}\n"
            f"🔗 Download link:\n{download_link}"
        )

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        await status_message.edit_text(
            "❌ Sorry, there was an error processing your file. Please try again."
        )

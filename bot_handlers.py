import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_USER_ID, MAX_FILE_SIZE
from database import Database
from keyboards import get_file_keyboard, get_admin_keyboard
from utils import format_file_info, humanize

logger = logging.getLogger(__name__)
db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Enhanced File Download Bot!\n\n"
        "Send me any file (up to 2GB) and I'll process it for you.\n\n"
        "Features:\n"
        "• Secure file handling\n"
        "• Download confirmation\n"
        "• File statistics\n"
        "• Download tracking\n"
        "• Progress updates\n\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/help - Show help message\n"
        "/stats - Show your statistics\n"
        "/admin - Admin panel (admin only)"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 How to use this bot:\n\n"
        "1. Send any file\n"
        "2. Confirm the download\n"
        "3. Wait for processing\n"
        "4. Get your download link\n\n"
        "Tips:\n"
        "• Use /stats to see your usage\n"
        "• Check file details before downloading\n"
        "• Contact admin for support"
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats = await db.get_user_stats(user_id)
    
    await update.message.reply_text(
        f"📊 Your Statistics:\n\n"
        f"Files uploaded: {stats['total_files']}\n"
        f"Storage used: {humanize.naturalsize(stats['total_size'])}\n"
        f"Total downloads: {stats['total_downloads']}"
    )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("⚠️ This command is for administrators only.")
        return
    
    await update.message.reply_text(
        "🔧 Admin Panel",
        reply_markup=get_admin_keyboard()
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    file = message.document or message.video or message.audio or message.voice
    
    if not file:
        await message.reply_text("Please send a file.")
        return

    if file.file_size > MAX_FILE_SIZE:
        await message.reply_text("⚠️ File is too large. Maximum size is 2GB.")
        return

    try:
        file_id = await db.save_file_info(
            file_id=file.file_id,
            file_unique_id=file.file_unique_id,
            file_name=getattr(file, 'file_name', 'unnamed_file'),
            file_size=file.file_size,
            mime_type=getattr(file, 'mime_type', 'application/octet-stream'),
            user_id=message.from_user.id,
            username=message.from_user.username or "unknown"
        )
        
        await message.reply_text(
            f"📁 File received!\n\n"
            f"Name: {getattr(file, 'file_name', 'unnamed_file')}\n"
            f"Size: {humanize.naturalsize(file.file_size)}\n\n"
            f"Please confirm to start processing:",
            reply_markup=get_file_keyboard(file.file_id)
        )

    except Exception as e:
        logger.error(f"Error handling file: {str(e)}")
        await message.reply_text("❌ Error processing your file. Please try again.")

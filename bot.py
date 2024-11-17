import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)
from config import TELEGRAM_BOT_TOKEN, BASE_URL, MAX_FILE_SIZE, ADMIN_USER_ID
from database import Database
from keyboards import get_file_keyboard, get_admin_keyboard
from utils import format_file_info
import humanize
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
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
        # Save file info
        file_id = await db.save_file_info(
            file_id=file.file_id,
            file_unique_id=file.file_unique_id,
            file_name=getattr(file, 'file_name', 'unnamed_file'),
            file_size=file.file_size,
            mime_type=getattr(file, 'mime_type', 'application/octet-stream'),
            user_id=message.from_user.id,
            username=message.from_user.username or "unknown"
        )
        
        # Send confirmation message with keyboard
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

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("download_"):
        file_id = data.replace("download_", "")
        file_info = await db.get_file_by_id(file_id)
        
        if not file_info:
            await query.message.edit_text("❌ File not found.")
            return
        
        await db.update_file_status(file_id, "downloading")
        download_link = f"{BASE_URL}/download/{file_id}"
        
        await query.message.edit_text(
            f"✅ Download confirmed!\n\n"
            f"📁 {file_info['file_name']}\n"
            f"📊 {humanize.naturalsize(file_info['file_size'])}\n\n"
            f"🔗 Download link:\n{download_link}",
            reply_markup=None
        )
    
    elif data.startswith("cancel_"):
        file_id = data.replace("cancel_", "")
        await db.update_file_status(file_id, "cancelled")
        await query.message.edit_text("❌ Download cancelled.")
    
    elif data.startswith("stats_"):
        file_id = data.replace("stats_", "")
        file_info = await db.get_file_by_id(file_id)
        
        if file_info:
            await query.message.edit_text(
                format_file_info(file_info),
                reply_markup=get_file_keyboard(file_id)
            )
    
    elif data == "admin_stats":
        if query.from_user.id != ADMIN_USER_ID:
            return
        
        # Get system stats from database
        total_files = await db.collection.count_documents({})
        total_size = await db.collection.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$file_size"}}}
        ]).to_list(length=1)
        
        await query.message.edit_text(
            f"📊 System Statistics\n\n"
            f"Total files: {total_files}\n"
            f"Total storage: {humanize.naturalsize(total_size[0]['total'] if total_size else 0)}\n"
            f"Active users: {await db.collection.distinct('user_id').__len__()}",
            reply_markup=get_admin_keyboard()
        )

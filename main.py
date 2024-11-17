import uvicorn
from fastapi import FastAPI
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters
)
import asyncio
from config import TELEGRAM_BOT_TOKEN
from api import app
from bot import (
    start, help_command, stats_command, admin_command,
    handle_file, button_callback
)

async def run_bot():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_file))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    await application.initialize()
    await application.start()
    await application.run_polling()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_bot())

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()

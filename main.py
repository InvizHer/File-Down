import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Response, BackgroundTasks
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters
)
import uvicorn
from config import TELEGRAM_BOT_TOKEN
from bot_handlers import (
    start, help_command, stats_command, admin_command,
    handle_file
)
from button_handlers import button_callback
from download_handlers import download_file

# Global variable for the bot application
bot_app = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize bot on startup
    global bot_app
    bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(CommandHandler("stats", stats_command))
    bot_app.add_handler(CommandHandler("admin", admin_command))
    bot_app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_file))
    bot_app.add_handler(CallbackQueryHandler(button_callback))
    
    # Start bot
    await bot_app.initialize()
    await bot_app.start()
    
    # Start polling in background
    asyncio.create_task(bot_app.run_polling(allowed_updates=Update.ALL_TYPES))
    
    yield
    
    # Cleanup on shutdown
    await bot_app.stop()
    await bot_app.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"status": "active", "message": "Enhanced File Download Bot API"}

@app.get("/download/{file_id}")
async def handle_download(file_id: str, background_tasks: BackgroundTasks):
    return await download_file(file_id, background_tasks, bot_app)

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()

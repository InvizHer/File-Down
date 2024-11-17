import uvicorn
from fastapi import FastAPI
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters
)
import asyncio
from contextlib import asynccontextmanager
from config import TELEGRAM_BOT_TOKEN
from api import app
from bot import (
    start, help_command, stats_command, admin_command,
    handle_file, button_callback
)

# Global variable for the bot application
bot_app = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global bot_app
    bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(CommandHandler("stats", stats_command))
    bot_app.add_handler(CommandHandler("admin", admin_command))
    bot_app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_file))
    bot_app.add_handler(CallbackQueryHandler(button_callback))
    
    await bot_app.initialize()
    await bot_app.start()
    
    # Start polling in a separate task
    asyncio.create_task(bot_app.run_polling(allowed_updates=Update.ALL_TYPES))
    
    yield
    
    # Shutdown
    await bot_app.stop()
    await bot_app.shutdown()

# Update FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Add your API routes here (copy from api.py)
@app.get("/")
async def read_root():
    return {"status": "active", "message": "Enhanced File Download Bot API"}

# Add other routes from api.py

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()

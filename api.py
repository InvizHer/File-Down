from fastapi import FastAPI, HTTPException
from telegram.ext import Application
from config import TELEGRAM_BOT_TOKEN, BASE_URL
import aiohttp
from database import Database

app = FastAPI()
db = Database()

@app.get("/")
async def read_root():
    return {"message": "File Download Bot API is running"}

@app.get("/download/{file_id}")
async def download_file(file_id: str):
    # Get file info from database
    file_info = await db.get_file_by_id(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")

    # Get file path from Telegram
    bot = Application.builder().token(TELEGRAM_BOT_TOKEN).build().bot
    try:
        file = await bot.get_file(file_id)
        file_url = file.file_path
        
        # Increment download count
        await db.increment_download_count(file_id)
        
        # Return file download information
        return {
            "file_name": file_info["file_name"],
            "file_size": file_info["file_size"],
            "mime_type": file_info["mime_type"],
            "download_url": file_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# main.py
import uvicorn
from api import app
from bot import run_bot
import asyncio
import threading

def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

def main():
    # Run API in a separate thread
    api_thread = threading.Thread(target=run_api)
    api_thread.start()
    
    # Run bot in main thread
    run_bot()

if __name__ == "__main__":
    main()

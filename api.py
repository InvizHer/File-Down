from fastapi import FastAPI, HTTPException, Response
from telegram.ext import Application
from config import TELEGRAM_BOT_TOKEN
import aiohttp
from database import Database

app = FastAPI()
db = Database()

@app.get("/")
async def read_root():
    return {"status": "active", "message": "File Download Bot API is running"}

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
        headers = {
            "Content-Disposition": f"attachment; filename={file_info['file_name']}",
            "Content-Type": file_info['mime_type']
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                content = await response.read()
                return Response(
                    content=content,
                    headers=headers,
                    media_type=file_info['mime_type']
                )

    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download file")

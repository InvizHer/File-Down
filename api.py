from fastapi import FastAPI, HTTPException, Response, BackgroundTasks
from telegram.ext import Application
from config import TELEGRAM_BOT_TOKEN
import aiohttp
from database import Database
import logging

logger = logging.getLogger(__name__)
app = FastAPI()
db = Database()

@app.get("/")
async def read_root():
    return {"status": "active", "message": "Enhanced File Download Bot API"}

@app.get("/download/{file_id}")
async def download_file(file_id: str, background_tasks: BackgroundTasks):
    file_info = await db.get_file_by_id(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    if file_info['status'] != "downloading":
        raise HTTPException(status_code=400, detail="File not confirmed for download")
    
    bot = Application.builder().token(TELEGRAM_BOT_TOKEN).build().bot
    try:
        file = await bot.get_file(file_id)
        file_url = file.file_path
        
        background_tasks.add_task(db.increment_download_count, file_id)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                content = await response.read()
                return Response(
                    content=content,
                    headers={
                        "Content-Disposition": f"attachment; filename={file_info['file_name']}",
                        "Content-Type": file_info['mime_type']
                    },
                    media_type=file_info['mime_type']
                )

    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        await db.update_file_status(file_id, "failed")
        raise HTTPException(status_code=500, detail="Download failed")

from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("5457862323:AAFVMwvqyeVjMoYCLmzvfjzu2pGXSXvjRwA")
MONGODB_URI = os.getenv("mongodb+srv://codexun:TeamCodexun07@codexun.egmx5.mongodb.net/?retryWrites=true&w=majority")
DATABASE_NAME = "file_storage_bot"
COLLECTION_NAME = "files"
BASE_URL = os.getenv("BASE_URL", "https://inz-file-down.onrender.com")  # Update this with your Render URL
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max file size

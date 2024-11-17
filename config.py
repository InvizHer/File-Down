from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = "file_storage_bot"
COLLECTION_NAME = "files"
BASE_URL = os.getenv("BASE_URL", "https://your-app-name.onrender.com")
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB in bytes

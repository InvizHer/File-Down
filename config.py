from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = "5457862323:AAFVMwvqyeVjMoYCLmzvfjzu2pGXSXvjRwA"
MONGODB_URI = "mongodb+srv://codexun:TeamCodexun07@codexun.egmx5.mongodb.net/?retryWrites=true&w=majority"
DATABASE_NAME = "enhanced_file_bot"
COLLECTION_NAME = "files"
BASE_URL = os.getenv("BASE_URL", "https://inz-file-down.onrender.com")  # Update this after deployment
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
ADMIN_USER_ID = 2056407064

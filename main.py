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

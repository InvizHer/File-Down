from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_file_keyboard(file_id: str):
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm Download", callback_data=f"download_{file_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{file_id}")
        ],
        [
            InlineKeyboardButton("📊 File Stats", callback_data=f"stats_{file_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📊 System Stats", callback_data="admin_stats"),
            InlineKeyboardButton("🔄 Clear Cache", callback_data="admin_clear_cache")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

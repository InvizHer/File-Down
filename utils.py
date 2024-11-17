import humanize
from typing import Dict, Any
import magic
import os

def format_file_info(file_info: Dict[str, Any]) -> str:
    return (
        f"📁 File Information:\n\n"
        f"Name: {file_info['file_name']}\n"
        f"Size: {humanize.naturalsize(file_info['file_size'])}\n"
        f"Type: {file_info['mime_type']}\n"
        f"Downloads: {file_info['download_count']}\n"
        f"Status: {file_info['status'].title()}"
    )

def get_mime_type(file_path: str) -> str:
    mime = magic.Magic(mime=True)
    return mime.from_file(file_path)

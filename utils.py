import os
import magic
from typing import Optional

def get_mime_type(file_path: str) -> str:
    mime = magic.Magic(mime=True)
    return mime.from_file(file_path)

def get_file_extension(mime_type: str) -> Optional[str]:
    mime_to_ext = {
        'video/mp4': '.mp4',
        'video/x-matroska': '.mkv',
        'video/quicktime': '.mov',
        'video/x-msvideo': '.avi',
        'video/x-ms-wmv': '.wmv',
        'application/pdf': '.pdf',
        'application/zip': '.zip',
        'application/x-rar-compressed': '.rar',
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'audio/mpeg': '.mp3',
        'audio/x-wav': '.wav',
    }
    return mime_to_ext.get(mime_type, '')

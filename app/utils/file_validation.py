import os
from typing import Tuple
from fastapi import UploadFile

from app.core.config import settings
from app.exceptions.custom_exceptions import (
    InvalidFileFormatException,
    FileTooLargeException,
    FileCorruptedException
)
from app.core.logging import logger


def validate_file_metadata(filename: str, content_length: int = 0) -> str:
    """
    Validates file extension and declared content length.
    Returns normalized file_type: 'kml' or 'shapefile_zip'.
    """
    if not filename:
        raise InvalidFileFormatException("Uploaded file must have a valid filename.")

    ext = os.path.splitext(filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise InvalidFileFormatException(
            f"Unsupported file extension '{ext}'. Only {settings.ALLOWED_EXTENSIONS} are allowed."
        )

    if content_length > settings.MAX_FILE_SIZE_BYTES:
        raise FileTooLargeException(
            f"File size {content_length} bytes exceeds maximum limit of {settings.MAX_FILE_SIZE_BYTES} bytes."
        )

    return "kml" if ext == ".kml" else "shapefile_zip"


async def read_and_validate_file_content(file: UploadFile) -> Tuple[bytes, str]:
    """
    Reads the full content of an UploadFile into memory (safely within size limits),
    performs size and empty file checks, and verifies magic bytes/header signatures.
    """
    filename = file.filename or "unknown"
    file_type = validate_file_metadata(filename)

    # Read content chunk by chunk to prevent memory exhaustion
    contents = bytearray()
    chunk_size = 1024 * 1024  # 1MB chunks
    
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        contents.extend(chunk)
        if len(contents) > settings.MAX_FILE_SIZE_BYTES:
            raise FileTooLargeException(
                f"File '{filename}' exceeds maximum allowed size of {settings.MAX_FILE_SIZE_BYTES // (1024*1024)} MB."
            )

    raw_bytes = bytes(contents)

    if len(raw_bytes) == 0:
        raise FileCorruptedException(f"File '{filename}' is empty (0 bytes).")

    # Header signature verification
    if file_type == "shapefile_zip":
        if not raw_bytes.startswith(b"PK\x03\x04"):
            raise FileCorruptedException("Uploaded .zip file has invalid magic header signature.")
    elif file_type == "kml":
        header_sample = raw_bytes[:512].decode(errors="ignore").lower()
        if "<kml" not in header_sample and "<?xml" not in header_sample and "<gpx" not in header_sample:
            logger.warning(f"File '{filename}' has non-standard KML header sample: {header_sample[:100]}")

    return raw_bytes, file_type

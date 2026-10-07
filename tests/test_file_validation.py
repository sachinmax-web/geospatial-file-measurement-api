import asyncio
import pytest
from fastapi import UploadFile
from io import BytesIO

from app.utils.file_validation import validate_file_metadata, read_and_validate_file_content
from app.exceptions.custom_exceptions import (
    InvalidFileFormatException,
    FileTooLargeException,
    FileCorruptedException
)


def test_validate_file_metadata_valid():
    assert validate_file_metadata("test.kml") == "kml"
    assert validate_file_metadata("archive.ZIP") == "shapefile_zip"


def test_validate_file_metadata_invalid_extension():
    with pytest.raises(InvalidFileFormatException):
        validate_file_metadata("document.pdf")

    with pytest.raises(InvalidFileFormatException):
        validate_file_metadata("data.geojson")


def test_validate_file_metadata_too_large():
    with pytest.raises(FileTooLargeException):
        validate_file_metadata("test.kml", content_length=100 * 1024 * 1024)


def test_read_and_validate_empty_file():
    empty_upload = UploadFile(filename="empty.kml", file=BytesIO(b""))
    with pytest.raises(FileCorruptedException):
        asyncio.run(read_and_validate_file_content(empty_upload))


def test_read_and_validate_corrupted_zip():
    bad_zip_upload = UploadFile(filename="fake.zip", file=BytesIO(b"NOT_A_ZIP_HEADER"))
    with pytest.raises(FileCorruptedException):
        asyncio.run(read_and_validate_file_content(bad_zip_upload))

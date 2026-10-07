import os
import zipfile
from typing import List, Tuple
from app.exceptions.custom_exceptions import (
    ZipSecurityException,
    MissingShapefileComponentException,
    FileCorruptedException
)
from app.core.logging import logger

REQUIRED_SHAPEFILE_EXTENSIONS = {".shp", ".shx", ".dbf", ".prj"}
ALLOWED_GEOSPATIAL_EXTENSIONS = {".shp", ".shx", ".dbf", ".prj", ".cpg", ".qpj", ".sbn", ".sbx"}


def is_safe_zip_path(target_dir: str, member_name: str) -> bool:
    """
    Prevents Zip Slip path traversal vulnerabilities by verifying that the resolved destination
    path resides strictly within the intended target directory.
    """
    if os.path.isabs(member_name) or ".." in member_name.replace("/", "\\").split("\\"):
        return False
    
    target_dir_abs = os.path.abspath(target_dir)
    destination_abs = os.path.abspath(os.path.join(target_dir_abs, member_name))
    
    return destination_abs.startswith(target_dir_abs + os.sep) or destination_abs == target_dir_abs


def validate_and_extract_shapefile_zip(zip_path: str, extract_to_dir: str) -> str:
    """
    Validates a ZIP archive for Zip Slip vulnerabilities, verifies required Shapefile components
    (.shp, .shx, .dbf, .prj), and extracts valid components safely to target directory.
    
    Returns the absolute path to the extracted .shp file.
    """
    if not zipfile.is_zipfile(zip_path):
        raise FileCorruptedException("File is not a valid zip archive.")

    with zipfile.ZipFile(zip_path, 'r') as zf:
        namelist = zf.namelist()
        
        # 1. Zip Slip / Path Traversal Validation
        for name in namelist:
            if not is_safe_zip_path(extract_to_dir, name):
                logger.error(f"Zip Slip attack detected in member: '{name}'")
                raise ZipSecurityException(f"Zip Slip path traversal attempt detected in path: '{name}'")

        # Filter out directory entries
        file_members = [name for name in namelist if not name.endswith('/') and not name.endswith('\\')]
        
        if not file_members:
            raise FileCorruptedException("Zip archive is empty or contains only directories.")

        # Find shapefiles in zip
        shp_members = [name for name in file_members if name.lower().endswith('.shp')]
        
        if not shp_members:
            raise MissingShapefileComponentException("No .shp file found in ZIP archive.")
        
        # Select the primary shapefile (first .shp found, or in root)
        main_shp = shp_members[0]
        base_name = os.path.splitext(main_shp)[0]

        # Check required companion files (.shp, .shx, .dbf, .prj)
        found_extensions = set()
        for member in file_members:
            member_base, member_ext = os.path.splitext(member)
            if member_base.lower() == base_name.lower():
                found_extensions.add(member_ext.lower())

        missing_required = REQUIRED_SHAPEFILE_EXTENSIONS - found_extensions
        if missing_required:
            missing_str = ", ".join(sorted(missing_required))
            logger.error(f"Shapefile '{main_shp}' is missing required companion files: {missing_str}")
            raise MissingShapefileComponentException(
                f"Shapefile inside ZIP is missing required component files: {missing_str}"
            )

        # Safely extract matching shapefile files only
        extracted_shp_path = ""
        for member in zf.infolist():
            member_ext = os.path.splitext(member.filename)[1].lower()
            if member_ext in ALLOWED_GEOSPATIAL_EXTENSIONS:
                zf.extract(member, extract_to_dir)
                if member.filename == main_shp:
                    extracted_shp_path = os.path.abspath(os.path.join(extract_to_dir, member.filename))

        if not extracted_shp_path or not os.path.exists(extracted_shp_path):
            raise FileCorruptedException("Failed to extract .shp file from archive.")

        return extracted_shp_path

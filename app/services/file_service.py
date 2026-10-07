import os
import shutil
import uuid
from typing import Tuple, List, Dict, Any
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.file_repository import FileRepository
from app.utils.file_validation import read_and_validate_file_content
from app.services.geospatial_service import GeospatialService
from app.db.models import FileModel, MeasurementModel
from app.core.logging import logger


class FileService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = FileRepository(db)

    async def upload_and_process_file(self, upload_file: UploadFile) -> Tuple[FileModel, List[Dict[str, Any]]]:
        """
        Receives an uploaded file, validates content, saves to disk,
        creates DB record, processes geospatial measurements, and updates DB status.
        """
        filename = upload_file.filename or "unknown.file"
        
        # Validate content and read bytes safely
        file_bytes, file_type = await read_and_validate_file_content(upload_file)
        
        # Ensure upload directory exists
        os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
        
        # Save file to storage with UUID prefix
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        storage_path = os.path.join(settings.UPLOAD_DIRECTORY, unique_filename)
        
        with open(storage_path, "wb") as f:
            f.write(file_bytes)

        # Create DB record with PROCESSING status
        file_record = self.repo.create_file(
            filename=filename,
            file_type=file_type,
            file_size=len(file_bytes),
            storage_path=storage_path,
            status="PROCESSING"
        )

        try:
            logger.info(f"Started geospatial processing for file ID '{file_record.id}' ({filename})")
            
            detected_crs, feature_count, measurements = GeospatialService.process_geospatial_file(
                file_path=storage_path,
                file_type=file_type
            )

            # Persist feature measurements to database
            self.repo.save_measurements(file_record.id, measurements)

            # Update file status to COMPLETED
            updated_record = self.repo.update_file_status(
                file_id=file_record.id,
                status="COMPLETED",
                feature_count=feature_count,
                crs=detected_crs
            )

            logger.info(f"Successfully completed processing file ID '{file_record.id}'. Features: {feature_count}, CRS: {detected_crs}")
            return updated_record, measurements

        except Exception as e:
            logger.error(f"Processing failed for file ID '{file_record.id}': {e}", exc_info=True)
            self.repo.update_file_status(
                file_id=file_record.id,
                status="FAILED",
                error_message=str(e)
            )
            raise

    def get_file_summary(self, file_id: str) -> FileModel:
        return self.repo.get_file_by_id(file_id)

    def get_file_measurements(self, file_id: str) -> Tuple[FileModel, List[MeasurementModel]]:
        file_record = self.repo.get_file_by_id(file_id)
        measurements = self.repo.get_measurements_by_file_id(file_id)
        return file_record, measurements

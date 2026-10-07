from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.models import FileModel, MeasurementModel
from app.exceptions.custom_exceptions import ResourceNotFoundException


class FileRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_file(
        self,
        filename: str,
        file_type: str,
        file_size: int,
        storage_path: str,
        crs: Optional[str] = None,
        status: str = "PROCESSING"
    ) -> FileModel:
        file_record = FileModel(
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            storage_path=storage_path,
            crs=crs,
            status=status
        )
        self.db.add(file_record)
        self.db.commit()
        self.db.refresh(file_record)
        return file_record

    def get_file_by_id(self, file_id: str) -> FileModel:
        file_record = self.db.query(FileModel).filter(FileModel.id == file_id).first()
        if not file_record:
            raise ResourceNotFoundException(f"File with ID '{file_id}' not found.")
        return file_record

    def update_file_status(
        self,
        file_id: str,
        status: str,
        feature_count: Optional[int] = None,
        crs: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> FileModel:
        file_record = self.get_file_by_id(file_id)
        file_record.status = status
        if feature_count is not None:
            file_record.feature_count = feature_count
        if crs is not None:
            file_record.crs = crs
        if error_message is not None:
            file_record.error_message = error_message
        
        self.db.commit()
        self.db.refresh(file_record)
        return file_record

    def save_measurements(
        self,
        file_id: str,
        measurements_data: List[dict]
    ) -> List[MeasurementModel]:
        measurement_objects = []
        for data in measurements_data:
            obj = MeasurementModel(
                file_id=file_id,
                feature_index=data.get("feature_id", data.get("feature_index", 0)),
                geometry_type=data.get("geometry_type", "Unknown"),
                original_crs=data.get("original_crs"),
                projected_crs=data.get("projected_crs"),
                measurement_type=data.get("measurement_type"),
                measurement_value=data.get("measurement_value"),
                properties=data.get("properties", {}),
                status=data.get("status", "VALID"),
                message=data.get("message")
            )
            measurement_objects.append(obj)
        
        self.db.bulk_save_objects(measurement_objects)
        self.db.commit()
        return measurement_objects

    def get_measurements_by_file_id(self, file_id: str) -> List[MeasurementModel]:
        # Ensure file exists
        self.get_file_by_id(file_id)
        return (
            self.db.query(MeasurementModel)
            .filter(MeasurementModel.file_id == file_id)
            .order_by(MeasurementModel.feature_index)
            .all()
        )

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class FileModel(Base):
    __tablename__ = "files"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String(512), nullable=False)
    crs = Column(String(100), nullable=True)
    feature_count = Column(Integer, default=0, nullable=False)
    status = Column(String(50), default="PROCESSING", nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    measurements = relationship(
        "MeasurementModel",
        back_populates="file",
        cascade="all, delete-orphan",
        order_by="MeasurementModel.feature_index"
    )


class MeasurementModel(Base):
    __tablename__ = "feature_measurements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String(36), ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True)
    feature_index = Column(Integer, nullable=False)
    geometry_type = Column(String(50), nullable=False)
    original_crs = Column(String(100), nullable=True)
    projected_crs = Column(String(100), nullable=True)
    measurement_type = Column(String(50), nullable=True)  # area_sq_m, length_m, none, unsupported
    measurement_value = Column(Float, nullable=True)
    properties = Column(JSON, nullable=True)
    status = Column(String(50), default="VALID", nullable=False)  # VALID, REPAIRED, INVALID, UNSUPPORTED
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    file = relationship("FileModel", back_populates="measurements")

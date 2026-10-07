from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class FileResponse(BaseModel):
    """
    Schema for file summary response.
    """
    id: str = Field(..., description="Unique UUID of the uploaded file")
    filename: str = Field(..., description="Original filename")
    file_type: Optional[str] = Field(None, description="File type: kml or shapefile_zip")
    feature_count: int = Field(0, description="Number of geospatial features in the file")
    crs: Optional[str] = Field(None, description="Detected Coordinate Reference System")
    status: str = Field(..., description="Processing status: PROCESSING, COMPLETED, FAILED")
    error_message: Optional[str] = Field(None, description="Failure reason if status is FAILED")
    created_at: Optional[datetime] = Field(None, description="Timestamp when file was uploaded")

    model_config = ConfigDict(from_attributes=True)


class FileUploadResponse(BaseModel):
    """
    Response returned immediately after file upload.
    """
    id: str
    filename: str
    feature_count: int
    crs: Optional[str]
    status: str
    message: str = "File processing completed successfully"

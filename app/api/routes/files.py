from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.file_service import FileService
from app.schemas.file import FileResponse, FileUploadResponse
from app.schemas.measurement import FileMeasurementsListResponse, FeatureMeasurementResponse

router = APIRouter(prefix="/files", tags=["Files"])


@router.post(
    "/",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and process geospatial file",
    description="Accepts KML (.kml) files or Shapefile ZIP (.zip) archives, calculates metric measurements for features, and stores results."
)
async def upload_file(
    file: UploadFile = File(..., description="Geospatial file (.kml or .zip shapefile)"),
    db: Session = Depends(get_db)
):
    service = FileService(db)
    file_record, _ = await service.upload_and_process_file(file)
    return file_record


@router.get(
    "/{id}/",
    response_model=FileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get file summary",
    description="Retrieves metadata and processing status for an uploaded file by UUID."
)
def get_file(
    id: str,
    db: Session = Depends(get_db)
):
    service = FileService(db)
    return service.get_file_summary(id)


@router.get(
    "/{id}/measurements/",
    response_model=FileMeasurementsListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get feature measurements",
    description="Retrieves computed metric measurements (area in sq meters, length in meters) for all features in the specified file."
)
def get_file_measurements(
    id: str,
    db: Session = Depends(get_db)
):
    service = FileService(db)
    file_record, measurements_models = service.get_file_measurements(id)

    formatted_measurements = []
    for m in measurements_models:
        formatted_measurements.append(
            FeatureMeasurementResponse(
                feature_id=m.feature_index,
                geometry_type=m.geometry_type,
                original_crs=m.original_crs,
                projected_crs=m.projected_crs,
                measurement_type=m.measurement_type,
                measurement_value=m.measurement_value,
                properties=m.properties or {},
                status=m.status,
                message=m.message
            )
        )

    return FileMeasurementsListResponse(
        file_id=file_record.id,
        filename=file_record.filename,
        feature_count=file_record.feature_count,
        measurements=formatted_measurements
    )

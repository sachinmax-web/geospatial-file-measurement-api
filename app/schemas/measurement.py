from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class FeatureMeasurementResponse(BaseModel):
    """
    Measurement result schema for a single geospatial feature.
    """
    feature_id: int = Field(..., description="Feature index/ID within the geospatial file")
    geometry_type: str = Field(..., description="Shapely geometry type name")
    original_crs: Optional[str] = Field(None, description="Original CRS detected in feature/file")
    projected_crs: Optional[str] = Field(None, description="Projected metric CRS used for measurement")
    measurement_type: Optional[str] = Field(None, description="Type of measurement: area_sq_m, length_m, none, or unsupported")
    measurement_value: Optional[float] = Field(None, description="Computed metric value (square meters for area, meters for length)")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Attributes/properties of the feature")
    status: str = Field("VALID", description="Feature status: VALID, REPAIRED, INVALID, UNSUPPORTED")
    message: Optional[str] = Field(None, description="Explanatory message or error detail")

    model_config = ConfigDict(from_attributes=True)


class FileMeasurementsListResponse(BaseModel):
    """
    Response schema for listing measurements of a file.
    """
    file_id: str
    filename: str
    feature_count: int
    measurements: list[FeatureMeasurementResponse]

from typing import Optional, Dict, Any
from shapely.geometry import base, Polygon, MultiPolygon, LineString, MultiLineString, Point, MultiPoint, GeometryCollection
import shapely.validation
from app.services.crs_service import CRSService
from app.core.logging import logger


class MeasurementService:
    """
    Computes metric measurements for geospatial geometries.
    Handles geometry validation, repair, CRS transformation, and metric calculation.
    """

    @staticmethod
    def validate_and_repair_geometry(geom: base.BaseGeometry) -> tuple[base.BaseGeometry, str, Optional[str]]:
        """
        Validates geometry. Attempts repair if invalid.
        Returns (repaired_geom, status_string, message_string).
        """
        if geom is None or geom.is_empty:
            return geom, "INVALID", "Geometry is null or empty"

        if geom.is_valid:
            return geom, "VALID", None

        # Attempt repair using make_valid or buffer(0)
        try:
            repaired = shapely.validation.make_valid(geom)
            if repaired.is_valid and not repaired.is_empty:
                logger.info("Successfully repaired invalid geometry using make_valid.")
                return repaired, "REPAIRED", "Geometry was invalid and successfully repaired."
        except Exception as e:
            logger.warning(f"make_valid failed: {e}")

        try:
            repaired = geom.buffer(0)
            if repaired.is_valid and not repaired.is_empty:
                logger.info("Successfully repaired invalid geometry using buffer(0).")
                return repaired, "REPAIRED", "Geometry was invalid and successfully repaired via buffer(0)."
        except Exception as e:
            logger.warning(f"buffer(0) repair failed: {e}")

        return geom, "INVALID", "Geometry is invalid and automatic repair failed."

    @classmethod
    def process_feature_measurement(
        cls,
        feature_id: int,
        geom: base.BaseGeometry,
        original_crs_str: Optional[str],
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Processes a single feature geometry:
        1. Validates and repairs geometry.
        2. Reprojects to metric projected CRS (UTM).
        3. Computes metric area ($m^2$) for polygons, length ($m$) for linestrings, null for points.
        """
        if properties is None:
            properties = {}

        if geom is None or geom.is_empty:
            return {
                "feature_id": feature_id,
                "geometry_type": "None" if geom is None else geom.geom_type,
                "original_crs": original_crs_str,
                "projected_crs": None,
                "measurement_type": "none",
                "measurement_value": None,
                "properties": properties,
                "status": "INVALID",
                "message": "Geometry is null or empty."
            }

        geom_type = geom.geom_type

        # Step 1: Validate and Repair
        valid_geom, status, status_msg = cls.validate_and_repair_geometry(geom)

        if status == "INVALID":
            return {
                "feature_id": feature_id,
                "geometry_type": geom_type,
                "original_crs": original_crs_str,
                "projected_crs": None,
                "measurement_type": "invalid",
                "measurement_value": None,
                "properties": properties,
                "status": "INVALID",
                "message": status_msg
            }

        # Step 2: Handle Point geometries (No measurement required)
        if isinstance(valid_geom, (Point, MultiPoint)):
            return {
                "feature_id": feature_id,
                "geometry_type": geom_type,
                "original_crs": original_crs_str,
                "projected_crs": None,
                "measurement_type": "none",
                "measurement_value": None,
                "properties": properties,
                "status": status,
                "message": "No measurement required for Point geometry"
            }

        # Step 3: Handle Unsupported geometries
        if isinstance(valid_geom, GeometryCollection) or geom_type not in (
            "Polygon", "MultiPolygon", "LineString", "MultiLineString"
        ):
            return {
                "feature_id": feature_id,
                "geometry_type": geom_type,
                "original_crs": original_crs_str,
                "projected_crs": None,
                "measurement_type": "unsupported",
                "measurement_value": None,
                "properties": properties,
                "status": "UNSUPPORTED",
                "message": f"Measurement unsupported for geometry type '{geom_type}'."
            }

        # Step 4: Reproject to metric projected CRS
        try:
            projected_geom, orig_crs, proj_crs = CRSService.project_geometry(valid_geom, original_crs_str)
        except Exception as e:
            logger.error(f"CRS projection failed for feature {feature_id}: {e}")
            return {
                "feature_id": feature_id,
                "geometry_type": geom_type,
                "original_crs": original_crs_str,
                "projected_crs": None,
                "measurement_type": "error",
                "measurement_value": None,
                "properties": properties,
                "status": "INVALID",
                "message": f"CRS transformation failed: {str(e)}"
            }

        # Step 5: Compute Metric Measurement
        if isinstance(valid_geom, (Polygon, MultiPolygon)):
            area_sq_m = round(float(projected_geom.area), 2)
            return {
                "feature_id": feature_id,
                "geometry_type": geom_type,
                "original_crs": orig_crs,
                "projected_crs": proj_crs,
                "measurement_type": "area_sq_m",
                "measurement_value": area_sq_m,
                "properties": properties,
                "status": status,
                "message": status_msg
            }

        elif isinstance(valid_geom, (LineString, MultiLineString)):
            length_m = round(float(projected_geom.length), 2)
            return {
                "feature_id": feature_id,
                "geometry_type": geom_type,
                "original_crs": orig_crs,
                "projected_crs": proj_crs,
                "measurement_type": "length_m",
                "measurement_value": length_m,
                "properties": properties,
                "status": status,
                "message": status_msg
            }

        return {
            "feature_id": feature_id,
            "geometry_type": geom_type,
            "original_crs": orig_crs,
            "projected_crs": proj_crs,
            "measurement_type": "unsupported",
            "measurement_value": None,
            "properties": properties,
            "status": "UNSUPPORTED",
            "message": f"No metric logic defined for geometry type '{geom_type}'."
        }

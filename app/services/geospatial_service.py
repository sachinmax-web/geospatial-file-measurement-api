import os
import shutil
import tempfile
from typing import List, Dict, Any, Tuple
import geopandas as gpd

from app.utils.kml_parser import read_kml_with_fallback
from app.utils.zip_utils import validate_and_extract_shapefile_zip
from app.services.measurement_service import MeasurementService
from app.exceptions.custom_exceptions import GeospatialProcessingException, FileCorruptedException
from app.core.logging import logger


class GeospatialService:
    """
    Coordinates reading geospatial files (KML, Shapefile ZIP), extracting features,
    and invoking measurement processing.
    """

    @classmethod
    def read_geospatial_file(cls, file_path: str, file_type: str) -> Tuple[gpd.GeoDataFrame, str, str]:
        """
        Reads KML or Shapefile ZIP into a GeoPandas GeoDataFrame.
        Returns (gdf, crs_string, cleanup_dir_if_any).
        """
        temp_extract_dir = ""

        if file_type == "kml":
            try:
                gdf = read_kml_with_fallback(file_path)
                crs_str = f"EPSG:{gdf.crs.to_epsg()}" if gdf.crs and gdf.crs.to_epsg() else "EPSG:4326"
                return gdf, crs_str, ""
            except Exception as e:
                logger.error(f"Error reading KML file '{file_path}': {e}")
                raise FileCorruptedException(f"Failed to parse KML file: {str(e)}")

        elif file_type == "shapefile_zip":
            temp_extract_dir = tempfile.mkdtemp(prefix="shp_extract_")
            try:
                shp_path = validate_and_extract_shapefile_zip(file_path, temp_extract_dir)
                gdf = gpd.read_file(shp_path)
                
                crs_str = "Unknown"
                if gdf.crs:
                    epsg = gdf.crs.to_epsg()
                    crs_str = f"EPSG:{epsg}" if epsg else gdf.crs.name or str(gdf.crs)

                return gdf, crs_str, temp_extract_dir
            except Exception as e:
                # Clean up on error
                if temp_extract_dir and os.path.exists(temp_extract_dir):
                    shutil.rmtree(temp_extract_dir, ignore_errors=True)
                logger.error(f"Error reading shapefile ZIP '{file_path}': {e}")
                if not isinstance(e, FileCorruptedException):
                    raise FileCorruptedException(f"Failed to process Shapefile ZIP archive: {str(e)}")
                raise

        else:
            raise GeospatialProcessingException(f"Unsupported file type '{file_type}'")

    @classmethod
    def process_geospatial_file(
        cls,
        file_path: str,
        file_type: str
    ) -> Tuple[str, int, List[Dict[str, Any]]]:
        """
        Processes a file: reads features, computes measurements, cleans up temporary files.
        Returns (detected_crs, feature_count, list_of_feature_measurements).
        """
        cleanup_dir = ""
        try:
            gdf, detected_crs, cleanup_dir = cls.read_geospatial_file(file_path, file_type)
            feature_count = len(gdf)

            measurements = []
            for idx, row in gdf.iterrows():
                geom = row.geometry if hasattr(row, "geometry") else None
                
                # Extract properties/attributes
                properties = {}
                for col in gdf.columns:
                    if col != "geometry" and col != "properties":
                        val = row[col]
                        if not hasattr(val, "isoformat") and not isinstance(val, (dict, list, tuple)):
                            properties[col] = str(val) if val is not None else None

                # Mix in explicit properties column if parsed by KML
                if "properties" in gdf.columns and isinstance(row["properties"], dict):
                    properties.update(row["properties"])

                feature_result = MeasurementService.process_feature_measurement(
                    feature_id=int(idx),
                    geom=geom,
                    original_crs_str=detected_crs,
                    properties=properties
                )
                measurements.append(feature_result)

            return detected_crs, feature_count, measurements

        finally:
            if cleanup_dir and os.path.exists(cleanup_dir):
                shutil.rmtree(cleanup_dir, ignore_errors=True)

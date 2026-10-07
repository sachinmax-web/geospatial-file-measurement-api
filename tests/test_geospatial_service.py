import os
import pytest
from app.services.geospatial_service import GeospatialService


def test_read_kml_polygons():
    kml_path = os.path.join("sample_data", "sample_polygons.kml")
    if not os.path.exists(kml_path):
        pytest.skip("sample_polygons.kml missing")

    crs, count, measurements = GeospatialService.process_geospatial_file(kml_path, "kml")
    
    assert count >= 1
    assert "EPSG:4326" in crs
    assert measurements[0]["measurement_type"] == "area_sq_m"


def test_read_kml_lines():
    kml_path = os.path.join("sample_data", "sample_lines.kml")
    if not os.path.exists(kml_path):
        pytest.skip("sample_lines.kml missing")

    crs, count, measurements = GeospatialService.process_geospatial_file(kml_path, "kml")
    
    assert count == 2
    assert measurements[0]["geometry_type"] == "LineString"
    assert measurements[0]["measurement_type"] == "length_m"
    assert measurements[1]["geometry_type"] == "Point"
    assert measurements[1]["measurement_type"] == "none"


def test_read_shapefile_zip():
    zip_path = os.path.join("sample_data", "sample_shapefile.zip")
    if not os.path.exists(zip_path):
        pytest.skip("sample_shapefile.zip missing")

    crs, count, measurements = GeospatialService.process_geospatial_file(zip_path, "shapefile_zip")
    
    assert count >= 1
    assert measurements[0]["measurement_type"] == "area_sq_m"

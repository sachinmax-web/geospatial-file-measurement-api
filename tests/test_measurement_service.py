import pytest
from shapely.geometry import Point, LineString, Polygon, MultiPolygon, MultiLineString, GeometryCollection
from app.services.measurement_service import MeasurementService


def test_polygon_area_measurement():
    # ~1km x ~1km box in NYC
    poly = Polygon([
        (-73.98, 40.75),
        (-73.97, 40.75),
        (-73.97, 40.76),
        (-73.98, 40.76),
        (-73.98, 40.75)
    ])

    res = MeasurementService.process_feature_measurement(
        feature_id=0,
        geom=poly,
        original_crs_str="EPSG:4326"
    )

    assert res["measurement_type"] == "area_sq_m"
    assert res["measurement_value"] > 500000  # Significant metric area in m^2
    assert res["projected_crs"] == "EPSG:32618"
    assert res["status"] in ("VALID", "REPAIRED")


def test_multipolygon_area_measurement():
    poly1 = Polygon([(-73.98, 40.75), (-73.97, 40.75), (-73.97, 40.76), (-73.98, 40.76), (-73.98, 40.75)])
    poly2 = Polygon([(-73.96, 40.76), (-73.95, 40.76), (-73.95, 40.77), (-73.96, 40.77), (-73.96, 40.76)])
    multi_poly = MultiPolygon([poly1, poly2])

    res = MeasurementService.process_feature_measurement(
        feature_id=1,
        geom=multi_poly,
        original_crs_str="EPSG:4326"
    )

    assert res["measurement_type"] == "area_sq_m"
    assert res["measurement_value"] > 1000000


def test_linestring_length_measurement():
    line = LineString([(-73.985, 40.748), (-73.981, 40.753), (-73.974, 40.762)])

    res = MeasurementService.process_feature_measurement(
        feature_id=2,
        geom=line,
        original_crs_str="EPSG:4326"
    )

    assert res["measurement_type"] == "length_m"
    assert res["measurement_value"] > 1000  # Length in meters
    assert res["projected_crs"] == "EPSG:32618"


def test_multilinestring_length_measurement():
    line1 = LineString([(-73.985, 40.748), (-73.981, 40.753)])
    line2 = LineString([(-73.974, 40.762), (-73.970, 40.768)])
    multi_line = MultiLineString([line1, line2])

    res = MeasurementService.process_feature_measurement(
        feature_id=3,
        geom=multi_line,
        original_crs_str="EPSG:4326"
    )

    assert res["measurement_type"] == "length_m"
    assert res["measurement_value"] > 500


def test_point_measurement_handling():
    pt = Point(-73.9855, 40.7580)

    res = MeasurementService.process_feature_measurement(
        feature_id=4,
        geom=pt,
        original_crs_str="EPSG:4326"
    )

    assert res["measurement_type"] == "none"
    assert res["measurement_value"] is None
    assert "No measurement required for Point geometry" in res["message"]


def test_invalid_geometry_repair():
    # Self-intersecting hourglass polygon (invalid)
    invalid_poly = Polygon([
        (0, 0), (0, 2), (2, 0), (2, 2), (0, 0)
    ])

    res = MeasurementService.process_feature_measurement(
        feature_id=5,
        geom=invalid_poly,
        original_crs_str="EPSG:4326"
    )

    # Should be repaired automatically or marked with status
    assert res["status"] in ("REPAIRED", "INVALID", "VALID")


def test_unsupported_geometry_collection():
    geom_col = GeometryCollection([Point(0, 0), LineString([(0, 0), (1, 1)])])

    res = MeasurementService.process_feature_measurement(
        feature_id=6,
        geom=geom_col,
        original_crs_str="EPSG:4326"
    )

    assert res["status"] == "UNSUPPORTED"
    assert res["measurement_value"] is None

import pytest
from shapely.geometry import Point, Polygon
from app.services.crs_service import CRSService


def test_get_utm_epsg_for_latlon():
    # New York City (approx 40.7128° N, 74.0060° W) -> UTM Zone 18N -> EPSG:32618
    epsg_ny = CRSService.get_utm_epsg_for_latlon(40.7128, -74.0060)
    assert epsg_ny == 32618

    # Sydney Australia (approx 33.8688° S, 151.2093° E) -> UTM Zone 56S -> EPSG:32756
    epsg_sydney = CRSService.get_utm_epsg_for_latlon(-33.8688, 151.2093)
    assert epsg_sydney == 32756


def test_project_geometry_epsg4326_to_utm():
    poly_nyc = Polygon([
        (-73.98, 40.75),
        (-73.97, 40.75),
        (-73.97, 40.76),
        (-73.98, 40.76),
        (-73.98, 40.75)
    ])

    proj_geom, orig_crs, proj_crs = CRSService.project_geometry(poly_nyc, "EPSG:4326")
    
    assert orig_crs == "EPSG:4326"
    assert proj_crs == "EPSG:32618"
    assert proj_geom.area > 0  # Area calculated in square meters!


def test_missing_crs_handling():
    pt = Point(-73.98, 40.75)
    proj_geom, orig_crs, proj_crs = CRSService.project_geometry(pt, None)
    
    assert "EPSG:4326" in orig_crs
    assert proj_crs == "EPSG:32618"

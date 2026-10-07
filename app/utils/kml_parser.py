import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Tuple
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon, MultiPolygon, MultiLineString, MultiPoint, GeometryCollection
import shapely.wkt
from app.core.logging import logger


def parse_kml_coordinates(coords_str: str) -> List[Tuple[float, float]]:
    """
    Parses coordinate string from KML element: 'lon,lat,alt lon,lat,alt ...'
    Returns list of (lon, lat) tuples.
    """
    coords = []
    tokens = coords_str.strip().split()
    for token in tokens:
        parts = token.split(',')
        if len(parts) >= 2:
            try:
                lon = float(parts[0])
                lat = float(parts[1])
                coords.append((lon, lat))
            except ValueError:
                continue
    return coords


def parse_kml_geometry(elem: ET.Element) -> Any:
    """
    Recursively parses KML XML elements into Shapely geometries.
    """
    # Remove XML namespace prefix if present
    tag = elem.tag.split('}')[-1]

    if tag == 'Point':
        coordinates_elem = elem.find('.//{*}coordinates')
        if coordinates_elem is not None and coordinates_elem.text:
            coords = parse_kml_coordinates(coordinates_elem.text)
            if coords:
                return Point(coords[0])

    elif tag == 'LineString':
        coordinates_elem = elem.find('.//{*}coordinates')
        if coordinates_elem is not None and coordinates_elem.text:
            coords = parse_kml_coordinates(coordinates_elem.text)
            if len(coords) >= 2:
                return LineString(coords)

    elif tag == 'Polygon':
        outer_boundary = elem.find('.//{*}outerBoundaryIs//{*}coordinates')
        if outer_boundary is not None and outer_boundary.text:
            exterior_coords = parse_kml_coordinates(outer_boundary.text)
            if len(exterior_coords) >= 3:
                interiors = []
                inner_boundaries = elem.findall('.//{*}innerBoundaryIs//{*}coordinates')
                for inner in inner_boundaries:
                    if inner.text:
                        int_coords = parse_kml_coordinates(inner.text)
                        if len(int_coords) >= 3:
                            interiors.append(int_coords)
                return Polygon(shell=exterior_coords, holes=interiors)

    elif tag in ('MultiGeometry', 'MultiPolygon', 'MultiLineString', 'MultiPoint'):
        geoms = []
        for child in elem:
            g = parse_kml_geometry(child)
            if g is not None and not g.is_empty:
                geoms.append(g)
        if geoms:
            if all(isinstance(g, Polygon) for g in geoms):
                return MultiPolygon(geoms)
            elif all(isinstance(g, LineString) for g in geoms):
                return MultiLineString(geoms)
            elif all(isinstance(g, Point) for g in geoms):
                return MultiPoint(geoms)
            else:
                return GeometryCollection(geoms)

    # Check children if tag was Container/Placemark wrapper
    for child in elem:
        g = parse_kml_geometry(child)
        if g is not None:
            return g

    return None


def read_kml_with_fallback(kml_file_path: str) -> gpd.GeoDataFrame:
    """
    Reads a KML file into a GeoPandas GeoDataFrame.
    Attempts GeoPandas/Fiona read_file first. If GDAL KML driver is unavailable,
    falls back to custom Python ElementTree KML parser.
    """
    try:
        # Enable fiona KML driver if available
        import fiona
        fiona.drvsupport.supported_drivers['KML'] = 'rw'
        fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'
        gdf = gpd.read_file(kml_file_path, driver='KML')
        if len(gdf) > 0:
            if gdf.crs is None:
                gdf.set_crs(epsg=4326, inplace=True)
            return gdf
    except Exception as e:
        logger.info(f"Fiona/GeoPandas KML driver failed or uninstalled ({e}). Using XML ElementTree fallback parser.")

    # ElementTree Fallback Parser
    tree = ET.parse(kml_file_path)
    root = tree.getroot()
    
    placemarks = root.findall('.//{*}Placemark')
    records = []
    
    for i, pm in enumerate(placemarks):
        name_elem = pm.find('{*}name')
        desc_elem = pm.find('{*}description')
        
        name = name_elem.text if name_elem is not None else f"Feature_{i}"
        desc = desc_elem.text if desc_elem is not None else ""
        
        properties = {"name": name, "description": desc}

        # Extra ExtendedData properties if present
        for data_elem in pm.findall('.//{*}Data'):
            data_name = data_elem.attrib.get('name')
            val_elem = data_elem.find('{*}value')
            if data_name and val_elem is not None:
                properties[data_name] = val_elem.text

        geom = parse_kml_geometry(pm)
        if geom is not None:
            records.append({
                "geometry": geom,
                "name": name,
                "properties": properties
            })

    if not records:
        # Create empty GeoDataFrame with 4326 CRS if no placemarks found
        return gpd.GeoDataFrame(columns=["geometry", "name", "properties"], crs="EPSG:4326")

    df = pd.DataFrame(records)
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
    return gdf

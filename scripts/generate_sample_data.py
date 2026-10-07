import os
import zipfile
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, MultiPolygon


def generate_sample_files(output_dir: str = "sample_data"):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Generating sample geospatial files in '{output_dir}'...")

    # 1. Generate KML with Polygons
    kml_poly_content = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Sample Polygons</name>
    <Placemark>
      <name>Central Park Zone</name>
      <description>Sample polygon feature in New York</description>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              -73.973,40.764,0
              -73.981,40.768,0
              -73.958,40.800,0
              -73.949,40.796,0
              -73.973,40.764,0
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>"""

    kml_poly_path = os.path.join(output_dir, "sample_polygons.kml")
    with open(kml_poly_path, "w", encoding="utf-8") as f:
        f.write(kml_poly_content)
    print(f"Created {kml_poly_path}")

    # 2. Generate KML with Lines and Points
    kml_lines_content = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Sample Lines and Points</name>
    <Placemark>
      <name>Broadway Route</name>
      <LineString>
        <coordinates>
          -73.985,40.748,0
          -73.981,40.753,0
          -73.974,40.762,0
        </coordinates>
      </LineString>
    </Placemark>
    <Placemark>
      <name>Times Square Landmark</name>
      <Point>
        <coordinates>-73.9855,40.7580,0</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>"""

    kml_lines_path = os.path.join(output_dir, "sample_lines.kml")
    with open(kml_lines_path, "w", encoding="utf-8") as f:
        f.write(kml_lines_content)
    print(f"Created {kml_lines_path}")

    # 3. Generate Valid Shapefile ZIP with Polygons
    poly_data = [
        {"name": "Parcel Alpha", "geometry": Polygon([(-73.98, 40.75), (-73.97, 40.75), (-73.97, 40.76), (-73.98, 40.76), (-73.98, 40.75)])},
        {"name": "Parcel Beta", "geometry": Polygon([(-73.96, 40.76), (-73.95, 40.76), (-73.95, 40.77), (-73.96, 40.77), (-73.96, 40.76)])}
    ]
    gdf_poly = gpd.GeoDataFrame(poly_data, crs="EPSG:4326")

    temp_shp_dir = os.path.join(output_dir, "_temp_shp")
    os.makedirs(temp_shp_dir, exist_ok=True)
    shp_base = os.path.join(temp_shp_dir, "survey_polygons.shp")
    gdf_poly.to_file(shp_base)

    valid_zip_path = os.path.join(output_dir, "sample_shapefile.zip")
    with zipfile.ZipFile(valid_zip_path, "w") as zf:
        for fname in os.listdir(temp_shp_dir):
            fpath = os.path.join(temp_shp_dir, fname)
            zf.write(fpath, arcname=fname)
    
    print(f"Created {valid_zip_path}")

    # 4. Generate Missing Component ZIP (Missing .prj)
    missing_zip_path = os.path.join(output_dir, "missing_components.zip")
    with zipfile.ZipFile(missing_zip_path, "w") as zf:
        for fname in os.listdir(temp_shp_dir):
            if not fname.endswith(".prj"):
                fpath = os.path.join(temp_shp_dir, fname)
                zf.write(fpath, arcname=fname)
    print(f"Created {missing_zip_path}")

    # 5. Generate Malicious Zip Slip Archive
    zip_slip_path = os.path.join(output_dir, "zip_slip_attack.zip")
    with zipfile.ZipFile(zip_slip_path, "w") as zf:
        zf.writestr("../../evil.txt", "malicious payload")
        for fname in os.listdir(temp_shp_dir):
            fpath = os.path.join(temp_shp_dir, fname)
            zf.write(fpath, arcname=fname)
    print(f"Created {zip_slip_path}")

    # Cleanup temp directory
    for fname in os.listdir(temp_shp_dir):
        os.remove(os.path.join(temp_shp_dir, fname))
    os.rmdir(temp_shp_dir)
    
    print("Sample file generation complete.")


if __name__ == "__main__":
    generate_sample_files()

from typing import Tuple, Optional, Any
import pyproj
from pyproj import CRS
from shapely.geometry import base, Point
import shapely.ops
import geopandas as gpd
from app.core.logging import logger


class CRSService:
    """
    Handles CRS detection, validation, automatic projected CRS selection (UTM),
    and metric geometry transformation.
    """

    @staticmethod
    def parse_crs(crs_input: Optional[Any] = None) -> Tuple[Optional[CRS], Optional[str]]:
        """
        Parses various CRS representations into a pyproj.CRS object and EPSG string.
        """
        if crs_input is None:
            return None, None

        try:
            if isinstance(crs_input, CRS):
                crs_obj = crs_input
            else:
                crs_obj = CRS.from_user_input(crs_input)

            epsg_code = crs_obj.to_epsg()
            crs_str = f"EPSG:{epsg_code}" if epsg_code else crs_obj.name or str(crs_input)
            return crs_obj, crs_str
        except Exception as e:
            logger.warning(f"Could not parse CRS '{crs_input}': {e}")
            return None, str(crs_input)

    @staticmethod
    def get_utm_epsg_for_latlon(lat: float, lon: float) -> int:
        """
        Calculates the EPSG code for the appropriate UTM zone given latitude and longitude.
        """
        zone_number = int((lon + 180) / 6) + 1
        if lat >= 0:
            return 32600 + zone_number  # Northern Hemisphere
        else:
            return 32700 + zone_number  # Southern Hemisphere

    @classmethod
    def get_target_projected_crs(
        cls,
        geom: base.BaseGeometry,
        source_crs_obj: Optional[CRS]
    ) -> Tuple[CRS, str]:
        """
        Determines the optimal metric projected CRS for a given geometry.
        - If source_crs is geographic (or missing, defaulting to EPSG:4326 for bounds):
            Calculates UTM zone based on geometry centroid.
        - If source_crs is already projected with metric units:
            Keeps the existing projected CRS.
        - If source_crs is projected with non-metric units (e.g. feet):
            Reprojects to metric UTM.
        """
        # If source CRS is projected and uses metric units, keep it
        if source_crs_obj is not None and source_crs_obj.is_projected:
            # Check unit
            unit_name = source_crs_obj.axis_info[0].unit_name.lower() if source_crs_obj.axis_info else "metre"
            if "meter" in unit_name or "metre" in unit_name or "m" == unit_name:
                epsg = source_crs_obj.to_epsg()
                crs_str = f"EPSG:{epsg}" if epsg else source_crs_obj.name
                return source_crs_obj, crs_str

        # Calculate centroid in geographic terms
        if geom.is_empty:
            target_epsg = 3857  # Web Mercator fallback for empty
            return CRS.from_epsg(target_epsg), f"EPSG:{target_epsg}"

        centroid = geom.centroid
        lon, lat = centroid.x, centroid.y

        # Determine UTM zone
        utm_epsg = cls.get_utm_epsg_for_latlon(lat, lon)
        target_crs_obj = CRS.from_epsg(utm_epsg)
        return target_crs_obj, f"EPSG:{utm_epsg}"

    @classmethod
    def project_geometry(
        cls,
        geom: base.BaseGeometry,
        source_crs_str: Optional[str] = None
    ) -> Tuple[base.BaseGeometry, Optional[str], str]:
        """
        Reprojects a single Shapely geometry to a metric projected CRS.
        Returns (projected_geometry, original_crs_str, projected_crs_str).
        """
        source_crs_obj, parsed_source_str = cls.parse_crs(source_crs_str)

        if source_crs_obj is None:
            # Missing CRS handling: Assume geographic EPSG:4326 with warning
            logger.warning("Missing CRS detected for feature; assuming EPSG:4326 for UTM projection.")
            source_crs_obj = CRS.from_epsg(4326)
            parsed_source_str = "EPSG:4326 (assumed)"

        target_crs_obj, projected_crs_str = cls.get_target_projected_crs(geom, source_crs_obj)

        if source_crs_obj == target_crs_obj:
            return geom, parsed_source_str, projected_crs_str

        # Perform transformation using pyproj Transformer
        transformer = pyproj.Transformer.from_crs(
            source_crs_obj,
            target_crs_obj,
            always_xy=True
        )

        projected_geom = shapely.ops.transform(transformer.transform, geom)
        return projected_geom, parsed_source_str, projected_crs_str

import os
import pytest
import tempfile
from app.utils.zip_utils import validate_and_extract_shapefile_zip, is_safe_zip_path
from app.exceptions.custom_exceptions import ZipSecurityException, MissingShapefileComponentException


def test_is_safe_zip_path_security():
    target_dir = os.path.abspath("/tmp/safe_dir")
    
    # Safe paths
    assert is_safe_zip_path(target_dir, "data.shp") is True
    assert is_safe_zip_path(target_dir, "subfolder/data.shp") is True
    
    # Dangerous paths (Zip Slip)
    assert is_safe_zip_path(target_dir, "../etc/passwd") is False
    assert is_safe_zip_path(target_dir, "..\\Windows\\System32\\cmd.exe") is False


def test_zip_slip_attack_prevention():
    zip_slip_path = os.path.join("sample_data", "zip_slip_attack.zip")
    if not os.path.exists(zip_slip_path):
        pytest.skip("sample_data/zip_slip_attack.zip not found")

    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(ZipSecurityException):
            validate_and_extract_shapefile_zip(zip_slip_path, temp_dir)


def test_missing_shapefile_components():
    missing_zip_path = os.path.join("sample_data", "missing_components.zip")
    if not os.path.exists(missing_zip_path):
        pytest.skip("sample_data/missing_components.zip not found")

    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(MissingShapefileComponentException):
            validate_and_extract_shapefile_zip(missing_zip_path, temp_dir)


def test_valid_shapefile_zip_extraction():
    valid_zip_path = os.path.join("sample_data", "sample_shapefile.zip")
    if not os.path.exists(valid_zip_path):
        pytest.skip("sample_data/sample_shapefile.zip not found")

    with tempfile.TemporaryDirectory() as temp_dir:
        extracted_shp = validate_and_extract_shapefile_zip(valid_zip_path, temp_dir)
        assert os.path.exists(extracted_shp)
        assert extracted_shp.endswith(".shp")

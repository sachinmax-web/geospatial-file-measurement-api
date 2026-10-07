import os
import pytest


def test_health_check_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["database"] == "healthy"


def test_upload_kml_api(client):
    kml_path = os.path.join("sample_data", "sample_polygons.kml")
    if not os.path.exists(kml_path):
        pytest.skip("sample_polygons.kml missing")

    with open(kml_path, "rb") as f:
        response = client.post("/api/files/", files={"file": ("sample_polygons.kml", f, "application/vnd.google-earth.kml+xml")})

    assert response.status_code == 201
    file_data = response.json()
    assert "id" in file_data
    assert file_data["filename"] == "sample_polygons.kml"
    assert file_data["status"] == "COMPLETED"
    assert file_data["feature_count"] >= 1

    file_id = file_data["id"]

    # Test GET /api/files/{id}/
    get_res = client.get(f"/api/files/{file_id}/")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == file_id

    # Test GET /api/files/{id}/measurements/
    meas_res = client.get(f"/api/files/{file_id}/measurements/")
    assert meas_res.status_code == 200
    meas_data = meas_res.json()
    assert meas_data["file_id"] == file_id
    assert len(meas_data["measurements"]) >= 1
    assert meas_data["measurements"][0]["measurement_type"] == "area_sq_m"
    assert meas_data["measurements"][0]["measurement_value"] > 0


def test_upload_shapefile_zip_api(client):
    zip_path = os.path.join("sample_data", "sample_shapefile.zip")
    if not os.path.exists(zip_path):
        pytest.skip("sample_shapefile.zip missing")

    with open(zip_path, "rb") as f:
        response = client.post("/api/files/", files={"file": ("sample_shapefile.zip", f, "application/zip")})

    assert response.status_code == 201
    file_data = response.json()
    assert file_data["status"] == "COMPLETED"
    assert file_data["feature_count"] >= 1


def test_upload_invalid_extension(client):
    response = client.post("/api/files/", files={"file": ("document.txt", b"hello world", "text/plain")})
    assert response.status_code == 400
    assert "Unsupported file extension" in response.json()["message"]


def test_upload_zip_slip_attack_rejected(client):
    zip_slip_path = os.path.join("sample_data", "zip_slip_attack.zip")
    if not os.path.exists(zip_slip_path):
        pytest.skip("zip_slip_attack.zip missing")

    with open(zip_slip_path, "rb") as f:
        response = client.post("/api/files/", files={"file": ("zip_slip_attack.zip", f, "application/zip")})

    assert response.status_code == 400
    assert "Zip Slip" in response.json()["message"]


def test_get_nonexistent_file_404(client):
    response = client.get("/api/files/nonexistent-uuid-12345/")
    assert response.status_code == 404
    assert "not found" in response.json()["message"]

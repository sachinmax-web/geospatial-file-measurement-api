# Geospatial File Measurement API

A production-grade Python backend built with **FastAPI**, **GeoPandas**, **Shapely**, **PyProj**, **SQLAlchemy**, and **PostgreSQL/PostGIS** for uploading, processing, re-projecting, and measuring geospatial vector files (`.kml` and Shapefile `.zip` archives).

---

## 🚀 1. Project Overview

The **Geospatial File Measurement API** provides scalable REST endpoints to ingest geospatial vector data, inspect Coordinate Reference Systems (CRS), dynamically reproject geographic geometries (e.g. `EPSG:4326`) into local metric Universal Transverse Mercator (UTM) projected coordinate systems, compute accurate metric measurements (polygon area in $m^2$, linestring length in meters), repair invalid geometries, and persist feature-level analytics to a database.

---

## ✨ 2. Key Features

- **Multi-Format Processing**: Full support for `.kml` files and Shapefile `.zip` archives containing `.shp`, `.shx`, `.dbf`, `.prj`.
- **Zip-Slip & Path Traversal Protection**: Hardened archive extractor preventing directory traversal attacks (`..`, absolute paths, symlinks).
- **Dual KML Parser**: High-performance Fiona/GDAL KML driver with an automatic XML `ElementTree` fallback ensuring 100% parsing reliability in any environment.
- **Dynamic Metric CRS Transformation**: Detects geographic CRS (e.g., `EPSG:4326` in degrees) and automatically computes optimal local metric UTM projection (e.g. `EPSG:32618`) based on feature centroids before metric calculations. Never calculates metric distance/area directly in degrees!
- **Metric Calculations**:
  - **Polygons & MultiPolygons**: Area in square meters ($m^2$).
  - **LineStrings & MultiLineStrings**: Length in meters ($m$).
  - **Points & MultiPoints**: Handled with `measurement = null` and explanatory status.
  - **Unsupported / Empty Geometries**: Gracefully captured without crashing file processing.
- **Invalid Geometry Repair**: Automatic geometry repair using `shapely.validation.make_valid` and buffer zero-width healing.
- **Layered Architecture**: Strict separation of concerns (API Routes -> Service Layer -> Repository Layer -> Database).
- **Comprehensive Pytest Suite**: 28 automated tests covering security, CRS projection, metric accuracy, invalid formats, and API responses.
- **Docker & PostGIS Ready**: Fully containerized environment using `docker-compose` with PostgreSQL/PostGIS.

---

## 🛠️ 3. Tech Stack

- **Framework**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2
- **Geospatial Libraries**: GeoPandas, Shapely 2.0, PyProj, Fiona / PyOGRIO
- **Database & ORM**: PostgreSQL / PostGIS, SQLite (Local Dev), SQLAlchemy 2.0, Alembic
- **Testing & Tooling**: Pytest, HTTPX, Docker, Docker Compose

---

## 🏗️ 4. Architecture

```
                               ┌───────────────────────────┐
                               │   HTTP Client / OpenAPI   │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │     FastAPI Router        │
                               │  (/api/files, /health)    │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │       File Service        │
                               └──────┬─────────────────┬──┘
                                      │                 │
                                      ▼                 ▼
             ┌───────────────────────────────────┐   ┌───────────────────────────┐
             │         Geospatial Service        │   │      File Repository      │
             │  (KML Parser / Zip Security)      │   └─────────────┬─────────────┘
             └────────────────┬──────────────────┘                 │
                              │                                    ▼
                              ▼                      ┌───────────────────────────┐
             ┌───────────────────────────────────┐   │     PostgreSQL / SQLite   │
             │   CRS Service & Measurement Svc   │   │  (Files & Measurements)   │
             │   (UTM Selection, Metric Area/Len)│   └───────────────────────────┘
             └───────────────────────────────────┘
```

---

## 📁 5. Folder Structure

```
geospatial-measurement-api/
├── app/
│   ├── main.py                    # FastAPI app initialization, middleware & routes
│   ├── api/
│   │   ├── router.py              # Main API router aggregating endpoints
│   │   └── routes/
│   │       ├── files.py           # Upload, detail, & measurement endpoints
│   │       └── health.py          # Health check endpoint
│   ├── core/
│   │   ├── config.py              # Pydantic BaseSettings configuration
│   │   └── logging.py             # Application structured logging
│   ├── db/
│   │   ├── database.py            # SQLAlchemy engine setup
│   │   ├── models.py              # FileModel and MeasurementModel ORM tables
│   │   └── session.py             # Request DB session provider
│   ├── schemas/
│   │   ├── file.py                # File API request & response schemas
│   │   └── measurement.py         # Measurement Pydantic response schemas
│   ├── services/
│   │   ├── file_service.py        # File processing orchestrator service
│   │   ├── geospatial_service.py  # File reader & feature extractor
│   │   ├── crs_service.py         # CRS detection & UTM metric re-projection
│   │   └── measurement_service.py # Metric area ($m^2$) & length ($m$) logic
│   ├── repositories/
│   │   └── file_repository.py     # Database CRUD operations
│   ├── utils/
│   │   ├── file_validation.py     # Extension, size, magic header validation
│   │   ├── zip_utils.py           # Secure ZIP extraction & Zip Slip security
│   │   └── kml_parser.py          # Dual GeoPandas + XML parsing fallback
│   └── exceptions/
│       ├── custom_exceptions.py   # Domain exceptions
│       └── handlers.py            # Centralized exception handlers
├── alembic/                       # Database migrations folder
├── scripts/
│   └── generate_sample_data.py    # Script to create valid sample KML & Shapefile files
├── sample_data/                   # Sample KML and Shapefile ZIP archives
├── tests/                         # Pytest test suite (28 tests)
│   ├── conftest.py
│   ├── test_file_validation.py
│   ├── test_zip_security.py
│   ├── test_crs_service.py
│   ├── test_measurement_service.py
│   ├── test_geospatial_service.py
│   └── test_api_files.py
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .env
├── .gitignore
├── requirements.txt
├── alembic.ini
└── README.md
```

---

## 🔄 6. File Processing Flow

1. **Upload Request**: Client sends multipart/form-data request to `POST /api/files/`.
2. **File Validation**:
   - Check extension (`.kml`, `.zip`).
   - Validate magic bytes (`PK\x03\x04` for ZIP, XML headers for KML).
   - Enforce 50MB file size limit.
3. **Secure Extraction** (ZIP Shapefiles):
   - Path traversal verification (disallows `..`, absolute paths, symlinks).
   - Checks presence of mandatory component files (`.shp`, `.shx`, `.dbf`, `.prj`).
4. **Feature Extraction**: Reads features into Shapely geometries.
5. **Geometry Validation & Repair**: Checks `is_valid`. Attempts `shapely.validation.make_valid` / `buffer(0)` if invalid.
6. **CRS Detection & Metric Re-projection**:
   - Detects original CRS (e.g. `EPSG:4326`).
   - Computes geometry centroid to calculate appropriate UTM projected CRS (e.g., `EPSG:32618`).
   - Reprojects geometry into metric coordinates.
7. **Metric Calculations**:
   - Polygons: `projected_geom.area` -> Square meters ($m^2$).
   - LineStrings: `projected_geom.length` -> Meters ($m$).
   - Points: `measurement = null` with message.
8. **Persistence**: Saves file summary (`status="COMPLETED"`) and feature measurements in database.

---

## 🗺️ 7. CRS Strategy

> **CRITICAL RULE**: Never calculate area or length directly from geographic coordinates (`EPSG:4326`). Latitude and longitude are angular coordinates (degrees) and vary in physical length across latitudes.

### Workflow:
1. **Detect Original CRS**: Identifies input CRS (e.g. `EPSG:4326` or missing). Missing CRS defaults to `EPSG:4326` with explicit log warnings.
2. **Identify Projected Status**: If input CRS is already a metric projected CRS, keep existing projection.
3. **UTM Zone Calculation**: For geographic coordinates, compute UTM Zone:
   $$\text{Zone} = \lfloor \frac{\text{Longitude} + 180}{6} \rfloor + 1$$
   $$\text{EPSG Code} = \begin{cases} 32600 + \text{Zone} & \text{Northern Hemisphere} \\ 32700 + \text{Zone} & \text{Southern Hemisphere} \end{cases}$$
4. **Transform & Measure**: Reproject geometry to metric UTM coordinates using PyProj before calculating area or length.

---

## 📏 8. Measurement Logic

- **Polygon / MultiPolygon**:
  - Measurement Type: `area_sq_m`
  - Units: Square meters ($m^2$)
- **LineString / MultiLineString**:
  - Measurement Type: `length_m`
  - Units: Meters ($m$)
- **Point / MultiPoint**:
  - Measurement Type: `none`
  - Value: `null`
  - Message: `"No measurement required for Point geometry"`
- **Unsupported Geometries**:
  - Measurement Type: `unsupported`
  - Value: `null`
  - Status: `UNSUPPORTED`

---

## 🔒 9. Security Features

- **Zip Slip Prevention**: Validates every member path in uploaded ZIP archives against target extraction directory using canonical path resolution.
- **Strict File Type Verification**: Validates file extension, magic headers, and disallows execution of unapproved file formats.
- **Centralized Exception Handling**: Sanitizes external error messages to prevent leakage of filesystem paths, internal stack traces, or SQL queries.

---

## 📡 10. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | System health check and DB status |
| `POST` | `/api/files/` | Upload and process KML / Shapefile ZIP |
| `GET` | `/api/files/{id}/` | Get file metadata and processing status |
| `GET` | `/api/files/{id}/measurements/` | Get feature measurements for file |

---

## 💻 11. Local Setup Instructions

### 1. Clone Repository & Setup Virtual Environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate Sample Data
```bash
python scripts/generate_sample_data.py
```

### 4. Run Application
```bash
uvicorn app.main:app --reload --port 8000
```
Access Swagger UI documentation at: `http://localhost:8000/docs`

---

## 🐳 12. Docker Setup

### Run with Docker Compose (PostgreSQL / PostGIS + FastAPI)
```bash
docker compose up --build
```
The API will be available at `http://localhost:8000`.

---

## 🧪 13. Running Tests

Run the full automated test suite with 28 tests:
```bash
python -m pytest -v
```

---

## 📝 14. License
MIT License. Created for technical interview assignment.

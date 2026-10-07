BUILD THIS COMPLETE PROJECT

You are a senior Python Backend Engineer and Geospatial Engineer.

Build a complete, working, production-quality backend project for this hiring assignment.

PROJECT NAME:
Geospatial File Measurement API

GOAL:
Create a FastAPI backend that accepts KML files and ZIP files containing Shapefiles, processes their geospatial features, correctly handles CRS, calculates measurements, stores processing information, and exposes REST APIs.

IMPORTANT:
Do not only explain the solution.
Actually CREATE and IMPLEMENT the project files in the workspace.

Do not use fake/mock implementations.
Do not leave TODOs for required features.
Do not ask unnecessary questions.
Make reasonable engineering decisions yourself.

==================================================
TECH STACK
==================================================

Use:

- Python 3.12+
- FastAPI
- Uvicorn
- Pydantic
- GeoPandas
- Shapely
- PyProj
- Fiona / appropriate GeoPandas engine
- PostgreSQL
- SQLAlchemy
- Alembic
- Pytest
- HTTPX
- Docker
- Docker Compose

Use type hints and clean Python code.

==================================================
REQUIRED INPUT FILES
==================================================

Accept:

1. .kml
2. .zip containing a Shapefile

Validate ZIP files and ensure the required Shapefile components are present where applicable:

- .shp
- .shx
- .dbf
- .prj

Do not blindly trust uploaded files.

==================================================
REQUIRED API
==================================================

Implement:

POST /api/files/

Uploads and processes a geospatial file.

GET /api/files/{id}/

Returns information about the uploaded file.

GET /api/files/{id}/measurements/

Returns measurements for every feature.

Example file response:

{
    "id": "uuid",
    "filename": "survey.kml",
    "feature_count": 120,
    "crs": "EPSG:4326",
    "status": "COMPLETED"
}

Possible status values:

PROCESSING
COMPLETED
FAILED

==================================================
FEATURE PROCESSING
==================================================

For every feature identify:

- Feature ID/index
- Geometry type
- Geometry
- CRS
- Properties/attributes

Support:

- Point
- MultiPoint
- LineString
- MultiLineString
- Polygon
- MultiPolygon
- GeometryCollection

Do not crash if a geometry type is unsupported.

==================================================
MEASUREMENTS
==================================================

Polygon / MultiPolygon:

Calculate area.

Return area in:

square meters

LineString / MultiLineString:

Calculate length.

Return length in:

meters

Point / MultiPoint:

No measurement required.

Unsupported geometry:

Return null measurement and an explanation.

Example:

{
    "feature_id": 5,
    "geometry_type": "Point",
    "measurement": null,
    "message": "No measurement required for Point geometry"
}

==================================================
CRS — VERY IMPORTANT
==================================================

NEVER calculate area or length directly from geographic coordinates such as:

EPSG:4326

Latitude/longitude are angular coordinates and must not be treated as meters.

Implement this workflow:

Input CRS
→ determine whether CRS is geographic
→ select suitable projected CRS
→ transform geometry
→ calculate measurement
→ return metric measurement

Use a sensible automatic projected CRS strategy.

Prefer a suitable UTM/local projected CRS based on the geometry's location where appropriate.

Do NOT hardcode one projected CRS for all files.

If the input is already projected:

- verify the units
- use an appropriate metric CRS

If CRS is missing:

- handle it explicitly
- do not silently invent a CRS

Document the CRS strategy in README.md.

==================================================
INVALID GEOMETRIES
==================================================

Detect invalid geometries.

Where appropriate, safely attempt geometry repair.

If repair succeeds:
continue processing.

If repair fails:
do not crash the entire file unnecessarily.

Return useful feature-level error information.

Handle:

- empty geometry
- null geometry
- invalid geometry
- mixed geometry types

==================================================
FILE VALIDATION
==================================================

Implement:

- extension validation
- content validation where practical
- file size limit
- empty-file detection
- corrupted file handling
- invalid KML handling
- invalid ZIP handling
- missing Shapefile components
- unsupported formats

Use appropriate HTTP status codes.

Do not expose stack traces to clients.

==================================================
ZIP SECURITY
==================================================

Secure ZIP extraction.

Prevent:

- Zip Slip
- path traversal
- absolute paths
- extraction outside the temporary directory
- dangerous/unexpected files

Only extract the required geospatial files.

Clean up temporary files after processing.

==================================================
DATABASE
==================================================

Use PostgreSQL + SQLAlchemy + Alembic.

Use UUID for public file IDs.

Store at minimum:

- id
- filename
- file type
- stored file path if required
- CRS
- feature count
- status
- error message
- created_at
- updated_at

Use proper database transactions.

==================================================
ARCHITECTURE
==================================================

Use clean layered architecture.

Do not put all logic inside FastAPI routes.

Recommended structure:

app/
    main.py

    api/
        routes/
            files.py

    core/
        config.py
        logging.py

    db/
        database.py
        models.py
        session.py

    schemas/
        file.py
        measurement.py

    services/
        file_service.py
        geospatial_service.py
        measurement_service.py
        crs_service.py

    repositories/
        file_repository.py

    utils/
        file_validation.py
        zip_utils.py

    exceptions/
        custom_exceptions.py
        handlers.py

tests/

scripts/

sample_data/

Also create:

Dockerfile
docker-compose.yml
.env.example
.gitignore
requirements.txt
alembic.ini
README.md

You may modify the structure if there is a strong engineering reason.

==================================================
PROCESSING FLOW
==================================================

Implement:

Upload
→ Validate
→ Secure temporary storage
→ Read KML/Shapefile
→ Extract features
→ Validate geometry
→ Detect CRS
→ Transform CRS
→ Calculate measurements
→ Store results
→ Set status
→ Return result

Status:

PROCESSING
→ COMPLETED

or:

PROCESSING
→ FAILED

Keep the design ready for future background processing.

Do not add Celery/Redis unless genuinely necessary.

==================================================
ERROR HANDLING
==================================================

Create centralized exception handling.

Use meaningful HTTP responses.

Examples:

400 invalid input
404 file not found
413 file too large
422 validation error
500 unexpected processing error

Do not expose:

- stack traces
- filesystem paths
- SQL errors
- secrets

Log technical details internally.

==================================================
LOGGING
==================================================

Add clean application logging.

Log important events:

- upload received
- validation
- processing started
- CRS detected
- CRS transformed
- measurement completed
- processing failed

Do not log sensitive information.

==================================================
TESTING
==================================================

Use Pytest.

Create tests for:

- valid KML
- valid Shapefile ZIP
- invalid extension
- empty file
- corrupted ZIP
- missing Shapefile components
- invalid KML
- EPSG:4326
- projected CRS
- Polygon area
- MultiPolygon area
- LineString length
- MultiLineString length
- Point
- unsupported geometry
- invalid geometry
- missing CRS
- file not found
- measurement endpoint
- ZIP path traversal attack

Use test fixtures and temporary directories.

==================================================
SAMPLE DATA
==================================================

Create:

scripts/generate_sample_data.py

Generate simple sample geospatial data containing:

- Point
- LineString
- Polygon

Use EPSG:4326.

Create sample files where practical.

==================================================
DOCKER
==================================================

Create:

Dockerfile
docker-compose.yml

Docker Compose should run:

- FastAPI
- PostgreSQL/PostGIS

Use environment variables.

Never hardcode database passwords.

The project should run with:

docker compose up --build

==================================================
ENVIRONMENT
==================================================

Create:

.env.example

Include:

DATABASE_URL=
MAX_FILE_SIZE=
UPLOAD_DIRECTORY=
ENVIRONMENT=
LOG_LEVEL=

.gitignore should include:

.env
__pycache__/
.pytest_cache/
uploads/
.venv/
temporary files

==================================================
README
==================================================

Create a professional README.md.

Include:

1. Project overview
2. Features
3. Tech stack
4. Architecture
5. Folder structure
6. File processing flow
7. CRS strategy
8. Measurement logic
9. Security
10. API documentation
11. Request examples
12. Response examples
13. Local setup
14. Docker setup
15. Database migration
16. Testing
17. Swagger
18. Design decisions
19. Learning
20. Future scope

Swagger:

/docs

ReDoc:

/redoc

Learning section should mention:

- FastAPI
- GeoPandas
- Shapely
- PyProj
- CRS
- PostgreSQL
- API design
- file security
- testing
- Docker

Future scope can mention:

- Celery/Redis
- cloud storage
- authentication
- rate limiting
- additional geospatial formats
- advanced spatial analysis
- PostGIS spatial queries
- monitoring
- horizontal scaling

Do not claim future features are already implemented.

==================================================
CODE QUALITY
==================================================

Follow:

- PEP 8
- type hints
- clean naming
- single responsibility
- small functions
- dependency injection
- service layer
- repository layer
- centralized exceptions
- meaningful docstrings
- useful comments only

Avoid:

- duplicated code
- giant files
- hardcoded paths
- hardcoded secrets
- unnecessary abstractions
- fake calculations
- TODO placeholders
- business logic inside routes

==================================================
PERFORMANCE
==================================================

Consider reasonably large files.

Use temporary storage safely.

Avoid unnecessary duplicate file loading.

Set reasonable file-size limits.

Clean temporary files.

Keep architecture extensible for asynchronous processing.

==================================================
IMPLEMENTATION STRATEGY
==================================================

Build the project in these phases.

PHASE 1:
Project foundation.

Create:

- FastAPI app
- configuration
- database connection
- SQLAlchemy models
- Alembic
- logging
- exception handling
- health endpoint

PHASE 2:
File upload and validation.

Implement:

POST /api/files/

Include:

- KML
- ZIP Shapefile
- validation
- secure extraction
- database record
- processing status

PHASE 3:
Geospatial processing.

Implement:

- GeoPandas reading
- feature extraction
- geometry detection
- properties
- geometry validation

PHASE 4:
CRS and measurements.

Implement:

- CRS detection
- projected CRS selection
- CRS transformation
- polygon area
- line length
- point handling
- unsupported geometry handling

PHASE 5:
Remaining APIs.

Implement:

GET /api/files/{id}/

GET /api/files/{id}/measurements/

Add response models.

PHASE 6:
Testing and hardening.

Implement and verify all tests.

Review:

- security
- validation
- errors
- logging
- cleanup
- performance
- code quality

PHASE 7:
Docker and documentation.

Create:

- Dockerfile
- docker-compose.yml
- README.md
- .env.example
- final migrations

PHASE 8:
Final audit.

Compare the finished project against EVERY requirement in this prompt.

Fix missing or broken functionality.

==================================================
IMPORTANT AGENT RULES
==================================================

Do not generate the entire project in one enormous response.

Work directly on files if your environment supports file editing.

After each phase:

1. Check imports.
2. Check file references.
3. Run tests that are available.
4. Fix errors.
5. Continue to the next phase.

Do not claim tests passed unless they actually ran.

Do not claim Docker works unless verified.

Do not claim a feature is implemented unless it actually exists.

Do not stop after creating only the architecture.

The final goal is a complete working project.

==================================================
FINAL VERIFICATION
==================================================

Before finishing, verify:

[ ] FastAPI starts
[ ] PostgreSQL connection works
[ ] Alembic works
[ ] POST /api/files/ works
[ ] GET /api/files/{id}/ works
[ ] GET /api/files/{id}/measurements/ works
[ ] KML processing works
[ ] Shapefile ZIP processing works
[ ] Polygon area works
[ ] MultiPolygon area works
[ ] LineString length works
[ ] MultiLineString length works
[ ] Point handling works
[ ] Unsupported geometry does not crash
[ ] EPSG:4326 is transformed before measurement
[ ] Projected CRS works
[ ] Missing CRS is handled
[ ] Invalid geometry is handled
[ ] ZIP path traversal is blocked
[ ] File-size validation exists
[ ] Error handling works
[ ] Tests exist and pass
[ ] Docker files work
[ ] README is complete
[ ] .env.example exists
[ ] .gitignore exists

Create a final audit table:

Requirement | Status | File/Implementation

Only mark a requirement complete if it is actually implemented.

==================================================
FINAL OUTPUT
==================================================

When everything is complete, provide:

1. Final project structure
2. Setup commands
3. Docker commands
4. Migration commands
5. Test commands
6. curl API examples
7. Example responses
8. Swagger location
9. GitHub publishing instructions
10. Five resume bullet points
11. Two-minute interview explanation
12. Fifteen technical interview questions and answers
13. Final requirement audit
14. Known limitations
15. Future scope

START NOW.

First create the project foundation and continue through all phases until the complete project is implemented and verified.
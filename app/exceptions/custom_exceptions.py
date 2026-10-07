class GeospatialAPIException(Exception):
    """Base exception for Geospatial API."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class InvalidFileFormatException(GeospatialAPIException):
    def __init__(self, message: str = "Invalid or unsupported file format"):
        super().__init__(message=message, status_code=400)


class FileTooLargeException(GeospatialAPIException):
    def __init__(self, message: str = "File size exceeds maximum allowed limit"):
        super().__init__(message=message, status_code=413)


class FileCorruptedException(GeospatialAPIException):
    def __init__(self, message: str = "Uploaded file is corrupted or unreadable"):
        super().__init__(message=message, status_code=400)


class ZipSecurityException(GeospatialAPIException):
    def __init__(self, message: str = "Zip file contains suspicious or forbidden path components"):
        super().__init__(message=message, status_code=400)


class MissingShapefileComponentException(GeospatialAPIException):
    def __init__(self, message: str = "Shapefile zip archive is missing required files (.shp, .shx, .dbf, .prj)"):
        super().__init__(message=message, status_code=400)


class ResourceNotFoundException(GeospatialAPIException):
    def __init__(self, message: str = "Requested resource was not found"):
        super().__init__(message=message, status_code=404)


class GeospatialProcessingException(GeospatialAPIException):
    def __init__(self, message: str = "Failed to process geospatial feature geometry"):
        super().__init__(message=message, status_code=422)

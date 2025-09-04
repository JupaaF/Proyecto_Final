class FileHandlerError(Exception):
    """Base exception for errors in the file_handler module."""
    pass

class TemplateError(FileHandlerError):
    """Raised for errors related to template processing."""
    pass

class ParameterError(FileHandlerError):
    """Raised for errors related to parameter manipulation."""
    pass

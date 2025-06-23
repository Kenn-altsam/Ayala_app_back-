class AppException(Exception):
    """Base application exception"""
    
    def __init__(self, message: str, status_code: int = 400, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class DatabaseException(AppException):
    """Database related exceptions"""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=500, error_code="DATABASE_ERROR")


class AuthenticationException(AppException):
    """Authentication related exceptions"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401, error_code="AUTH_ERROR")


class AuthorizationException(AppException):
    """Authorization related exceptions"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status_code=403, error_code="ACCESS_DENIED")


class ValidationException(AppException):
    """Validation related exceptions"""
    
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=400, error_code="VALIDATION_ERROR")


class NotFoundException(AppException):
    """Resource not found exceptions"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404, error_code="NOT_FOUND")


class CacheException(AppException):
    """Cache related exceptions"""
    
    def __init__(self, message: str = "Cache operation failed"):
        super().__init__(message, status_code=500, error_code="CACHE_ERROR") 
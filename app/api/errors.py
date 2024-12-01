from werkzeug.exceptions import HTTPException
from app.api import bp
from flask import jsonify
import datetime


class BaseCustomHTTPException(HTTPException):
    """Base class for all custom HTTP exceptions."""

    description = "An error occurred"

    def __init__(self, message=None, errors=None):
        # If a message is provided, use it; otherwise, use the default description
        super().__init__(description=message or self.description)
        self.errors = errors or {}

    @property
    def name(self):
        """Use the class name as the error name."""
        return self.__class__.__name__

    def to_dict(self):
        """Convert error to dictionary for response."""
        return {
            "status": "error",
            "statusCode": self.code,
            "error": {
                "code": self.name,
                "message": self.description,
                "fields": self.errors,
                "timestamp": datetime.datetime.now(),
            },
        }


class ValidationError(BaseCustomHTTPException):
    """Raised when a validation error occurs."""

    description = "Validation error occurred"
    code = 400


class AuthenticationError(BaseCustomHTTPException):
    """Raised when authentication fails."""

    description = "Authentication error occurred"
    code = 401


@bp.errorhandler(BaseCustomHTTPException)
def handle_custom_error(e):
    return jsonify(e.to_dict()), e.code


@bp.errorhandler(HTTPException)
def handle_http_exception(e):
    response = {
        "status": "error",
        "statusCode": e.code,
        "error": {
            "code": e.name,
            "message": e.description or "",
            "timestamp": datetime.datetime.now(),
        },
    }
    return jsonify(response), e.code


@bp.errorhandler(Exception)
def handle_generic_exception(e):
    response = {
        "status": "error",
        "statusCode": 500,
        "error": {
            "code": "Internal Server Error",
            "timestamp": datetime.datetime.now(),
        },
    }
    return jsonify(response), 500
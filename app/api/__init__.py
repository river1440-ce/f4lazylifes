from flask import Blueprint

bp = Blueprint("api_v1", __name__)

from app.api import auth, errors  # noqa: E402, F401

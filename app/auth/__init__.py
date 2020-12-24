from flask import Blueprint

bp = Blueprint('auth', __name__)
db = Blueprint('auth1', __name__)
mail = Blueprint('auth2', __name__)
bcrypt = Blueprint('auth3', __name__)

from app.auth import routes

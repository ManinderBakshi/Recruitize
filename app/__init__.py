from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_jwt_extended import JWTManager
from flask_mail import Mail



app = Flask(__name__)

app.config.from_object(Config)
bcrypt = Bcrypt(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
blacklist = set()


login = LoginManager(app)
login.login_view = 'auth.login'
bootstrap = Bootstrap(app)

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'recruitize.dei@gmail.com'
app.config['MAIL_PASSWORD'] = 'recruitize@vsrvsm'
mail = Mail(app)


from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from app.auth import bp as auth_bp
app.register_blueprint(auth_bp)

from app.main import bp as main_bp
app.register_blueprint(main_bp)

from app.api import bp as api_bp
app.register_blueprint(api_bp)

from app import model

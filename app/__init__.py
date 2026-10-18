from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config


def create_app():
    app = Flask(__name__, static_folder='../web', static_url_path='')
    app.config.from_object(Config)

    CORS(app)
    JWTManager(app)

    from app.models import db
    db.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.business import business_bp
    from app.routes.user import user_bp
    from app.routes.merchant import merchant_bp
    from app.routes.platform import platform_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(business_bp, url_prefix='/api/businesses')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(merchant_bp, url_prefix='/api/merchant')
    app.register_blueprint(platform_bp, url_prefix='/api/platform')

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    return app
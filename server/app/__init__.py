from flask import Flask
from app.config import Config
from app.extensions import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация расширений
    db.init_app(app)

    # Регистрация Blueprints (маршрутов)
    from app.routes.auth import auth_bp
    from app.routes.vault import vault_bp

    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(vault_bp, url_prefix='/api/v1/vault')

    return app
from flask import Flask
from flask_cors import CORS

from config.app_config import AppConfig


def create_app(mode):
    """Crea la aplicación Flask a ejecutar de acuerdo a una configuración especificada
    :param mode: mode de ejecución del APP
    :type mode: str
    """

    app_config_object = AppConfig(mode)

    app = Flask(__name__)
    app.config.from_object(app_config_object)
    CORS(app)

    from views import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

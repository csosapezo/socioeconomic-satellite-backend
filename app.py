from flask import Flask
from flask_cors import CORS


def create_app(config_filename):
    """Crea la aplicación Flask a ejecutar de acuerdo a una configuración especificada
    :param config_filename: dirección de la configuración
    :type config_filename: str
    """
    app = Flask(__name__)
    app.config.from_object(config_filename)
    CORS(app)

    from views import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

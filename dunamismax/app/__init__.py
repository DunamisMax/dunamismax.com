from flask import Flask
import logging


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    if not app.debug:
        gunicorn_error_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_error_logger.handlers
        app.logger.setLevel(logging.INFO)

    # Register blueprints or routes here
    with app.app_context():
        from .routes import bp

        app.register_blueprint(bp)

    return app

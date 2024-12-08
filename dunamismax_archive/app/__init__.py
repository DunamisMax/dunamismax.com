from flask import Flask
from flask_wtf.csrf import CSRFProtect
import logging
import time

csrf = CSRFProtect()  # Instantiate CSRFProtect


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    csrf.init_app(app)  # Initialize CSRF protection with the app

    app.jinja_env.globals["time"] = time.time  # Add `time` to Jinja globals

    if not app.debug:
        gunicorn_error_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_error_logger.handlers
        app.logger.setLevel(logging.INFO)

    # Register blueprints
    with app.app_context():
        from .routes import bp

        app.register_blueprint(bp)

    return app

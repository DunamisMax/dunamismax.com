from app import create_app
import logging

app = create_app()

if not app.debug:
    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_error_logger.handlers
    app.logger.setLevel(logging.INFO)

if __name__ == "__main__":
    app.run(debug=True)

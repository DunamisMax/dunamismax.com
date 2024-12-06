from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Register blueprints or routes here
    with app.app_context():
        from .routes import bp

        app.register_blueprint(bp)

    return app

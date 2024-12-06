import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default-key")
    DEBUG = os.getenv("FLASK_ENV") == "development"


config = Config()

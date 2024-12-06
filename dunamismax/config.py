import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default-key-if-missing")
    DEBUG = os.getenv("FLASK_ENV") == "development"


config = Config()

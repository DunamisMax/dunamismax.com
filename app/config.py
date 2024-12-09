import os
from dotenv import load_dotenv

load_dotenv()  # This will load variables from .env into the environment

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

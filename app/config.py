import os
from dotenv import load_dotenv

load_dotenv()  # This will load variables from .env into the environment

SECRET_KEY = os.getenv("SECRET_KEY")

import secrets
from os import environ
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = secrets.token_hex()
SQLALCHEMY_DATABASE_URI = environ['SQLALCHEMY_DATABASE_URI']
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_PATH = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_PATH, exist_ok=True)


class Config:
    SECRET_KEY = "trekking-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(INSTANCE_PATH, "database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
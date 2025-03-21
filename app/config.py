import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://root:admin@localhost/ecommerce")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
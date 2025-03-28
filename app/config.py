import os

class Config:
    # configuração banaco relacional
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://root:admin@localhost/ecommerce")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # configuração banco Nosql
    AZURE_COSMOS_URI = "https://localhost:8081"
    AZURE_COSMOS_KEY = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
    AZURE_COSMOS_DATABASE = "ibmec-cloud-mall-products"
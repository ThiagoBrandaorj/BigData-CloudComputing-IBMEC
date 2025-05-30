import os

class Config:
    #SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://root:admin@localhost/ecommerce")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://grupo:administrador99*@ibmec-cloud-ecommerce-gr.mysql.database.azure.com/ecommerce?ssl_verify_cert=false")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #AZURE_COSMOS_URI = "https://localhost:8081"
    #AZURE_COSMOS_KEY = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
    #AZURE_COSMOS_DATABASE = "ecommerce-produtos"
    AZURE_COSMOS_URI = "https://ibmec-cloud-ecommerce-35625.documents.azure.com:443/"
    AZURE_COSMOS_KEY = "nOMr6CyGGmaFiCEVHHPXqEbRk8LuaaQW24TQIxe41OnuDJetd1wQvP2ONw4UgYAK0F9rkVCpKRcVACDb1AMpsg=="
    AZURE_COSMOS_DATABASE = "ecommerce-produtos"
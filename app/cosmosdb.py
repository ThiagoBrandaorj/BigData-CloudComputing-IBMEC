import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from azure.cosmos import CosmosClient
from app.config import Config

# Criar o cliente do Cosmos DB
client = CosmosClient(Config.AZURE_COSMOS_URI, credential=Config.AZURE_COSMOS_KEY)

# Acessar o banco de dados
database = client.get_database_client(Config.AZURE_COSMOS_DATABASE)

# Criar um container (tabela) chamado "produtos"
container_name = "produtos"
container = database.get_container_client(container_name)
import requests
import json
from urllib.parse import quote
from config import DefaultConfig

CONFIG = DefaultConfig()

class ProductAPI:
    def consultar_produtos(self, product_name):
        try:
            # Fazer URL encoding do nome do produto para tratar espaços e acentos
            encoded_name = quote(product_name, safe='')
            url = f"{CONFIG.API_BASE_URL}/produto/nome/{encoded_name}"
            print(f"Consultando API: {url}")
            
            # Adicionar headers apropriados
            headers = {
                'User-Agent': 'IBMEC-Bot/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Resposta da API: {json.dumps(result, indent=2)}")
                return result
            else:
                print(f"Erro na API: {response.text}")
                return None
        except Exception as e:
            print(f"Exceção ao consultar a API de Produtos: {e}")
            return None

    def consultar_produto_por_id(self, product_id):
        try:
            url = f"{CONFIG.API_BASE_URL}/produto/{product_id}"
            print(f"Consultando produto por ID: {url}")
            
            # Adicionar headers apropriados
            headers = {
                'User-Agent': 'IBMEC-Bot/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Produto encontrado: {json.dumps(result, indent=2)}")
                return result
            else:
                print(f"Erro na API: {response.text}")
                return None
        except Exception as e:
            print(f"Exceção ao consultar produto por ID: {e}")
            return None

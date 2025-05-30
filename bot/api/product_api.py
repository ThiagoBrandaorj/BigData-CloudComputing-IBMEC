import requests
import json
from config import DefaultConfig

CONFIG = DefaultConfig()

class ProductAPI:
    def consultar_produtos(self, product_name):
        try:
            url = f"{CONFIG.API_BASE_URL}/produto/nome/{product_name}"
            print(f"Consultando API: {url}")
            
            response = requests.get(url)
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
            
            response = requests.get(url)
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

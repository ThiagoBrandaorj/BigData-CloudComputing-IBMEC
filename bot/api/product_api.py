import requests
import json

class ProductAPI:
    def consultar_produtos(self, product_name):
        try:
            url = f"http://localhost:8000/produto/nome/{product_name}"
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

import requests
import json

class OrderAPI:
    def consultar_pedidos_por_usuario(self, nome_cliente):
        try:
            url = f"http://localhost:8000/pedido/nome/{nome_cliente}"
            print(f"Consultando API: {url}")
            
            response = requests.get(url)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Resposta da API: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return result
            else:
                print(f"Erro na API: {response.text}")
                return None
        except Exception as e:
            print(f"Exceção ao consultar a API de Pedidos: {e}")
            return None
import requests
import json
from config import DefaultConfig

CONFIG = DefaultConfig()

class CartaoAPI():
    def consultar_cartao_por_numero(self,card_number):
        try:
            url = f"{CONFIG.API_BASE_URL}/cartao/numero/{card_number}"

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
                print(f"Cartão encontrado...")
                return result
            else:
                print(f"Erro na API: {response.text}")
                return None
            
        except Exception as e:
            print(f"Exceção ao consultar cartão pelo número: {e}")
            return None
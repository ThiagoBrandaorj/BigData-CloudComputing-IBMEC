import requests
import json
import re
from config import DefaultConfig

CONFIG = DefaultConfig()

class UsuarioAPI():
    def buscar_usuario_por_cpf(self, cpf):
        """
        Busca usuário por CPF
        """
        try:
            # Limpar CPF (remover pontos, traços e espaços)
            cpf_limpo = re.sub(r'[^\d]', '', cpf)
            
            url = f"{CONFIG.API_BASE_URL}/usuario"
            
            headers = {
                'User-Agent': 'IBMEC-Bot/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            print(f"Status code busca usuários: {response.status_code}")
            
            if response.status_code == 200:
                usuarios = response.json()
                
                # Buscar usuário com CPF correspondente
                for usuario in usuarios:
                    usuario_cpf = usuario.get('cpf', '')
                    if usuario_cpf:
                        # Limpar CPF do usuário também
                        usuario_cpf_limpo = re.sub(r'[^\d]', '', usuario_cpf)
                        if usuario_cpf_limpo == cpf_limpo:
                            print(f"Usuário encontrado por CPF: {usuario.get('nome')}")
                            return usuario
                
                print(f"Nenhum usuário encontrado com CPF: {cpf}")
                return None
            else:
                print(f"Erro ao buscar usuários: {response.text}")
                return None
                
        except Exception as e:
            print(f"Exceção ao buscar usuário por CPF: {e}")
            return None
    
    def buscar_usuario_por_id(self, usuario_id):
        """
        Busca usuário por ID
        """
        try:
            url = f"{CONFIG.API_BASE_URL}/usuario/{usuario_id}"
            
            headers = {
                'User-Agent': 'IBMEC-Bot/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            print(f"Status code busca usuário por ID: {response.status_code}")
            
            if response.status_code == 200:
                usuario = response.json()
                print(f"Usuário encontrado: {usuario.get('nome')}")
                return usuario
            else:
                print(f"Erro ao buscar usuário por ID: {response.text}")
                return None
                
        except Exception as e:
            print(f"Exceção ao buscar usuário por ID: {e}")
            return None

    def validar_cpf(self, cpf):
        """
        Valida formato do CPF (apenas formato, não algoritmo)
        """
        # Remove caracteres não numéricos
        cpf_limpo = re.sub(r'[^\d]', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf_limpo) != 11:
            return False
        
        # Verifica se não são todos iguais (ex: 11111111111)
        if cpf_limpo == cpf_limpo[0] * 11:
            return False
            
        return True 
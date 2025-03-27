from pydantic import BaseModel
from datetime import datetime

class TransacaoRequest(BaseModel):
    numero: str  # Número do cartão (16 dígitos)
    dt_expiracao: str  # Data de expiração no formato datetime
    cvv: str  # CVV pode ter 3 ou 4 dígitos
    valor: float  # Valor da transação
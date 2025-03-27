from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

class TransacaoResponse(BaseModel):
    status: str  # "AUTHORIZED" ou "NOT_AUTHORIZED"
    codigo_autorizacao: Optional[UUID] = None  # Código único de autorização
    dt_transacao: datetime  # Data e hora da transação
    message: str  # Mensagem explicativa
from app.database import db

class Cartao(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    numero = db.Column(db.String(16), nullable=False)
    nome_impresso = db.Column(db.String(100), nullable=False)
    validade = db.Column(db.DateTime, nullable=False)
    cvv = db.Column(db.String(4), nullable=False)
    bandeira = db.Column(db.String(20), nullable=False)
    tipo = db.Column(db.String(50))
    saldo = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    
    criado_em = db.Column(db.DateTime, default=db.func.current_timestamp())
    atualizado_em = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    usuario = db.relationship("Usuario", back_populates="cartoes")

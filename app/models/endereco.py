from app.database import db

class Endereco(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    logradouro = db.Column(db.String(150), nullable=False)
    complemento = db.Column(db.String(100))
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    uf = db.Column(db.String(2), nullable=False)
    cep = db.Column(db.String(8), nullable=False)
    pais = db.Column(db.String(50), default="Brasil", nullable=False)
    tipo = db.Column(db.String(50))
    
    criado_em = db.Column(db.DateTime, default=db.func.current_timestamp())
    atualizado_em = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    usuario = db.relationship("Usuario", back_populates="enderecos")
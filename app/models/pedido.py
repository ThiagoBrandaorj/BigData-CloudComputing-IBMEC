from app.database import db

class Pedido(db.Model):
    id_pedido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_cliente = db.Column(db.String(50), nullable=False)
    data_pedido = db.Column(db.Date, nullable=False)
    nome_produto = db.Column(db.String(100), nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    criado_em = db.Column(db.DateTime, default=db.func.current_timestamp())
    atualizado_em = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    usuario = db.relationship("Usuario", back_populates="pedidos", lazy=True)
from flask import Blueprint, request, jsonify
from app.database import db
from app.models.pedido import Pedido
from datetime import datetime
from app.models.usuario import Usuario

pedido_bp = Blueprint("pedido", __name__)

# Buscar todos os pedidos
@pedido_bp.route("/", methods=["GET"])
def listar_pedidos():
    pedidos = Pedido.query.all()
    return jsonify([
        {
            "id": p.id_pedido,
            "cliente": p.nome_cliente,
            "produto": p.nome_produto,
            "data": p.data_pedido.strftime("%d/%m/%Y"),
            "valor": p.valor_total,
            "status": p.status
        } for p in pedidos
    ])

# Buscar pedidos por ID
@pedido_bp.route("/<int:id_pedido>", methods=["GET"])
def buscar_pedido_por_id(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)

    return jsonify({
        "id": pedido.id_pedido,
        "cliente": pedido.nome_cliente,
        "produto": pedido.nome_produto,
        "data": pedido.data_pedido.strftime("%d/%m/%Y"),
        "valor": pedido.valor_total,
        "status": pedido.status
    })

# Buscar pedidos de um cliente
@pedido_bp.route("/nome/<string:nome_cliente>", methods=["GET"])
def listar_pedidos_por_nome(nome_cliente):
    pedidos = Pedido.query.filter(
        Pedido.nome_cliente == nome_cliente
    ).all()

    return jsonify([
        {
            "id": p.id_pedido,
            "cliente": p.nome_cliente,
            "produto": p.nome_produto,
            "data": p.data_pedido.strftime("%d/%m/%Y"),
            "valor": p.valor_total,
            "status": p.status
        } for p in pedidos
    ])

# Criar um pedido
@pedido_bp.route("/", methods=["POST"])
def criar_pedido():
    dados = request.json
    # Obriga que os campos de nome de cliente, nome do produto e valor total do pedido necessariamente estejam escritos
    if not dados.get("nome_cliente") or not dados.get("nome_produto") or not dados.get("valor_total"):
        return jsonify({"erro": "Nome do cliente, nome dos produtos, preço e data da compra são obrigatórios"}), 400
    usuario = Usuario.query.filter(Usuario.nome.ilike(dados["nome_cliente"])).first()
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado para o nome fornecido"}), 404

    novo_pedido = Pedido(
        nome_cliente=dados["nome_cliente"],
        data_pedido=datetime.strptime(dados["data_pedido"], "%Y-%m-%d"),
        nome_produto=dados["nome_produto"],
        valor_total=dados["valor_total"],
        status=dados["status"],
        id_usuario=usuario.id
    )

    db.session.add(novo_pedido)
    db.session.commit()
    return jsonify({"mensagem": "Pedido criado com sucesso", "id_pedido": novo_pedido.id_pedido}), 201

# Atualizar um pedido
@pedido_bp.route("/<int:id_pedido>", methods=["PUT"])
def atualizar_pedido(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    data = request.json

    pedido.nome_cliente = data.get("nome_cliente", pedido.nome_cliente)
    pedido.data_pedido = datetime.strptime(data["data_pedido"], "%Y-%m-%d")
    pedido.nome_produto = data.get("nome_produto", pedido.nome_produto)
    pedido.valor_total = data.get("valor_total", pedido.valor_total)
    pedido.status = data.get("status", pedido.status)

    db.session.commit()
    return jsonify({"mensagem": "Pedido atualizado"})

# Deletar um pedido
@pedido_bp.route("/<int:id_pedido>", methods=["DELETE"])
def deletar_pedido(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    db.session.delete(pedido)
    db.session.commit()
    return jsonify({"mensagem": "Pedido deletado"})

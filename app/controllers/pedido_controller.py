from flask import Blueprint, request, jsonify
from app.database import db
from app.models.pedido import Pedido
from datetime import datetime
from app.models.usuario import Usuario
from app.models.cartao import Cartao
import requests
import os

pedido_bp = Blueprint("pedido", __name__)

def buscar_nome_produto(id_produto):
    """Busca o nome do produto via API do CosmosDB"""
    try:
        api_base_url = os.environ.get('API_BASE_URL', 'https://ibmec-ecommerce-produtos-thpedu-hpgdamgyc3c4grgx.centralus-01.azurewebsites.net')
        url = f"{api_base_url}/produto/{id_produto}"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            produto = response.json()
            return produto.get('nome', f'Produto ID: {id_produto}')
        else:
            return f'Produto ID: {id_produto}'
    except:
        return f'Produto ID: {id_produto}'

# Buscar todos os pedidos
@pedido_bp.route("/", methods=["GET"])
def listar_pedidos():
    pedidos = Pedido.query.join(Usuario).all()
    resultado = []
    
    for p in pedidos:
        nome_produto = buscar_nome_produto(p.id_produto)
        resultado.append({
            "id": p.id_pedido,
            "cliente": p.usuario.nome,  # Nome via relacionamento
            "produto": nome_produto,
            "id_produto": p.id_produto,
            "id_cartao": p.id_cartao,
            "id_usuario": p.id_usuario,
            "data": p.data_pedido.strftime("%d/%m/%Y"),
            "valor": p.valor_total,
            "status": p.status
        })
    
    return jsonify(resultado)

# Buscar pedidos por ID
@pedido_bp.route("/<int:id_pedido>", methods=["GET"])
def buscar_pedido_por_id(id_pedido):
    pedido = Pedido.query.join(Usuario).filter(Pedido.id_pedido == id_pedido).first_or_404()
    nome_produto = buscar_nome_produto(pedido.id_produto)

    return jsonify({
        "id": pedido.id_pedido,
        "cliente": pedido.usuario.nome,  # Nome via relacionamento
        "produto": nome_produto,
        "id_produto": pedido.id_produto,
        "id_cartao": pedido.id_cartao,
        "id_usuario": pedido.id_usuario,
        "data": pedido.data_pedido.strftime("%d/%m/%Y"),
        "valor": pedido.valor_total,
        "status": pedido.status
    })

# Buscar pedidos de um cliente por nome
@pedido_bp.route("/nome/<string:nome_cliente>", methods=["GET"])
def listar_pedidos_por_nome(nome_cliente):
    pedidos = Pedido.query.join(Usuario).filter(
        Usuario.nome.ilike(f"%{nome_cliente}%")
    ).all()

    resultado = []
    for p in pedidos:
        nome_produto = buscar_nome_produto(p.id_produto)
        resultado.append({
            "id": p.id_pedido,
            "cliente": p.usuario.nome,  # Nome via relacionamento
            "produto": nome_produto,
            "id_produto": p.id_produto,
            "id_cartao": p.id_cartao,
            "id_usuario": p.id_usuario,
            "data": p.data_pedido.strftime("%d/%m/%Y"),
            "valor": p.valor_total,
            "status": p.status
        })
    
    return jsonify(resultado)

# Criar um pedido
@pedido_bp.route("/", methods=["POST"])
def criar_pedido():
    dados = request.json
    
    # Validar campos obrigatórios (removemos nome_cliente)
    if not dados.get("id_produto") or not dados.get("valor_total") or not dados.get("id_cartao") or not dados.get("id_usuario"):
        return jsonify({"erro": "ID do produto, ID do cartão, ID do usuário e valor total são obrigatórios"}), 400
    
    # Verificar se usuário existe
    usuario = Usuario.query.get(dados["id_usuario"])
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    # Verificar se cartão existe e pertence ao usuário
    cartao = Cartao.query.get(dados["id_cartao"])
    if not cartao:
        return jsonify({"erro": "Cartão não encontrado"}), 404
    
    if cartao.usuario_id != usuario.id:
        return jsonify({"erro": "Cartão não pertence ao usuário informado"}), 400

    novo_pedido = Pedido(
        data_pedido=datetime.strptime(dados["data_pedido"], "%Y-%m-%d"),
        id_produto=dados["id_produto"],  # Obrigatório
        id_cartao=dados["id_cartao"],    # Obrigatório
        id_usuario=dados["id_usuario"],  # Obrigatório
        valor_total=dados["valor_total"],
        status=dados["status"]
    )

    db.session.add(novo_pedido)
    db.session.commit()
    return jsonify({"mensagem": "Pedido criado com sucesso", "id_pedido": novo_pedido.id_pedido}), 201

# Atualizar um pedido
@pedido_bp.route("/<int:id_pedido>", methods=["PUT"])
def atualizar_pedido(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    data = request.json

    # Validar se usuário existe caso seja fornecido
    if "id_usuario" in data and data["id_usuario"]:
        usuario = Usuario.query.get(data["id_usuario"])
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404

    # Validar se cartão existe caso seja fornecido
    if "id_cartao" in data and data["id_cartao"]:
        cartao = Cartao.query.get(data["id_cartao"])
        if not cartao:
            return jsonify({"erro": "Cartão não encontrado"}), 404

    pedido.data_pedido = datetime.strptime(data["data_pedido"], "%Y-%m-%d") if "data_pedido" in data else pedido.data_pedido
    pedido.id_produto = data.get("id_produto", pedido.id_produto)
    pedido.id_cartao = data.get("id_cartao", pedido.id_cartao)
    pedido.id_usuario = data.get("id_usuario", pedido.id_usuario)
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

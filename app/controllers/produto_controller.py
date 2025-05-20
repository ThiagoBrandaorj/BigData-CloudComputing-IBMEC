from flask import Blueprint, request, jsonify
from app.cosmosdb import container
from app.models.produto import Produto

produto_bp = Blueprint("produto", __name__)

# Criar um produto
@produto_bp.route("", methods=["POST"])
def criar_produto():
    dados = request.json
    
    if not dados.get("produtoCategoria") or not dados.get("nome") or not dados.get("preco"):
        return jsonify({"erro": "Categoria, nome e preço são obrigatórios"}), 400

    novo_produto = Produto(
        produtoCategoria=dados["produtoCategoria"],
        nome=dados["nome"],
        preco=dados["preco"],
        urlImagem=dados.get("urlImagem"),
        descricao=dados.get("descricao")
    )

    container.create_item(novo_produto.to_dict())

    return jsonify({"mensagem": "Produto criado com sucesso!", "id": novo_produto.id}), 201


# Buscar todos os produtos
@produto_bp.route("", methods=["GET"])
def buscar_produtos():
    query = "SELECT * FROM produtos"
    produtos = list(container.query_items(query=query, enable_cross_partition_query=True))

    return jsonify(produtos), 200


# Buscar produto por ID
@produto_bp.route("/<string:produto_id>", methods=["GET"])
def buscar_produto_por_id(produto_id):
    query = f"SELECT * FROM produtos p WHERE p.id = '{produto_id}'"
    produtos = list(container.query_items(query=query, enable_cross_partition_query=True))

    if not produtos:
        return jsonify({"erro": "Produto não encontrado"}), 404

    return jsonify(produtos[0]), 200

# Buscar produto por Nome
@produto_bp.route("/nome/<string:nome>", methods=["GET"])
def buscar_produto_por_nome(nome):
    query = f"SELECT * FROM produtos p WHERE p.nome = '{nome}'"
    produtos = list(container.query_items(query=query, enable_cross_partition_query=True))

    if not produtos:
        return jsonify({"erro": "Produto não encontrado"}), 404

    return jsonify(produtos[0]), 200


# Editar um produto
@produto_bp.route("/<string:produto_id>", methods=["PUT"])
def editar_produto(produto_id):
    query = f"SELECT * FROM produtos p WHERE p.id = '{produto_id}'"
    produtos = list(container.query_items(query=query, enable_cross_partition_query=True))

    if not produtos:
        return jsonify({"erro": "Produto não encontrado"}), 404

    produto = produtos[0]  # Pegamos o primeiro (e único) resultado

    dados = request.json
    produto.update({
        "produtoCategoria": dados.get("produtoCategoria", produto["produtoCategoria"]),
        "nome": dados.get("nome", produto["nome"]),
        "preco": dados.get("preco", produto["preco"]),
        "urlImagem": dados.get("urlImagem", produto["urlImagem"]),
        "descricao": dados.get("descricao", produto["descricao"]),
    })

    container.replace_item(item=produto["id"], body=produto)

    return jsonify({"mensagem": "Produto atualizado com sucesso!"}), 200


# Deletar um produto
@produto_bp.route("/<string:produto_id>", methods=["DELETE"])
def deletar_produto(produto_id):
    query = f"SELECT * FROM produtos p WHERE p.id = '{produto_id}'"
    produtos = list(container.query_items(query=query, enable_cross_partition_query=True))

    if not produtos:
        return jsonify({"erro": "Produto não encontrado"}), 404

    container.delete_item(item=produtos[0]["id"], partition_key=produtos[0]["produtoCategoria"])

    return jsonify({"mensagem": "Produto deletado com sucesso!"}), 200

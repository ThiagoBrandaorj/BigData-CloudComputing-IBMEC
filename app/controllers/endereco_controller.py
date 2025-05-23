from flask import Blueprint, request, jsonify
from app.database import db
from app.models.endereco import Endereco
from app.models.usuario import Usuario

endereco_bp = Blueprint("endereco", __name__)

@endereco_bp.route("/usuario/<int:usuario_id>", methods=["POST"])
def criar_endereco(usuario_id):
    dados = request.json
    
    if not Usuario.query.get(usuario_id):
        return jsonify({"erro": "Usuário não encontrado"}), 404
    
    # Validar campos obrigatórios
    campos_obrigatorios = ["logradouro", "bairro", "cidade", "uf", "cep"]
    for campo in campos_obrigatorios:
        if not dados.get(campo):
            return jsonify({"erro": f"O campo '{campo}' é obrigatório"}), 400
    
    endereco = Endereco(
        usuario_id=usuario_id,
        logradouro=dados["logradouro"],
        complemento=dados.get("complemento"),
        bairro=dados["bairro"],
        cidade=dados["cidade"],
        uf=dados["uf"],
        cep=dados["cep"],
        pais=dados.get("pais", "Brasil"),
        tipo=dados.get("tipo")
    )
    
    try:
        db.session.add(endereco)
        db.session.commit()
        return jsonify({"mensagem": "Endereço criado com sucesso", "id": endereco.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": "Erro ao criar endereço"}), 500

@endereco_bp.route("/usuario/<int:usuario_id>", methods=["GET"])
def listar_enderecos(usuario_id):
    if not Usuario.query.get(usuario_id):
        return jsonify({"erro": "Usuário não encontrado"}), 404
        
    enderecos = Endereco.query.filter_by(usuario_id=usuario_id).all()
    if not enderecos:
        return jsonify({"erro": "Nenhum endereço encontrado para este usuário"}), 404
        
    return jsonify([{
        "id": e.id,
        "logradouro": e.logradouro,
        "complemento": e.complemento,
        "bairro": e.bairro,
        "cidade": e.cidade,
        "uf": e.uf,
        "cep": e.cep,
        "pais": e.pais,
        "tipo": e.tipo
    } for e in enderecos]), 200

@endereco_bp.route("/<int:endereco_id>", methods=["PUT"])
def atualizar_endereco(endereco_id):
    endereco = Endereco.query.get(endereco_id)
    if not endereco:
        return jsonify({"erro": "Endereço não encontrado"}), 404
    
    dados = request.json
    if not dados:
        return jsonify({"erro": "O corpo da requisição não pode estar vazio"}), 400
    
    endereco.logradouro = dados.get("logradouro", endereco.logradouro)
    endereco.complemento = dados.get("complemento", endereco.complemento)
    endereco.bairro = dados.get("bairro", endereco.bairro)
    endereco.cidade = dados.get("cidade", endereco.cidade)
    endereco.uf = dados.get("uf", endereco.uf)
    endereco.cep = dados.get("cep", endereco.cep)
    endereco.pais = dados.get("pais", endereco.pais)
    endereco.tipo = dados.get("tipo", endereco.tipo)
    
    try:
        db.session.commit()
        return jsonify({"mensagem": "Endereço atualizado com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": "Erro ao atualizar endereço"}), 500

@endereco_bp.route("/<int:endereco_id>", methods=["DELETE"])
def deletar_endereco(endereco_id):
    endereco = Endereco.query.get(endereco_id)
    if not endereco:
        return jsonify({"erro": "Endereço não encontrado"}), 404
    
    db.session.delete(endereco)
    db.session.commit()
    
    return jsonify({"mensagem": "Endereço deletado com sucesso"}), 200
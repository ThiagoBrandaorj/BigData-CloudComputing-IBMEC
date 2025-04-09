from flask import Blueprint, request, jsonify
from app.database import db
from app.models.usuario import Usuario

usuario_bp = Blueprint("usuario", __name__)

@usuario_bp.route("", methods=["POST"])
def criar_usuario():
    dados = request.json

    # Validações iniciais
    if not dados.get("nome") or not dados.get("email"):
        return jsonify({"erro": "Nome e email são obrigatórios"}), 400

    # Verificar se email já existe
    if Usuario.query.filter_by(email=dados["email"]).first():
        return jsonify({"erro": "Email já cadastrado"}), 400

    # Verificar se CPF já existe (se fornecido)
    if "cpf" in dados and dados["cpf"] and Usuario.query.filter_by(cpf=dados["cpf"]).first():
        return jsonify({"erro": "CPF já cadastrado"}), 400

    # Só cria o objeto depois de todas as validações
    novo_usuario = Usuario(
        nome=dados["nome"],
        email=dados["email"],
        dt_nascimento=dados.get("dt_nascimento"),
        cpf=dados.get("cpf"),
        telefone=dados.get("telefone")
    )

    try:
        db.session.add(novo_usuario)
        db.session.commit()
        return jsonify({"mensagem": "Usuário criado com sucesso!", "id": novo_usuario.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": "Erro ao salvar usuário no banco de dados"}), 500


# Buscar todos os usuários
@usuario_bp.route("", methods=["GET"])
def buscar_usuarios():
    usuarios = Usuario.query.all()
    lista_usuarios = [
        {
            "id": u.id,
            "nome": u.nome,
            "email": u.email,
            "dt_nascimento": str(u.dt_nascimento) if u.dt_nascimento else None,
            "cpf": u.cpf,
            "telefone": u.telefone
        }
        for u in usuarios
    ]
    return jsonify(lista_usuarios), 200


# Buscar usuário por ID
@usuario_bp.route("/<int:usuario_id>", methods=["GET"])
def buscar_usuario_por_id(usuario_id):
    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    return jsonify({
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "dt_nascimento": str(usuario.dt_nascimento) if usuario.dt_nascimento else None,
        "cpf": usuario.cpf,
        "telefone": usuario.telefone
    }), 200


# Editar um usuário
@usuario_bp.route("/<int:usuario_id>", methods=["PUT"])
def editar_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    dados = request.json
    if not dados:
        return jsonify({"erro": "O corpo da requisição não pode estar vazio"}), 400

    usuario.nome = dados.get("nome", usuario.nome)
    usuario.email = dados.get("email", usuario.email)
    usuario.dt_nascimento = dados.get("dt_nascimento", usuario.dt_nascimento)
    usuario.cpf = dados.get("cpf", usuario.cpf)
    usuario.telefone = dados.get("telefone", usuario.telefone)

    db.session.commit()
    return jsonify({"mensagem": "Usuário atualizado com sucesso!"}), 200


# Deletar um usuário
@usuario_bp.route("/<int:usuario_id>", methods=["DELETE"])
def deletar_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    db.session.delete(usuario)
    db.session.commit()

    return jsonify({"mensagem": "Usuário deletado com sucesso!"}), 200

from flask import Blueprint, request, jsonify
from app.database import db
from app.models.usuario import Usuario
from app.models.cartao import Cartao
from app.request.transacao_request import TransacaoRequest
from app.response.transacao_response import TransacaoResponse
from datetime import datetime
import uuid
from decimal import Decimal
from dateutil.relativedelta import relativedelta

cartao_bp = Blueprint("cartao", __name__)

# Criar um novo cartão
@cartao_bp.route("/<int:id_user>", methods=["POST"])
def create_cartao(id_user):
    data = request.get_json()

    usuario = Usuario.query.get(id_user)
    if not usuario:
        return jsonify({"message": "Usuário não encontrado"}), 404
    
    mes, ano = map(int, data["validade"].split("/"))
    validade = datetime(ano, mes, 1) + relativedelta(day=31)

    novo_cartao = Cartao(
        usuario_id=id_user,
        numero=data["numero"],
        nome_impresso=data["nome_impresso"],
        validade=validade,
        cvv=data["cvv"],
        bandeira=data["bandeira"],
        tipo=data.get("tipo", ""),
        saldo=data.get("saldo", 0.00),
    )

    db.session.add(novo_cartao)
    db.session.commit()

    return jsonify({"message": "Cartão criado com sucesso", "cartao_id": novo_cartao.id}), 201


# Autorizar uma transação
@cartao_bp.route("/authorize/<int:id_user>", methods=["POST"])
def authorize_transaction(id_user):
    try:
        data = request.get_json()
        transacao = TransacaoRequest(**data)  # Validação automática com Pydantic

        usuario = Usuario.query.get(id_user)
        if not usuario:
            return jsonify(TransacaoResponse(
                status="NOT_AUTHORIZED",
                codigo_autorizacao=None,
                dt_transacao=datetime.utcnow(),
                message="Usuário não encontrado"
            ).model_dump()), 404

        # Buscar o cartão do usuário
        cartao = Cartao.query.filter_by(usuario_id=id_user, numero=transacao.numero, cvv=transacao.cvv).first()
        if not cartao:
            return jsonify(TransacaoResponse(
                status="NOT_AUTHORIZED",
                codigo_autorizacao=None,
                dt_transacao=datetime.utcnow(),
                message="Cartão não encontrado"
            ).model_dump()), 404
        
         # Pegar a validade informada na requisição
        mes, ano = map(int, transacao.dt_expiracao.split("/"))
        validade_requisicao = datetime(ano, mes, 1) + relativedelta(day=31)

        # Verificar se o cartão está expirado
        if cartao.validade < datetime.utcnow():
            return jsonify(TransacaoResponse(
                status="NOT_AUTHORIZED",
                codigo_autorizacao=None,
                dt_transacao=datetime.utcnow(),
                message="Cartão expirado"
            ).model_dump()), 400
        
        # Verificar se a validade informada na transação bate com a validade cadastrada no banco
        if cartao.validade != validade_requisicao:
            return jsonify(TransacaoResponse(
                status="NOT_AUTHORIZED",
                codigo_autorizacao=None,
                dt_transacao=datetime.utcnow(),
                message="Validade incorreta"
            ).model_dump()), 400

        # Verificar saldo disponível
        if cartao.saldo < Decimal(str(transacao.valor)):
            return jsonify(TransacaoResponse(
                status="NOT_AUTHORIZED",
                codigo_autorizacao=None,
                dt_transacao=datetime.utcnow(),
                message="Saldo insuficiente"
            ).model_dump()), 400

        # Deduzir o valor da compra do saldo
        cartao.saldo -= Decimal(str(transacao.valor))
        db.session.commit()

        # Criar resposta com sucesso
        return jsonify(TransacaoResponse(
            status="AUTHORIZED",
            codigo_autorizacao=uuid.uuid4(),
            dt_transacao=datetime.utcnow(),
            message="Compra autorizada"
        ).model_dump()), 200

    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

# Atualizar o saldo de um cartão
@cartao_bp.route("/saldo/<int:id_cartao>", methods=["PUT"])
def update_saldo(id_cartao):
    try:
        data = request.get_json()
        
        if 'saldo' not in data:
            return jsonify({"message": "O campo 'saldo' é obrigatório"}), 400
            
        cartao = Cartao.query.get(id_cartao)
        if not cartao:
            return jsonify({"message": "Cartão não encontrado"}), 404
        
        # Soma o novo valor ao saldo atual do cartão
        cartao.saldo += Decimal(str(data['saldo']))
        db.session.commit()
        
        return jsonify({
            "message": "Saldo atualizado com sucesso",
            "cartao_id": cartao.id,
            "saldo": float(cartao.saldo)
        }), 200
        
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500
        
# Deletar um cartão
@cartao_bp.route("/<int:id_cartao>", methods=["DELETE"])
def delete_cartao(id_cartao):
    try:
        cartao = Cartao.query.get(id_cartao)
        if not cartao:
            return jsonify({"message": "Cartão não encontrado"}), 404
            
        db.session.delete(cartao)
        db.session.commit()
        
        return jsonify({"message": "Cartão deletado com sucesso"}), 200
        
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500


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
@cartao_bp.route("/usuario/<int:id_user>", methods=["POST"])
def create_cartao(id_user):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"erro": "O corpo da requisição não pode estar vazio"}), 400

        usuario = Usuario.query.get(id_user)
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        # Validar campos obrigatórios
        campos_obrigatorios = ["numero", "nome_impresso", "validade", "cvv", "bandeira"]
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({"erro": f"O campo '{campo}' é obrigatório"}), 400
        
        # Verificar se já existe um cartão com o mesmo número para este usuário
        cartao_existente = Cartao.query.filter_by(
            usuario_id=id_user,
            numero=data["numero"]
        ).first()
        
        if cartao_existente:
            return jsonify({"erro": "Já existe um cartão cadastrado com este número para este usuário"}), 400
        
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

        return jsonify({"mensagem": "Cartão criado com sucesso", "cartao_id": novo_cartao.id}), 201
        
    except ValueError:
        return jsonify({"erro": "Formato de data inválido. Use o formato MM/AAAA"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": "Erro ao criar cartão"}), 500


# Autorizar uma transação
@cartao_bp.route("/authorize/usuario/<int:id_user>", methods=["POST"])
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

@cartao_bp.route("/usuario/<int:id_user>", methods=["GET"])
def listar_cartoes_usuario(id_user):
    try:
        usuario = Usuario.query.get(id_user)
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404
            
        cartoes = Cartao.query.filter_by(usuario_id=id_user).all()
        if not cartoes:
            return jsonify({"erro": "Nenhum cartão encontrado para este usuário"}), 404
            
        resultado = []
        for cartao in cartoes:
            mes = cartao.validade.month
            ano = cartao.validade.year
            validade_formatada = f"{mes:02d}/{ano}"
            
            resultado.append({
                "id": cartao.id,
                "numero": cartao.numero,
                "nome_impresso": cartao.nome_impresso,
                "validade": validade_formatada,
                "cvv": cartao.cvv,
                "bandeira": cartao.bandeira,
                "tipo": cartao.tipo,
                "saldo": float(cartao.saldo)
            })
            
        return jsonify(resultado), 200
            
    except Exception as e:
        return jsonify({"erro": "Erro ao listar cartões"}), 500
    
# buscando cartão pelo número
@cartao_bp.route("/numero/<string:numero_cartao>", methods=["GET"])
def get_cartao_by_numero(numero_cartao):
    try:
        # Buscar cartão pelo número
        cartao = Cartao.query.filter_by(numero=numero_cartao).first()
        
        if not cartao:
            return jsonify({"erro": "Cartão não encontrado"}), 404
        
        # Formatar a data de validade
        mes = cartao.validade.month
        ano = cartao.validade.year
        validade_formatada = f"{mes:02d}/{ano}"
        
        # Montar a resposta
        resposta = {
            "id": cartao.id,
            "usuario_id": cartao.usuario_id,
            "numero": cartao.numero,
            "nome_impresso": cartao.nome_impresso,
            "validade": validade_formatada,
            "cvv": cartao.cvv,
            "bandeira": cartao.bandeira,
            "tipo": cartao.tipo,
            "saldo": float(cartao.saldo)
        }
        
        return jsonify(resposta), 200
        
    except Exception as e:
        return jsonify({"erro": "Erro ao buscar cartão", "detalhes": str(e)}), 500


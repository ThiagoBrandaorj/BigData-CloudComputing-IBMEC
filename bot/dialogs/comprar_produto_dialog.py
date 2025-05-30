from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext
from botbuilder.core import MessageFactory, UserState, CardFactory
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.dialogs import DialogTurnResult
from botbuilder.schema import (
    ActionTypes,
    HeroCard,
    CardAction,
    CardImage,
)
import re
from datetime import datetime, date
from api.product_api import ProductAPI
from api.order_api import OrderAPI

class ComprarProdutoDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(ComprarProdutoDialog, self).__init__("ComprarProdutoDialog")

        self.add_dialog(TextPrompt("nomeClientePrompt"))
        self.add_dialog(TextPrompt("numeroCartaoCreditoPrompt"))
        self.add_dialog(TextPrompt("dataExpiracaoPrompt"))
        self.add_dialog(TextPrompt("cvvPrompt"))

        self.add_dialog(
            WaterfallDialog(
                "comprarProdutoWaterfall",
                [
                    self.nome_cliente_step,
                    self.numero_cartao_step,
                    self.data_expiracao_step,
                    self.cvv_step,
                    self.processar_compra_step
                ],
            )
        )

        self.initial_dialog_id = "comprarProdutoWaterfall"

    async def nome_cliente_step(self, step_context: WaterfallStepContext):
        product_id = step_context.options.get("productId")
        step_context.values["productId"] = product_id
        
        prompt_message = MessageFactory.text("Para finalizar a compra, preciso do seu nome completo:")
        
        prompt_options = PromptOptions(
            prompt=prompt_message,
            retry_prompt=MessageFactory.text("Por favor, digite seu nome completo.")
        )
        
        return await step_context.prompt("nomeClientePrompt", prompt_options)

    async def numero_cartao_step(self, step_context: WaterfallStepContext):
        nome_cliente = step_context.result.strip()
        
        # Validar nome (pelo menos 2 palavras)
        if len(nome_cliente.split()) < 2:
            await step_context.context.send_activity(
                MessageFactory.text("Por favor, digite seu nome completo (nome e sobrenome).")
            )
            return await step_context.replace_dialog("comprarProdutoWaterfall", step_context.options)
        
        step_context.values["nome_cliente"] = nome_cliente
        
        prompt_message = MessageFactory.text("Digite o número do seu cartão de crédito (16 dígitos):")
        
        prompt_options = PromptOptions(
            prompt=prompt_message,
            retry_prompt=MessageFactory.text("Por favor, digite um número de cartão válido com 16 dígitos.")
        )
        
        return await step_context.prompt("numeroCartaoCreditoPrompt", prompt_options)

    async def data_expiracao_step(self, step_context: WaterfallStepContext):
        numero_cartao = step_context.result.strip().replace(" ", "")
        
        # Validar número do cartão
        if not self.validar_numero_cartao(numero_cartao):
            await step_context.context.send_activity(
                MessageFactory.text("Número de cartão inválido. O cartão deve ter exatamente 16 dígitos.")
            )
            return await step_context.replace_dialog("comprarProdutoWaterfall", step_context.options)
        
        step_context.values["numero_cartao"] = numero_cartao
        
        prompt_message = MessageFactory.text("Digite a data de validade do cartão (formato MM/AAAA):")
        
        prompt_options = PromptOptions(
            prompt=prompt_message,
            retry_prompt=MessageFactory.text("Por favor, digite a data no formato MM/AAAA (ex: 12/2026).")
        )
        
        return await step_context.prompt("dataExpiracaoPrompt", prompt_options)

    async def cvv_step(self, step_context: WaterfallStepContext):
        data_expiracao = step_context.result.strip()
        
        # Validar data de expiração
        if not self.validar_data_expiracao(data_expiracao):
            await step_context.context.send_activity(
                MessageFactory.text("Data de validade inválida ou cartão vencido. Use o formato MM/AAAA e certifique-se de que o cartão não está vencido.")
            )
            return await step_context.replace_dialog("comprarProdutoWaterfall", step_context.options)
        
        step_context.values["data_expiracao"] = data_expiracao
        
        prompt_message = MessageFactory.text("Digite o CVV do cartão (3 ou 4 dígitos):")
        
        prompt_options = PromptOptions(
            prompt=prompt_message,
            retry_prompt=MessageFactory.text("Por favor, digite um CVV válido (3 ou 4 dígitos).")
        )
        
        return await step_context.prompt("cvvPrompt", prompt_options)

    async def processar_compra_step(self, step_context: WaterfallStepContext):
        cvv = step_context.result.strip()
        
        if not self.validar_cvv(cvv):
            await step_context.context.send_activity(
                MessageFactory.text("CVV inválido. Digite 3 ou 4 dígitos.")
            )
            return await step_context.replace_dialog("comprarProdutoWaterfall", step_context.options)
        
        step_context.values["cvv"] = cvv
        
        product_id = step_context.values["productId"]
        nome_cliente = step_context.values["nome_cliente"]
        numero_cartao = step_context.values["numero_cartao"]
        data_expiracao = step_context.values["data_expiracao"]
        
        await step_context.context.send_activity(
            MessageFactory.text("Processando sua compra... Por favor, aguarde.")
        )
        
        try:
            # 1. Buscar dados do produto
            produto_api = ProductAPI()
            produto = produto_api.consultar_produto_por_id(product_id)
            
            if not produto:
                await step_context.context.send_activity(
                    MessageFactory.text("Erro: Produto não encontrado. Tente novamente.")
                )
                return await step_context.replace_dialog("WaterfallDialog")
            
            if isinstance(produto, dict):
                valor_produto = produto["preco"]
                nome_produto = produto["nome"]
            else:
                await step_context.context.send_activity(
                    MessageFactory.text("Erro: Não foi possível obter informações do produto.")
                )
                return await step_context.replace_dialog("WaterfallDialog")
            
            order_api = OrderAPI()
            id_usuario = 1
            
            resultado_transacao = order_api.autorizar_transacao(
                id_usuario, numero_cartao, data_expiracao, cvv, valor_produto
            )
            
            if not resultado_transacao or resultado_transacao.get("status") != "AUTHORIZED":
                mensagem_erro = resultado_transacao.get("message", "Transação não autorizada") if resultado_transacao else "Erro na comunicação com o banco"
                await step_context.context.send_activity(
                    MessageFactory.text(f"Pagamento não autorizado: {mensagem_erro}")
                )
                return await step_context.replace_dialog("WaterfallDialog")
            
            print(f"Tentando criar pedido para cliente: {nome_cliente}, produto: {nome_produto}, valor: {valor_produto}")
            resultado_pedido = order_api.criar_pedido(product_id, nome_cliente, valor_produto)
            print(f"Resultado da criação do pedido: {resultado_pedido}")
            
            if not resultado_pedido:
                await step_context.context.send_activity(
                    MessageFactory.text("⚠️ Pagamento autorizado, mas houve erro ao registrar o pedido. Verifique se a API está rodando e tente novamente.")
                )
                await step_context.context.send_activity(
                    MessageFactory.text("💡 Dica: Verifique se a aplicação Flask está rodando na porta 8000.")
                )
                return await step_context.replace_dialog("WaterfallDialog")
            
            # 4. Sucesso!
            codigo_autorizacao = resultado_transacao.get("codigo_autorizacao", "N/A")
            id_pedido = resultado_pedido.get("id_pedido", "N/A")
            data_compra = datetime.now().strftime("%d/%m/%Y às %H:%M")
            
            
            card_comprovante = CardFactory.hero_card(
                HeroCard(
                    title="✅ Compra Realizada com Sucesso!",
                    subtitle=f"Comprovante de Compra - {data_compra}",
                    text=f"""
**Produto:** {nome_produto}
**Valor:** R$ {valor_produto:.2f}
**Pedido:** #{id_pedido}
**Autorização:** {str(codigo_autorizacao)}
**Cliente:** {nome_cliente}
                    """
                )
            )
            
            await step_context.context.send_activity(MessageFactory.attachment(card_comprovante))

            
        except Exception as e:
            print(f"Erro no processamento da compra: {e}")
            await step_context.context.send_activity(
                MessageFactory.text("Ocorreu um erro inesperado. Tente novamente mais tarde.")
            )
        
        return await step_context.replace_dialog("WaterfallDialog")

    def validar_numero_cartao(self, numero):
        """Valida se o número do cartão tem 16 dígitos"""
        return bool(re.match(r'^\d{16}$', numero))

    def validar_data_expiracao(self, data):
        """Valida formato MM/AAAA e se não está vencido"""
        try:
            if not re.match(r'^\d{2}/\d{4}$', data):
                return False
            
            mes, ano = map(int, data.split('/'))
            
            if mes < 1 or mes > 12:
                return False
            
            # Verificar se não está vencido
            hoje = date.today()
            data_vencimento = date(ano, mes, 1)
            
            return data_vencimento >= date(hoje.year, hoje.month, 1)
            
        except:
            return False

    def validar_cvv(self, cvv):
        """Valida se CVV tem 3 ou 4 dígitos"""
        return bool(re.match(r'^\d{3,4}$', cvv))
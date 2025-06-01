from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext
from botbuilder.core import MessageFactory, CardFactory
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.schema import HeroCard, CardImage
from api.cartao_api import CartaoAPI
from api.order_api import OrderAPI
from api.product_api import ProductAPI
from datetime import datetime, date
import re

class ExtratoCompraDialog(ComponentDialog):
    def __init__(self):
        super(ExtratoCompraDialog, self).__init__("ExtratoCompraDialog")

        self.cartao_api = CartaoAPI()
        self.order_api = OrderAPI()
        self.product_api = ProductAPI()

        self.add_dialog(TextPrompt("numeroCartaoPrompt"))
        self.add_dialog(TextPrompt("nomeImpressoPrompt"))
        self.add_dialog(TextPrompt("dataValidadePrompt"))
        self.add_dialog(TextPrompt("cvvPrompt"))
        
        self.add_dialog(
            WaterfallDialog(
                "ExtratoCompraWaterfallDialog",
                [
                    self.numero_cartao_step,
                    self.nome_impresso_step,
                    self.data_validade_step,
                    self.cvv_step,
                    self.mostrar_extrato_step,
                ]
            )
        )

        self.initial_dialog_id = "ExtratoCompraWaterfallDialog"

    async def numero_cartao_step(self, step_context: WaterfallStepContext):
        prompt_message = MessageFactory.text("Para consultar seu extrato, digite o número do seu cartão (16 dígitos):")
        
        prompt_options = PromptOptions(
            prompt=prompt_message,
            retry_prompt=MessageFactory.text("Por favor, digite um número de cartão válido com 16 dígitos.")
        )
        
        return await step_context.prompt("numeroCartaoPrompt", prompt_options)

    async def nome_impresso_step(self, step_context: WaterfallStepContext):
        numero_cartao = step_context.result.strip().replace(" ", "")
        
        # Validar número do cartão
        if not self.validar_numero_cartao(numero_cartao):
            await step_context.context.send_activity(
                MessageFactory.text("Número de cartão inválido. O cartão deve ter exatamente 16 dígitos.")
            )
            return await step_context.replace_dialog("ExtratoCompraWaterfallDialog")
        
        # Buscar o cartão no sistema
        cartao_cadastrado = self.cartao_api.consultar_cartao_por_numero(numero_cartao)
        
        if not cartao_cadastrado:
            await step_context.context.send_activity(
                MessageFactory.text("Cartão não encontrado no sistema. Verifique o número e tente novamente.")
            )
            return await step_context.replace_dialog("ExtratoCompraWaterfallDialog")
        
        step_context.values["numero_cartao"] = numero_cartao
        step_context.values["cartao_info"] = cartao_cadastrado
        
        prompt_message = MessageFactory.text("Digite o nome impresso no cartão:")
        
        prompt_options = PromptOptions(
            prompt=prompt_message,
            retry_prompt=MessageFactory.text("Por favor, digite o nome exatamente como aparece no cartão.")
        )
        
        return await step_context.prompt("nomeImpressoPrompt", prompt_options)

    async def data_validade_step(self, step_context: WaterfallStepContext):
        nome_impresso = step_context.result.strip()
        cartao_info = step_context.values["cartao_info"]
        
        # Validar nome impresso
        nome_cadastrado = cartao_info.get('nome_impresso', '').strip()
        nome_fornecido_limpo = ' '.join(nome_impresso.lower().split())
        nome_cadastrado_limpo = ' '.join(nome_cadastrado.lower().split())
        
        if nome_fornecido_limpo != nome_cadastrado_limpo:
            await step_context.context.send_activity(
                MessageFactory.text("O nome impresso no cartão não confere com os dados cadastrados.")
            )
            return await step_context.replace_dialog("ExtratoCompraWaterfallDialog")
        
        step_context.values["nome_impresso"] = nome_impresso
        
        prompt_message = MessageFactory.text("Digite a data de validade do cartão (formato MM/AAAA):")
        
        prompt_options = PromptOptions(
            prompt=prompt_message,
            retry_prompt=MessageFactory.text("Por favor, digite a data no formato MM/AAAA (ex: 12/2026).")
        )
        
        return await step_context.prompt("dataValidadePrompt", prompt_options)

    async def cvv_step(self, step_context: WaterfallStepContext):
        data_validade = step_context.result.strip()
        
        # Validar data de validade
        if not self.validar_data_expiracao(data_validade):
            await step_context.context.send_activity(
                MessageFactory.text("Data de validade inválida ou cartão vencido. Use o formato MM/AAAA e certifique-se de que o cartão não está vencido.")
            )
            return await step_context.replace_dialog("ExtratoCompraWaterfallDialog")
        
        step_context.values["data_validade"] = data_validade
        
        prompt_message = MessageFactory.text("Digite o CVV do cartão (3 ou 4 dígitos):")
        
        prompt_options = PromptOptions(
            prompt=prompt_message,
            retry_prompt=MessageFactory.text("Por favor, digite um CVV válido (3 ou 4 dígitos).")
        )
        
        return await step_context.prompt("cvvPrompt", prompt_options)

    async def mostrar_extrato_step(self, step_context: WaterfallStepContext):
        cvv = step_context.result.strip()
        
        # Validar CVV
        if not self.validar_cvv(cvv):
            await step_context.context.send_activity(
                MessageFactory.text("CVV inválido. Digite 3 ou 4 dígitos.")
            )
            return await step_context.replace_dialog("ExtratoCompraWaterfallDialog")
        
        cartao_info = step_context.values["cartao_info"]
        cartao_id = cartao_info.get("id")
        
        
        usuario_id = cartao_info.get("usuario_id")
        if not usuario_id:
            await step_context.context.send_activity(
                MessageFactory.text("Erro: Usuário do cartão não encontrado.")
            )
            return await step_context.end_dialog()
        
        pedidos = []
        
        nome_cliente = cartao_info.get('nome_impresso', '')
        if nome_cliente:
            pedidos = self.order_api.consultar_pedidos(nome_cliente)
        
        pedidos_filtrados = []
        for pedido in pedidos:
            if pedido.get('id_cartao') == cartao_id:
                pedidos_filtrados.append(pedido)
            elif not pedido.get('id_cartao'):
                pedidos_filtrados.append(pedido)
        
        if not pedidos_filtrados or len(pedidos_filtrados) == 0:
            await step_context.context.send_activity(
                MessageFactory.text("Nenhum pedido encontrado neste cartão.")
            )
            return await step_context.replace_dialog("WaterfallDialog")
        
        await self.exibir_extrato_cards(step_context, cartao_info, pedidos_filtrados)
        return await step_context.replace_dialog("WaterfallDialog")

    async def exibir_extrato_cards(self, step_context, cartao_info, pedidos):
        ultimos_digitos = cartao_info["numero"][-4:] if cartao_info.get("numero") else "****"
        total_valor = sum(float(p.get('valor', 0)) for p in pedidos)
        
        card_resumo = CardFactory.hero_card(
            HeroCard(
                title="Extrato do Cartão",
                subtitle=f"Cliente: {cartao_info.get('nome_impresso', 'N/A')}",
                text=f"**Cartão:** •••• •••• •••• {ultimos_digitos}\n\n"
                     f"**Total de pedidos:** {len(pedidos)}\n\n"
                     f"**Valor total:** R$ {total_valor:.2f}"
            )
        )
        
        await step_context.context.send_activity(MessageFactory.attachment(card_resumo))
        
        for pedido in pedidos:
            await self.exibir_card_pedido(step_context, pedido)

    async def exibir_card_pedido(self, step_context, pedido):
        produto_id = pedido.get('id_produto')
        imagem_url = ""
        
        if produto_id:
            produto = self.product_api.consultar_produto_por_id(produto_id)
            if produto and isinstance(produto, dict):
                imagem_url = produto.get('urlImagem', '')
        
        # Criar card do pedido
        card = CardFactory.hero_card(
            HeroCard(
                title=f"Pedido #{pedido.get('id', 'N/A')}",
                subtitle=f"Data: {pedido.get('data', 'N/A')} | Status: {pedido.get('status', 'N/A')}",
                text=f"**Produto:** {pedido.get('produto', 'N/A')}\n\n"
                     f"**Valor:** R$ {float(pedido.get('valor', 0)):.2f}",
                images=[CardImage(url=imagem_url)] if imagem_url else []
            )
        )
        
        await step_context.context.send_activity(MessageFactory.attachment(card))

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
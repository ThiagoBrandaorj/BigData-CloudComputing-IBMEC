from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext, \
TextPrompt, PromptOptions
from botbuilder.core import MessageFactory
from api.cartao_api import CartaoAPI
from api.order_api import OrderAPI
from datetime import datetime

class ExtratoCompraDialog(ComponentDialog):
    def __init__(self):
        super(ExtratoCompraDialog, self).__init__("ExtratoCompraDialog")

        self.cartao_api = CartaoAPI()
        self.order_api = OrderAPI()

        self.add_dialog(TextPrompt("TextPrompt"))
        self.add_dialog(
            WaterfallDialog(
                "ExtratoCompraWaterfallDialog",
                [   self.pedir_numero_cartao_step,
                    self.verificar_cartao_step,
                    self.pedir_nome_step,
                    self.validar_usuario_step,
                    self.mostrar_extrato_step,
                ]
            )
        )

        self.initial_dialog_id = "ExtratoCompraWaterfallDialog"

    async def pedir_numero_cartao_step(self, step_context: WaterfallStepContext):
        return await step_context.prompt(
        "TextPrompt",
        PromptOptions(
            prompt=MessageFactory.text("Por favor, digite o número do seu cartão:")
        )
    )
    
    async def verificar_cartao_step(self, step_context: WaterfallStepContext):
        card_number = step_context.result.replace(" ", "").replace("-", "")
        step_context.values["card_number"] = card_number
        
        cartao = self.cartao_api.consultar_cartao_por_numero(card_number)
        if not cartao:
            await step_context.context.send_activity("Cartão não encontrado. Verifique o número e tente novamente.")
            return await step_context.end_dialog()
            
        step_context.values["cartao_info"] = cartao
        return await step_context.next(None)
    
    async def pedir_nome_step(self, step_context: WaterfallStepContext):
      cartao_info = step_context.values["cartao_info"]
      # Mostra apenas parte do nome para segurança
      nome_parcial = cartao_info["nome_impresso"].split()[0] + " " + cartao_info["nome_impresso"].split()[-1][0] + "."
    
      return await step_context.prompt(
        "TextPrompt",
        PromptOptions(
            prompt=MessageFactory.text(f"Por favor, digite seu nome completo como está no cartão (Ex: {nome_parcial}):")
        )
    )
    
    async def validar_usuario_step(self, step_context: WaterfallStepContext):
        nome_completo = step_context.result.strip()
        cartao_info = step_context.values["cartao_info"]
        
        # Comparação case-insensitive e removendo espaços extras
        if nome_completo.lower() != cartao_info["nome_impresso"].strip().lower():
            await step_context.context.send_activity(" Nome não confere com o cadastrado no cartão.")
            return await step_context.end_dialog()
            
        step_context.values["nome_cliente"] = nome_completo
        return await step_context.next(None)
    
    async def mostrar_extrato_step(self, step_context: WaterfallStepContext):
      nome_cliente = step_context.values["nome_cliente"]
      cartao_info = step_context.values["cartao_info"]
    
      # Buscar pedidos usando o OrderAPI existente
      pedidos = self.order_api.consultar_pedidos(nome_cliente)
    
      if not pedidos:
        await step_context.context.send_activity(
            MessageFactory.text(f"Nenhum pedido encontrado para o cliente {nome_cliente}.")
        )
        return await step_context.end_dialog()
    
      # Formatar a resposta (await the coroutine)
      message = await self._formatar_extrato(cartao_info, pedidos)
      await step_context.context.send_activity(MessageFactory.text(message))
      return await step_context.end_dialog()

    # Make sure this is defined as async since it's being awaited
    async def _formatar_extrato(self, cartao_info, pedidos):
      # Formata os últimos 4 dígitos do cartão
      ultimos_digitos = cartao_info["numero"][-4:] if cartao_info["numero"] else "****"
    
      message = [
        f"**EXTRATO DE PEDIDOS**",
        f"Cliente: {cartao_info['nome_impresso']}",
        f"Cartão final: {ultimos_digitos}",
        f"Total de pedidos: {len(pedidos)}",
        "---------------------------------"
        ]
    
      for pedido in pedidos:
        # Assuming pedido["data"] is in format "30/05/2025" as shown in your logs
        data_pedido = pedido["data"]  # Already in correct format based on your API response
        
        message.extend([
            f"**Pedido #**{pedido['id']}",
            f"Data: {data_pedido}",
            f"Valor: R$ {float(pedido['valor']):.2f}",
            f"Produto: {pedido['produto']}",
            f"Status: {pedido['status']}",
            "---------------------------------"
        ])
    
      # Adiciona saldo/resumo se disponível
      if "saldo" in cartao_info:
        message.append(f"Saldo disponível: R$ {float(cartao_info['saldo']):.2f}")
    
      return "\n".join(message)
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext
from botbuilder.core import MessageFactory, CardFactory
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.schema import HeroCard, CardImage, CardAction, ActionTypes
from api.order_api import OrderAPI
from api.product_api import ProductAPI


class ConsultarPedidoDialog(ComponentDialog):
    def __init__(self):
        super(ConsultarPedidoDialog, self).__init__("ConsultarPedidoDialog")

        self.order_api = OrderAPI()
        self.product_api = ProductAPI()
        self.add_dialog(TextPrompt("namePrompt"))

        self.add_dialog(
            WaterfallDialog(
                "consultarPedidoWaterfallDialog",
                [
                    self.prompt_user_name_step,
                    self.show_orders_step,
                ],
            )
        )

        self.initial_dialog_id = "consultarPedidoWaterfallDialog"

    async def prompt_user_name_step(self, step_context: WaterfallStepContext):
        return await step_context.prompt(
            "namePrompt",
            PromptOptions(prompt=MessageFactory.text("Digite o número do pedido que deseja consultar:"))
        )

    async def show_orders_step(self, step_context: WaterfallStepContext):
        id_pedido = step_context.result
        pedido_resultado = self.order_api.consultar_pedidos_por_id(id_pedido)

        if pedido_resultado and isinstance(pedido_resultado, dict):
            pedido = pedido_resultado  # Já é um dict direto
            
            # Buscar produto pelo ID (obrigatório e único)
            produto_id = pedido.get('id_produto')
            imagem_url = ""
            
            if produto_id:
                print(f"Buscando produto com ID: {produto_id}")
                produto = self.product_api.consultar_produto_por_id(produto_id)
                
                if produto and isinstance(produto, dict):
                    print(f"Produto encontrado: {produto.get('nome', 'N/A')}")
                    imagem_url = produto.get('urlImagem', '')
                    
                    if imagem_url:
                        print(f"URL da imagem: {imagem_url}")
                    else:
                        print("Produto sem imagem cadastrada")
                else:
                    print(f"Produto com ID {produto_id} não encontrado na API")
            else:
                print("ID do produto não encontrado no pedido")
            
            # Criar hero card para o pedido
            card = CardFactory.hero_card(
                HeroCard(
                    title=f"Pedido #{pedido.get('id', id_pedido)}",
                    subtitle=f"Data: {pedido.get('data', 'N/A')} | Status: {pedido.get('status', 'N/A')}",
                    text=f"**Produto:** {pedido.get('produto', 'N/A')}\n\n"
                         f"**Valor:** R$ {pedido.get('valor', 0):.2f}\n\n"
                         f"**Cliente:** {pedido.get('cliente', 'N/A')}",
                    images=[CardImage(url=imagem_url)] if imagem_url else []
                )
            )
            
            await step_context.context.send_activity(MessageFactory.attachment(card))
            
        else:
            # Mensagem simples para pedido não encontrado
            await step_context.context.send_activity(
                MessageFactory.text(f"Pedido #{id_pedido} não encontrado.")
            )

        # Voltar diretamente ao menu principal
        return await step_context.replace_dialog("WaterfallDialog")
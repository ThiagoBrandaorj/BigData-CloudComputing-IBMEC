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
        pedidos = self.order_api.consultar_pedidos_por_id_pedido(id_pedido)

        if pedidos and isinstance(pedidos, list) and len(pedidos) > 0:
            pedido = pedidos[0]  # Pega o primeiro (e provavelmente único) pedido
            
            # Buscar dados do produto para obter a imagem
            produto_id = pedido.get('id_produto')  # Novo campo prioritário
            nome_produto = pedido.get('produto') or pedido.get('nome_produto', '')
            produto = None
            imagem_url = ""
            
            if produto_id:
                # Preferir busca por ID se disponível
                print(f"Buscando produto com ID: {produto_id}")
                produto = self.product_api.consultar_produto_por_id(produto_id)
                
                if produto and isinstance(produto, dict):
                    print(f"Produto encontrado por ID: {produto.get('nome', 'N/A')}")
                    imagem_url = produto.get('urlImagem', '')
                    
                    if imagem_url:
                        print(f"URL da imagem encontrada: {imagem_url}")
                    else:
                        print("Produto não possui imagem cadastrada")
                else:
                    print(f"Produto com ID {produto_id} não encontrado, tentando busca por nome")
                    produto = None
            
            # Fallback: buscar por nome se ID não funcionou ou não existe
            if not produto and nome_produto:
                print(f"Buscando produto com nome: {nome_produto}")
                produtos_encontrados = self.product_api.consultar_produtos(nome_produto)
                
                if produtos_encontrados and isinstance(produtos_encontrados, list) and len(produtos_encontrados) > 0:
                    # Pega o primeiro produto encontrado
                    produto = produtos_encontrados[0]
                    print(f"Produto encontrado por nome: {produto.get('nome', 'N/A')}")
                    
                    # Buscar a URL da imagem do produto
                    imagem_url = produto.get('urlImagem', '')
                    
                    if imagem_url:
                        print(f"URL da imagem encontrada: {imagem_url}")
                    else:
                        print("Produto não possui imagem cadastrada")
                elif produtos_encontrados and isinstance(produtos_encontrados, dict):
                    # Se retornou um único produto como dict
                    produto = produtos_encontrados
                    print(f"Produto encontrado por nome: {produto.get('nome', 'N/A')}")
                    imagem_url = produto.get('urlImagem', '')
                    
                    if imagem_url:
                        print(f"URL da imagem encontrada: {imagem_url}")
                    else:
                        print("Produto não possui imagem cadastrada")
                else:
                    print(f"Produto '{nome_produto}' não encontrado")
                    produto = None
            
            if not produto:
                print("Nenhum método de busca de produto funcionou")
            
            # Criar hero card para o pedido com formatação melhorada
            card = CardFactory.hero_card(
                HeroCard(
                    title=f"Pedido #{pedido.get('id', id_pedido)}",
                    subtitle=f"Data: {pedido.get('data', 'N/A')} | Status: {pedido.get('status', 'N/A')}",
                    text=f"**Produto:** {pedido.get('produto', 'N/A')}\n\n"
                         f"**Valor:** R$ {pedido.get('valor', 0):.2f}\n\n"
                         f"**Cliente:** {pedido.get('cliente', 'N/A')}",
                    images=[CardImage(url=imagem_url)] if imagem_url and produto else []
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
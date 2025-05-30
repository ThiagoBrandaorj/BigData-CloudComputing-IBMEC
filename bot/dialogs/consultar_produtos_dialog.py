from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext, ChoicePrompt, DialogTurnResult, DialogTurnStatus
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, CardFactory, UserState
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.schema import HeroCard, CardImage, CardAction, ActionTypes
from api.product_api import ProductAPI
from dialogs.comprar_produto_dialog import ComprarProdutoDialog


class ConsultarProdutoDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(ConsultarProdutoDialog, self).__init__("ConsultarProdutoDialog")

        self.product_api = ProductAPI()
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        
        # Adicionar o dialog de compra
        self.add_dialog(ComprarProdutoDialog(user_state))

        self.add_dialog(
            WaterfallDialog(
                "consultarProdutoWaterfallDialog",
                [
                    self.product_name_step,
                    self.prompt_process_product_name_step,
                    self.processa_opcao_step,
                ],
            )
        )

        self.initial_dialog_id = "consultarProdutoWaterfallDialog"

    async def product_name_step(self, step_context: WaterfallStepContext):
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Digite o nome do produto:"))
        )

    async def prompt_process_product_name_step(self, step_context: WaterfallStepContext):
        product_name = step_context.result
        step_context.values["produto_nome"] = product_name

        produto = self.product_api.consultar_produtos(product_name)

        if produto:
            # Salvar produto nos values para usar depois
            step_context.values["produto"] = produto
            
            card = CardFactory.hero_card(
                HeroCard(
                    title=produto["nome"],
                    subtitle=f"Categoria: {produto['produtoCategoria']}\nPreço: R$ {produto['preco']}",
                    text=produto.get("descricao", ""),
                    images=[CardImage(url=produto["urlImagem"])] if produto.get("urlImagem") else [],
                    buttons=[
                        CardAction(
                            type=ActionTypes.post_back, 
                            title="Comprar este produto", 
                            value={"acao": "comprar", "productId": produto["id"]}
                        ),
                        CardAction(
                            type=ActionTypes.post_back, 
                            title="Voltar ao menu principal", 
                            value={"acao": "menu"}
                        ),
                    ]
                )
            )

            await step_context.context.send_activity(MessageFactory.attachment(card))
            
            # Retorna esperando a ação do usuário nos botões do card
            return DialogTurnResult(
                status=DialogTurnStatus.Waiting,
                result=step_context.result
            )

        else:
            await step_context.context.send_activity(
                MessageFactory.text(f"Nenhum produto encontrado com o nome '{product_name}'")
            )
            return await step_context.replace_dialog(self.initial_dialog_id)

    async def processa_opcao_step(self, step_context: WaterfallStepContext):
        # Capturar a ação dos botões do hero card
        result_action = step_context.context.activity.value
        
        if result_action is None:
            return await step_context.end_dialog()
        
        acao = result_action.get("acao")
        
        if acao == "comprar":
            product_id = result_action.get("productId")
            
            if product_id:
                return await step_context.begin_dialog("ComprarProdutoDialog", {"productId": product_id})
            else:
                await step_context.context.send_activity(
                    MessageFactory.text("Erro: ID do produto não encontrado.")
                )
                return await step_context.end_dialog()
                
        elif acao == "menu":
            return await step_context.replace_dialog("WaterfallDialog")
        
        # Fallback para casos inesperados
        return await step_context.end_dialog()
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
                MessageFactory.text(f"Nenhum produto encontrado com o nome '{product_name}'.")
            )
            
            # Oferecer opções ao usuário com choices mais claras
            choices = [
                Choice("Tentar novamente"),
                Choice("Voltar ao menu principal")
            ]
            
            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("O que você gostaria de fazer? Digite 1 ou 2:"),
                    choices=choices,
                    retry_prompt=MessageFactory.text("Por favor, escolha uma opção válida: 1 para Tentar novamente ou 2 para Voltar ao menu principal")
                )
            )

    async def processa_opcao_step(self, step_context: WaterfallStepContext):
        # Debug: mostrar o que foi recebido
        print(f"Tipo do resultado: {type(step_context.result)}")
        print(f"Valor do resultado: {step_context.result}")
        
        # Verificar se é uma escolha de texto (quando produto não foi encontrado)
        if isinstance(step_context.result, str):
            escolha = step_context.result.strip()
            
            # Aceitar tanto o texto quanto números
            if escolha in ["Tentar novamente", "1"]:
                # Reiniciar o dialog de consultar produto desde o início
                return await step_context.replace_dialog("consultarProdutoWaterfallDialog")
            elif escolha in ["Voltar ao menu principal", "2"]:
                return await step_context.replace_dialog("WaterfallDialog")
            else:
                # Se não reconheceu a escolha, mostrar erro e voltar ao menu
                await step_context.context.send_activity(
                    MessageFactory.text("Opção não reconhecida. Voltando ao menu principal.")
                )
                return await step_context.replace_dialog("WaterfallDialog")
        
        # Verificar se é um objeto Choice (resultado do ChoicePrompt)
        elif hasattr(step_context.result, 'value'):
            escolha = step_context.result.value
            
            if escolha == "Tentar novamente":
                return await step_context.replace_dialog("consultarProdutoWaterfallDialog")
            elif escolha == "Voltar ao menu principal":
                return await step_context.replace_dialog("WaterfallDialog")
        
        # Capturar a ação dos botões do hero card (quando produto foi encontrado)
        result_action = step_context.context.activity.value
        
        if result_action is None:
            return await step_context.replace_dialog("WaterfallDialog")
        
        acao = result_action.get("acao")
        
        if acao == "comprar":
            product_id = result_action.get("productId")
            
            if product_id:
                return await step_context.begin_dialog("ComprarProdutoDialog", {"productId": product_id})
            else:
                await step_context.context.send_activity(
                    MessageFactory.text("Erro: ID do produto não encontrado.")
                )
                return await step_context.replace_dialog("WaterfallDialog")
                
        elif acao == "menu":
            return await step_context.replace_dialog("WaterfallDialog")
        
        # Fallback para casos inesperados
        return await step_context.replace_dialog("WaterfallDialog")
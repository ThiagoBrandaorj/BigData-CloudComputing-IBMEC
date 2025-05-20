from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext
from botbuilder.core import MessageFactory
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from api.product_api import ProductAPI


class ConsultarProdutoDialog(ComponentDialog):
    def __init__(self):
        super(ConsultarProdutoDialog, self).__init__("ConsultarProdutoDialog")

        self.product_api = ProductAPI()
        self.add_dialog(TextPrompt(TextPrompt.__name__))

        self.add_dialog(
            WaterfallDialog(
                "consultarProdutoWaterfallDialog",
                [
                    self.product_name_step,
                    self.prompt_process_product_name_step,
                ],
            )
        )

        self.initial_dialog_id = "consultarProdutoWaterfallDialog"

    async def product_name_step(self, step_context: WaterfallStepContext):
                
        prompt_message = MessageFactory.text("Por favor, digite o nome do produto que você deseja consultar.")
        
        prompt_option = PromptOptions(
            prompt=prompt_message,
            retry_prompt=MessageFactory.text("Desculpe, não consegui entender. Por favor, digite o nome do produto novamente."),
        )

        return await step_context.prompt(TextPrompt.__name__, prompt_option)
    
    async def prompt_process_product_name_step(self, step_context: WaterfallStepContext):
        product_name = step_context.result
        
        # Consultar o produto usando a API
        produto = self.product_api.consultar_produtos(product_name)
        
        if produto:
            # Formatar os detalhes do produto
            detalhes = f"**{produto['nome']}**\n\n"
            detalhes += f"Categoria: {produto['produtoCategoria']}\n"
            detalhes += f"Preço: R$ {produto['preco']}\n"
            
            if 'descricao' in produto and produto['descricao']:
                detalhes += f"Descrição: {produto['descricao']}\n"
                
            if 'urlImagem' in produto and produto['urlImagem']:
                detalhes += f"Imagem: {produto['urlImagem']}"
                
            await step_context.context.send_activity(MessageFactory.text(detalhes))
        else:
            await step_context.context.send_activity(
                MessageFactory.text(f"Desculpe, não encontrei nenhum produto com o nome '{product_name}'.")
            )
            
        return await step_context.end_dialog()
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext
from botbuilder.core import MessageFactory
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from api.order_api import OrderAPI
import re
from datetime import datetime

class ComprarProdutoDialog(ComponentDialog):
    def __init__(self):
        super(ComprarProdutoDialog, self).__init__("ComprarProdutoDialog")

        self.add_dialog(TextPrompt("namePrompt"))
        self.add_dialog(TextPrompt("productPrompt"))
        self.add_dialog(TextPrompt("cardNumberPrompt", self.validate_card_number))
        self.add_dialog(TextPrompt("cardExpiryPrompt", self.validate_card_expiry))
        self.add_dialog(TextPrompt("cardCvvPrompt", self.validate_card_cvv))


        self.add_dialog(
            WaterfallDialog(
                "comprarProdutoWaterfallDialog",
                [
                    self.prompt_user_name_step,
                    self.prompt_product_step,
                    self.prompt_card_number_step,
                    self.prompt_card_expiry_step,
                    self.prompt_card_cvv_step,
                ],
            )
        )

        self.initial_dialog_id = "comprarProdutoWaterfallDialog"

    async def prompt_user_name_step(self, step_context: WaterfallStepContext):
        return await step_context.prompt(
            "namePrompt",
            PromptOptions(prompt=MessageFactory.text("Digite seu nome completo:"))
        )

    async def prompt_product_step(self, step_context: WaterfallStepContext):
        step_context.values["nome"] = step_context.result
        return await step_context.prompt(
            "productPrompt",
            PromptOptions(prompt=MessageFactory.text("Qual produto você deseja comprar?"))
            # Fazer lógica para checar se o produto existe no banco de dados
        )
    
    async def validate_card_number(self, prompt_context):
        number = prompt_context.recognized.value.strip()
        return number.isdigit() and len(number) == 16

    async def prompt_card_number_step(self, step_context: WaterfallStepContext):
        step_context.values["produto"] = step_context.result
        return await step_context.prompt(
            "cardNumberPrompt",
            PromptOptions(
                prompt=MessageFactory.text("Digite o número do cartão (16 dígitos):"),
                retry_prompt=MessageFactory.text("Número inválido. Tente novamente:")
            )
        )
    

    async def validate_card_expiry(self, prompt_context):
        date = prompt_context.recognized.value.strip()

        # Verifica padrão MM/AAAA
        if not re.match(r"^(0[1-9]|1[0-2])\/\d{4}$", date):
            return False

        try:
            mes, ano = map(int, date.split("/"))
            datetime(ano, mes, 1)
            return True
        except ValueError:
            return False

    async def prompt_card_expiry_step(self, step_context: WaterfallStepContext):
        step_context.values["numero_cartao"] = step_context.result
        return await step_context.prompt(
            "cardExpiryPrompt",
            PromptOptions(
                prompt=MessageFactory.text("Digite a validade do cartão (formato MM/AAAA):"),
                retry_prompt=MessageFactory.text("Formato ou data inválida. Tente novamente:")
            )
        )
    
    async def validate_card_cvv(self, prompt_context):
        cvv = prompt_context.recognized.value.strip()
        return cvv.isdigit() and len(cvv) == 3


    async def prompt_card_cvv_step(self, step_context: WaterfallStepContext):
        step_context.values["validade"] = step_context.result
        return await step_context.prompt(
            "cardCvvPrompt",
            PromptOptions(
                prompt=MessageFactory.text("Digite o CVV do cartão (3 dígitos):"),
                retry_prompt=MessageFactory.text("CVV inválido. Tente novamente:")
            )
        )

# Abaixo, programar autenticacao do cartao para a compra do produto desejado
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext
from botbuilder.core import MessageFactory
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from api.order_api import OrderAPI
from datetime import datetime, timezone

datetime.now(timezone.utc)

class ConsultarPedidoDialog(ComponentDialog):
    def __init__(self):
        super(ConsultarPedidoDialog, self).__init__("ConsultarPedidoDialog")

        self.order_api = OrderAPI()
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
            PromptOptions(prompt=MessageFactory.text("Digite seu nome completo para consultar seus pedidos:"))
        )

    async def show_orders_step(self, step_context: WaterfallStepContext):
        user_name = step_context.result
        pedidos = self.order_api.consultar_pedidos_por_usuario(user_name)

        if pedidos and isinstance(pedidos, list):
            for pedido in pedidos:
                detalhes = f"🛒 **Pedido #{pedido['id']} - {pedido['data']}**\n"
                detalhes += f"- Produto: {pedido['produto']}\n"
                detalhes += f"- Valor: R$ {pedido['valor']:.2f}\n"
                detalhes += f"- Status: {pedido['status']}\n"
                await step_context.context.send_activity(MessageFactory.text(detalhes, None, "markdown"))
        else:
            await step_context.context.send_activity(
                MessageFactory.text(f"Nenhum pedido encontrado para o usuário '{user_name}'.", None, "markdown")
        )
        return await step_context.end_dialog()
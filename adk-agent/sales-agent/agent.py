from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from .tools import registrar_cliente, contar_registros, get_current_date
from .prompts import MODEL_SYSTEM_MESSAGE

root_agent = LlmAgent(
    name="sales-agent",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    description=(
        "Agente de ventas."
    ),
    instruction=(
        MODEL_SYSTEM_MESSAGE
    ),
    tools=[registrar_cliente, contar_registros, get_current_date],
)
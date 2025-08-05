import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from .tools import registrar_cliente, contar_registros, get_current_date
from .prompts import MODEL_SYSTEM_MESSAGE, CREATE_MEMORY_INSTRUCTION

root_agent = LlmAgent(
    name="weather_time_agent",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=(
        MODEL_SYSTEM_MESSAGE
    ),
    tools=[registrar_cliente, contar_registros, get_current_date],
)
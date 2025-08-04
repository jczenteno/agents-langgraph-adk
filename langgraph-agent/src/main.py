import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()
from src.routes.chatbot_router import router as chatbot_router
from src.llm.llm_factory import LLMFactory
from src.agent.agent import ChatbotGraph
from src.service.chatbot_service import ChatbotService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_chatbot_graph():
    try:
        logger.info("Inicializando grafo LangGraph para el chatbot...")
        
        # Creacion de la instancia de modelo LLM
        model_provider = os.getenv('MODEL_PROVIDER', 'openai')
        chat_model = LLMFactory().create_chat_model(model_provider)
        
        # Inicializacion del grafo con el modelo
        chatbot_graph = ChatbotGraph(chat_model)
        
        # Configuracion del servicio con el grafo inicializado
        ChatbotService.set_chatbot_graph(chatbot_graph)
        
        logger.info("Grafo LangGraph inicializado correctamente")
        return chatbot_graph
    except Exception as e:
        logger.error(f"Error al inicializar el grafo LangGraph: {str(e)}")
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_chatbot_graph()
    yield


app = FastAPI(
    title="Chatbot API",
    description="API for processing chatbot questions",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatbot_router)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8080, reload=True)

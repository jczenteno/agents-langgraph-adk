from typing import Callable
from fastapi import APIRouter
import httpx
import logging
from src.entities.chatbot_entities import WahaRequest
from src.mapper.waha_mapper import map_from_waha_to_langgraph, map_from_langgraph_to_waha, map_from_waha_to_adk, map_from_adk_to_waha
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/waha", tags=["waha"])

async def send_waha_message(chatId: str, text: str):
    """Send a message to WAHA API sendText endpoint"""
    try:
        payload = {
            "chatId": chatId,
            "text": text,
            "session": 'default'
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{os.getenv('WAHA_API_URL')}/api/sendText",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error sending message to WAHA: {str(e)}")
        return None


async def handle_error_response(request: WahaRequest, user_message: str, technical_message: str, chatbot_data=None):
    """Handle error response by sending WAHA message and returning error dict"""
    await send_waha_message(request.payload.from_, user_message, request.session)
    error_response = {"status": "error", "message": technical_message}
    if chatbot_data:
        error_response["chatbot_response"] = chatbot_data
    return error_response

@router.post("/webhook/langgraph", summary="Process webhook")
async def chatbot_langgraph(request: WahaRequest):
    return await webhook(request, map_from_waha_to_langgraph, map_from_langgraph_to_waha, "/api/chatbot")

@router.post("/webhook/adk", summary="Process webhook")
async def chatbot_adk(request: WahaRequest):
    # Crear una sesion en ADK
    user = request.payload.from_
    logger.info(f"Creating session for user: {user}")
    try:
        async with httpx.AsyncClient() as client:
            chatbot_response = await client.post(
                f"{os.getenv('CHATBOT_API_URL')}/apps/sales_agent/users/{user}/sessions/{user}",
                json={},
                headers={"Content-Type": "application/json"}
            )
            chatbot_response.raise_for_status()
            chatbot_data = chatbot_response.json()
        logger.info(f"Session response: {chatbot_data}")
    except Exception as e:
        logger.warning(f"An error occurred: {str(e)}")


    return await webhook(request, map_from_waha_to_adk, map_from_adk_to_waha, "/run")


async def webhook(request: WahaRequest, mapperIn: Callable, mapperOut: Callable, path: str):
    logger.info(f"Received webhook request: {request}")
    try:
        chatbot_payload = mapperIn(request)

        logger.info(f"Calling chatbot API at: {os.getenv('CHATBOT_API_URL')}")
        
        # Call the chatbot API
        async with httpx.AsyncClient() as client:
            chatbot_response = await client.post(
                f"{os.getenv('CHATBOT_API_URL')}{path}",
                json=chatbot_payload,
                headers={"Content-Type": "application/json"}
            )
            chatbot_response.raise_for_status()
            chatbot_data = chatbot_response.json()

        logger.info(f"Chatbot API response: {chatbot_data}")
        
        # Validate chatbot API response
        if chatbot_response.status_code != 200:
            return await handle_error_response(
                request,
                "Lo siento, no puedo procesar tu mensaje en este momento. Por favor intenta nuevamente más tarde.",
                f"Chatbot API error - Status code: {chatbot_response.status_code}, Status: {chatbot_data.get('status', 'unknown')}",
                chatbot_data
            )
        
        response_text = mapperOut(chatbot_data)
        
        # Send the chatbot response to WAHA
        send_data = await send_waha_message(
            chatId=request.payload.from_,
            text=response_text
        )
        
        return {
            "status": "success",
            "message": "Message processed and sent successfully",
            "chatbot_response": chatbot_data,
            "send_response": send_data
        }
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return await handle_error_response(
            request,
            "Lo siento, ocurrió un error inesperado. Por favor intenta nuevamente más tarde.",
            f"An error occurred: {str(e)}"
        )
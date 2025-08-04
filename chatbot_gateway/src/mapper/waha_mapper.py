from src.entities.chatbot_entities import WahaRequest
from typing import Dict, Any, Optional, List

def map_from_waha_to_langgraph(request: WahaRequest) -> Dict[str, str]:
    return {
        "question": request.payload.body,
        "user": request.payload.from_
    }

def map_from_langgraph_to_waha(
    user: str, 
    response_text: str, 
    session: str,
    reply_to: Optional[str] = None,
    link_preview: bool = True,
    link_preview_high_quality: bool = False
) -> Dict[str, Any]:
    return {
        "chatId": user,
        "reply_to": reply_to,
        "text": response_text,
        "linkPreview": link_preview,
        "linkPreviewHighQuality": link_preview_high_quality,
        "session": session
    }

def map_from_waha_to_adk(request: WahaRequest) -> Dict[str, Any]:
    return {
        "app_name": "sales-agent",
        "user_id": request.payload.from_,
        "session_id": request.payload.from_,
        "new_message": {
            "role": "user",
            "parts": [
                {"text": request.payload.body}
            ]
        }
    }

def map_from_adk_to_waha(adk_response: List[Dict[str, Any]]) -> str:
    """
    Extrae el texto de respuesta del formato de respuesta de ADK.
    ADK devuelve un array de objetos, tomamos el texto del primer elemento.
    """
    if not adk_response or len(adk_response) == 0:
        return "Lo siento, no pude generar una respuesta."
    
    first_response = adk_response[0]
    content = first_response.get("content", {})
    parts = content.get("parts", [])
    
    if not parts or len(parts) == 0:
        return "Lo siento, no pude generar una respuesta."
    
    return parts[0].get("text", "Lo siento, no pude generar una respuesta.")

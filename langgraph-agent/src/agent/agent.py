from typing import Dict, Any, List

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from src.agent.tools import registrar_cliente, contar_registros, get_current_date
from langgraph.prebuilt import ToolNode, tools_condition
from src.agent.prompts import MODEL_SYSTEM_MESSAGE

class ChatbotGraph:
    def __init__(self, chat_model: BaseChatModel):
        self.model = chat_model.bind_tools([registrar_cliente, contar_registros, get_current_date])
        
        # Checkpointer for short-term (within-thread) memory
        self.within_thread_memory = MemorySaver()
        
        # Construir y compilar el grafo
        self.graph = self._build_graph()
        
        # Diccionario para almacenar los thread_ids por usuario
        self.user_threads = {}
        
    def _build_graph(self):
        
        def call_model(state: MessagesState):
            
            system_msg = MODEL_SYSTEM_MESSAGE
            
            response = self.model.invoke([SystemMessage(content=system_msg)] + state["messages"])

            return {"messages": [response]} 

        # Define the graph
        builder = StateGraph(MessagesState)
        builder.add_node("call_model", call_model)
        builder.add_node("tools", ToolNode([registrar_cliente, contar_registros, get_current_date]))

        builder.add_edge(START, "call_model")
        builder.add_conditional_edges(
            "call_model",
            tools_condition,
            {"tools": "tools", END: END}
        )
        builder.add_edge("tools", "call_model")

        # Compile the graph with the checkpointer
        return builder.compile(
            checkpointer=self.within_thread_memory
        )
    
    def process_message(self, message: str, user_id: str) -> Dict[str, Any]:
        config = {"configurable": {"thread_id": user_id, "user_id": user_id}}
        input_messages = [HumanMessage(content=message)]
        result = self.graph.invoke({"messages": input_messages}, config)
        ai_message = result["messages"][-1]
        
        return {
            "answer": ai_message.content,
            "user": user_id,
            "thread_id": user_id
        }
    
    def get_chat_history(self, user_id: str) -> List[Dict[str, Any]]:
        thread = {"configurable": {"thread_id": user_id}}
        state = self.graph.get_state(thread).values

        if not state:
            return []
        
        # Convertir los mensajes a un formato más simple para la API
        formatted_messages = []
        for m in state["messages"]: 
            if isinstance(m, BaseMessage):
                formatted_messages.append({
                    "role": m.type,
                    "content": m.content
                })
        
        return formatted_messages

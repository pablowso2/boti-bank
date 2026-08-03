import json
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

# ---------------------------------------------------------
# Cargar variables de entorno desde el archivo .env
# ---------------------------------------------------------
load_dotenv()

# ==========================================
# 1. BASE DE DATOS EN MEMORIA
# ==========================================
# Todo el almacenamiento vivirá en este diccionario global en la RAM
IN_MEMORY_DB = {
    "clientes": [
        {"id": "71992c72-cc1c-4c5a-8b50-9ee4fb6c214d", "nombre": "Ana", "apellido": "García"}, 
        {"id": "88888888-cc1c-4c5a-8b50-9ee4fb6c214d", "nombre": "Pablo", "apellido": "Saga"}
    ],
    "cuentas": [
        {"cuentaId": "CTA-122", "clienteId": "71992c72-cc1c-4c5a-8b50-9ee4fb6c214d", "saldo": 1800.50}, 
        {"cuentaId": "CTA-123", "clienteId": "71992c72-cc1c-4c5a-8b50-9ee4fb6c214d", "saldo": 100.0}, 
        {"cuentaId": "CTA-999", "clienteId": "71992c72-cc1c-4c5a-8b50-9ee4fb6c214d", "saldo": 0.0}
    ],
    "movimientos": [
        {"id": "01f15ec0-b34b-18a0-88e4-fea53fe216b1", "fecha": "2026-06-02T20:21:56.456908Z", "tipo": "INGRESO", "monto": 1500.50, "descripcion": "Ingreso por ventanilla/cajero", "cuentaId": "CTA-123"}
    ],
    "servicios": [
        {"codigoServicio": "LZ1", "nombre": "Luz", "monto": 50.0, "vencimiento": "2023-12-31"}
    ],
    "hipotecas": []
}

def registrar_movimiento(cuenta_id: str, tipo: str, monto: float, descripcion: str):
    """Auxiliar para guardar movimientos directamente en memoria."""
    mov = {
        "id": str(uuid.uuid4()),
        "fecha": datetime.utcnow().isoformat() + "Z",
        "tipo": tipo,
        "monto": monto,
        "descripcion": descripcion,
        "cuentaId": cuenta_id
    }
    IN_MEMORY_DB.setdefault("movimientos", []).append(mov)

# ==========================================
# 2. DEFINICIÓN DE TOOLS PARA EL AGENTE
# ==========================================

@tool
def listar_clientes() -> str:
    """Obtiene la lista de clientes del banco."""
    return json.dumps(IN_MEMORY_DB.get("clientes", []))

@tool
def consultar_cuentas(cliente_id: str) -> str:
    """Lista las cuentas bancarias pertenecientes a un cliente dado su ID."""
    cuentas = [c for c in IN_MEMORY_DB.get("cuentas", []) if c["clienteId"] == cliente_id]
    return json.dumps(cuentas)

@tool
def ingresar_dinero(cuenta_id: str, monto: float) -> str:
    """Ingresa dinero a una cuenta bancaria específica."""
    for cuenta in IN_MEMORY_DB["cuentas"]:
        if cuenta["cuentaId"] == cuenta_id:
            cuenta["saldo"] += monto
            registrar_movimiento(cuenta_id, "INGRESO", monto, "Ingreso por agente")
            return f"Ingreso exitoso. Nuevo saldo: {cuenta['saldo']}"
    return "Error: Cuenta no encontrada."

@tool
def transferir_dinero(cuenta_origen: str, cuenta_destino: str, monto: float, concepto: str) -> str:
    """Realiza una transferencia de dinero entre dos cuentas."""
    origen, destino = None, None
    for c in IN_MEMORY_DB["cuentas"]:
        if c["cuentaId"] == cuenta_origen: origen = c
        if c["cuentaId"] == cuenta_destino: destino = c
        
    if not origen or not destino:
        return "Error: Cuenta de origen o destino no encontrada."
    if origen["saldo"] < monto:
        return "Error: Saldo insuficiente."
        
    origen["saldo"] -= monto
    destino["saldo"] += monto
    registrar_movimiento(cuenta_origen, "TRANSFERENCIA_ENVIADA", monto, concepto)
    registrar_movimiento(cuenta_destino, "TRANSFERENCIA_RECIBIDA", monto, concepto)
    return f"Transferencia exitosa. Saldo restante en cuenta origen: {origen['saldo']}"

@tool
def listar_servicios() -> str:
    """Lista los servicios disponibles para pagar (luz, agua, etc.)."""
    return json.dumps(IN_MEMORY_DB.get("servicios", []))

@tool
def pagar_servicio(cuenta_origen: str, codigo_servicio: str) -> str:
    """Paga un servicio (luz, gas) descontando el dinero de una cuenta."""
    servicio = next((s for s in IN_MEMORY_DB["servicios"] if s["codigoServicio"] == codigo_servicio), None)
    if not servicio: return "Error: Servicio no encontrado."
    
    for cuenta in IN_MEMORY_DB["cuentas"]:
        if cuenta["cuentaId"] == cuenta_origen:
            if cuenta["saldo"] < servicio["monto"]:
                return "Error: Saldo insuficiente."
            
            cuenta["saldo"] -= servicio["monto"]
            registrar_movimiento(cuenta_origen, "PAGO_SERVICIO", servicio["monto"], f"Pago de servicio: {servicio['nombre']}")
            IN_MEMORY_DB["servicios"] = [s for s in IN_MEMORY_DB["servicios"] if s["codigoServicio"] != codigo_servicio]
            return f"Servicio {servicio['nombre']} pagado con éxito. Nuevo saldo: {cuenta['saldo']}"
    return "Error: Cuenta origen no encontrada."

@tool
def pagar_hipoteca(cuenta_origen: str, id_hipoteca: str, monto: float) -> str:
    """Realiza el pago de una cuota de hipoteca."""
    hipoteca = next((h for h in IN_MEMORY_DB.get("hipotecas", []) if h["id"] == id_hipoteca), None)
    if not hipoteca: return "Error: Hipoteca no encontrada."
    
    for cuenta in IN_MEMORY_DB["cuentas"]:
        if cuenta["cuentaId"] == cuenta_origen:
            if cuenta["saldo"] < monto:
                return "Error: Saldo insuficiente."
            
            cuenta["saldo"] -= monto
            hipoteca["balancePendiente"] -= monto
            registrar_movimiento(cuenta_origen, "PAGO_HIPOTECA", monto, f"Pago de hipoteca: {id_hipoteca}")
            return f"Hipoteca pagada. Balance restante de la hipoteca: {hipoteca['balancePendiente']}"
    return "Error: Cuenta origen no encontrada."

# Agrupamos las tools
tools = [
    listar_clientes, consultar_cuentas, ingresar_dinero, transferir_dinero, 
    listar_servicios, pagar_servicio, pagar_hipoteca
]

# ==========================================
# 3. CONFIGURACIÓN DEL GRAFO Y AGENTE
# ==========================================

# Leer configuración del modelo desde el .env
LLM_API_KEY = os.getenv("MODEL_API_KEY", "sk-mi-clave-secreta-123")
LLM_BASE_URL = os.getenv("MODEL_BASE_URL", "http://127.0.0.1:8081/v1")
LLM_MODEL_NAME = os.getenv("MODEL_NAME", "hermes-2-pro-llama3-8b")

llm = ChatOpenAI(
    base_url=LLM_BASE_URL,
    api_key=LLM_API_KEY,
    model=LLM_MODEL_NAME,
    temperature=0.0
)
llm_with_tools = llm.bind_tools(tools)

system_prompt = SystemMessage(content="""
Eres el asistente virtual inteligente de BotiBank. Tienes acceso a herramientas 
para consultar clientes, cuentas, realizar transferencias, ingresos, y pagos de servicios/hipotecas. 
Usa las herramientas siempre que sea necesario para realizar acciones o consultar datos reales en nombre del usuario.
Responde de manera cordial y profesional.
""")

def agent_node(state: MessagesState):
    messages = state["messages"]
    if not isinstance(messages[0], SystemMessage):
        messages = [system_prompt] + messages
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: MessagesState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

workflow = StateGraph(MessagesState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

checkpointer = MemorySaver()
botibank_agent = workflow.compile(checkpointer=checkpointer)

# ==========================================
# 4. FASTAPI ENDPOINTS
# ==========================================

app = FastAPI(title="BotiBank AI Agent", version="1.2.0")

class ChatRequest(BaseModel):
    thread_id: str = Field(..., description="ID del chat para mantener el historial")
    message: str = Field(..., description="El mensaje o instrucción del usuario")

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    run_config = {"configurable": {"thread_id": req.thread_id}}
    
    input_message = HumanMessage(content=req.message)
    
    try:
        final_state = await botibank_agent.ainvoke(
            {"messages": [input_message]}, 
            config=run_config
        )
        
        last_message = final_state["messages"][-1].content
        return ChatResponse(response=last_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    # Leer configuración del servidor desde el .env
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run("main:app", host=host, port=port, reload=True)
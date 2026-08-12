import json
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

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
        {"id": "71992c72-cc1c-4c5a-8b50-9ee4fb6c214d", "nombre": "Ana", "apellido": "García", "email": "ana@ejemplo.com"},
        {"id": "88888888-cc1c-4c5a-8b50-9ee4fb6c214d", "nombre": "Pablo", "apellido": "Saga", "email": "pablo@ejemplo.com"},
        {"id": "33333333-cc1c-4c5a-8b50-9ee4fb6c214d", "nombre": "Carlos", "apellido": "Pérez", "email": "carlos@ejemplo.com"}
    ],
    "cuentas": [
        {"cuentaId": "CTA-122", "clienteId": "71992c72-cc1c-4c5a-8b50-9ee4fb6c214d", "saldo": 1800.50, "tipo": "Corriente"},
        {"cuentaId": "CTA-123", "clienteId": "71992c72-cc1c-4c5a-8b50-9ee4fb6c214d", "saldo": 100.0, "tipo": "Ahorro"},
        {"cuentaId": "CTA-999", "clienteId": "71992c72-cc1c-4c5a-8b50-9ee4fb6c214d", "saldo": 0.0, "tipo": "Inversión"},
        {"cuentaId": "CTA-444", "clienteId": "88888888-cc1c-4c5a-8b50-9ee4fb6c214d", "saldo": 5000.00, "tipo": "Sueldo"},
        {"cuentaId": "CTA-555", "clienteId": "33333333-cc1c-4c5a-8b50-9ee4fb6c214d", "saldo": 250.00, "tipo": "Ahorro"}
    ],
    "movimientos": [
        # --- Movimientos de Ana: CTA-122 ---
        {"id": "m-101", "fecha": "2026-01-05T10:00:00Z", "tipo": "INGRESO", "monto": 1500.00, "descripcion": "Acreditación de sueldo", "cuentaId": "CTA-122"},
        {"id": "m-102", "fecha": "2026-01-10T15:30:00Z", "tipo": "EGRESO", "monto": 250.00, "descripcion": "Pago de servicio de luz", "cuentaId": "CTA-122"},
        {"id": "m-103", "fecha": "2026-02-01T09:15:00Z", "tipo": "INGRESO", "monto": 650.50, "descripcion": "Transferencia recibida de Carlos", "cuentaId": "CTA-122"},
        {"id": "m-104", "fecha": "2026-02-15T18:45:00Z", "tipo": "EGRESO", "monto": 100.00, "descripcion": "Extracción en cajero automático", "cuentaId": "CTA-122"},

        # --- Movimientos de Ana: CTA-123 ---
        {"id": "m-201", "fecha": "2026-01-08T11:20:00Z", "tipo": "INGRESO", "monto": 200.00, "descripcion": "Depósito por ventanilla", "cuentaId": "CTA-123"},
        {"id": "m-202", "fecha": "2026-01-12T14:10:00Z", "tipo": "EGRESO", "monto": 50.00, "descripcion": "Compra en supermercado", "cuentaId": "CTA-123"},
        {"id": "m-203", "fecha": "2026-02-05T10:05:00Z", "tipo": "INGRESO", "monto": 300.00, "descripcion": "Transferencia recibida", "cuentaId": "CTA-123"},
        {"id": "m-204", "fecha": "2026-02-20T16:30:00Z", "tipo": "EGRESO", "monto": 150.00, "descripcion": "Pago de tarjeta de crédito", "cuentaId": "CTA-123"},

        # --- Movimientos de Ana: CTA-999 (Inversión) ---
        {"id": "m-301", "fecha": "2026-01-02T09:00:00Z", "tipo": "INGRESO", "monto": 1000.00, "descripcion": "Apertura de cuenta fondo de inversión", "cuentaId": "CTA-999"},
        {"id": "m-302", "fecha": "2026-01-15T12:00:00Z", "tipo": "EGRESO", "monto": 1000.00, "descripcion": "Transferencia enviada a cuenta principal", "cuentaId": "CTA-999"},
        {"id": "m-303", "fecha": "2026-03-01T10:00:00Z", "tipo": "INGRESO", "monto": 50.00, "descripcion": "Intereses ganados", "cuentaId": "CTA-999"},
        {"id": "m-304", "fecha": "2026-03-02T11:00:00Z", "tipo": "EGRESO", "monto": 50.00, "descripcion": "Cobro de mantenimiento de cuenta", "cuentaId": "CTA-999"},

        # --- Movimientos de Pablo: CTA-444 ---
        {"id": "m-401", "fecha": "2026-01-10T08:30:00Z", "tipo": "INGRESO", "monto": 6000.00, "descripcion": "Acreditación de sueldo", "cuentaId": "CTA-444"},
        {"id": "m-402", "fecha": "2026-01-15T09:15:00Z", "tipo": "EGRESO", "monto": 1200.00, "descripcion": "Pago cuota hipoteca HIP-002", "cuentaId": "CTA-444"},
        {"id": "m-403", "fecha": "2026-02-10T08:30:00Z", "tipo": "INGRESO", "monto": 6000.00, "descripcion": "Acreditación de sueldo", "cuentaId": "CTA-444"},
        {"id": "m-404", "fecha": "2026-02-20T19:20:00Z", "tipo": "EGRESO", "monto": 800.00, "descripcion": "Compra pasajes aéreos", "cuentaId": "CTA-444"},

        # --- Movimientos de Carlos: CTA-555 ---
        {"id": "m-501", "fecha": "2026-01-05T13:00:00Z", "tipo": "INGRESO", "monto": 500.00, "descripcion": "Depósito en efectivo", "cuentaId": "CTA-555"},
        {"id": "m-502", "fecha": "2026-01-20T17:45:00Z", "tipo": "EGRESO", "monto": 100.00, "descripcion": "Extracción en cajero automático", "cuentaId": "CTA-555"},
        {"id": "m-503", "fecha": "2026-02-10T12:30:00Z", "tipo": "INGRESO", "monto": 250.00, "descripcion": "Transferencia recibida de Ana", "cuentaId": "CTA-555"},
        {"id": "m-504", "fecha": "2026-03-05T14:15:00Z", "tipo": "EGRESO", "monto": 200.00, "descripcion": "Pago de servicio de internet", "cuentaId": "CTA-555"}
    ],
    "servicios": [
        {"codigoServicio": "LZ1", "nombre": "Luz", "monto": 50.0, "vencimiento": "2026-12-31"},
        {"codigoServicio": "AG2", "nombre": "Agua", "monto": 25.50, "vencimiento": "2026-11-15"},
        {"codigoServicio": "IN3", "nombre": "Internet", "monto": 40.0, "vencimiento": "2026-10-30"}
    ],
    "hipotecas": [
        {"id": "HIP-001", "clienteId": "71992c72-cc1c-4c5a-8b50-9ee4fb6c214d", "montoOriginal": 150000.0, "balancePendiente": 145000.0, "cuotaMensual": 800.0},
        {"id": "HIP-002", "clienteId": "88888888-cc1c-4c5a-8b50-9ee4fb6c214d", "montoOriginal": 200000.0, "balancePendiente": 50000.0, "cuotaMensual": 1200.0}
    ]
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

REGLAS CRÍTICAS DE OPERACIÓN:
1. ERES COMPLETAMENTE AUTÓNOMO: Nunca pidas permiso ni confirmación al usuario para ejecutar una herramienta.
2. Si el usuario te pide realizar una acción (como pagar un servicio, transferir dinero o consultar un saldo) y tienes los datos necesarios (como IDs de cuenta o códigos), DEBES EJECUTAR LA HERRAMIENTA INMEDIATAMENTE.
3. Solo debes responder con texto al usuario DESPUÉS de haber ejecutado la herramienta y obtenido el resultado de la base de datos.
4. Responde de manera cordial y profesional basándote en los resultados que devuelvan las herramientas.
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

# NOTE: field names/requiredness here must match the OpenAPI schema
# registered for this component's /chat endpoint in Agent Manager
# (message + session_id required, context optional) — otherwise the
# gateway's requests get rejected with 422 before they ever reach the graph.
class ChatRequest(BaseModel):
    message: str = Field(..., description="El mensaje o instrucción del usuario")
    session_id: str = Field(..., description="ID de sesión para mantener el historial")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Contexto opcional en formato JSON")

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    run_config = {"configurable": {"thread_id": req.session_id}}

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

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))

    uvicorn.run("main:app", host=host, port=port)
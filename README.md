# ⚡ BOTIBANK AI AGENT // NEXT-GEN FINTECH ORCHESTRATOR ⚡

![Cyberpunk Fintech Banner](https://img.shields.io/badge/ARCHITECTURE-LANGGRAPH%20%2F%2F%20FASTAPI-00F0FF?style=for-the-badge&labelColor=0D0E15)
![AI Engine](https://img.shields.io/badge/LLM-LOCAL%20%2F%2F%20OPENAI%20COMPATIBLE-FF0055?style=for-the-badge&labelColor=0D0E15)
![Memory](https://img.shields.io/badge/STATE-IN--MEMORY%20RAM-00FF66?style=for-the-badge&labelColor=0D0E15)
![Python](https://img.shields.io/badge/PYTHON-3.10+-7928CA?style=for-the-badge&labelColor=0D0E15)

> *"El punto de convergencia entre la banca transaccional de alta velocidad y el razonamiento autónomo por Inteligencia Artificial."*

**BotiBank AI Agent** es un núcleo bancario conversacional impulsado por **LangGraph** y expuesto mediante **FastAPI**. Diseñado bajo una arquitectura 100% en memoria (*In-Memory RAM*) para latencia cero, el agente es capaz de razonar, consultar estados financieros y ejecutar operaciones transaccionales complejas de forma autónoma mediante *Function Calling / Tools*.

---

## 🧠 Capacidades Funcionales // TOOL MATRIX

El agente posee un set de herramientas nativas vinculadas directamente a la lógica del *core* bancario, con validaciones en tiempo real de saldos, identidad y límites operativos:

| Herramienta | Capacidad | Descripción |
| :--- | :--- | :--- |
| 🛡️ `listar_clientes` | **Identidad & Onboarding** | Consulta el registro central de usuarios y devuelve identidades activas en el sistema. |
| 💎 `consultar_cuentas` | **Posición Consolidada** | Mapea y lista todas las cuentas bancarias y balances exactos asociados a un `cliente_id`. |
| ⚡ `ingresar_dinero` | **Inyección de Liquidez** | Procesa depósitos en tiempo real sobre una cuenta, generando el recibo y auditoría de movimiento. |
| 🔄 `transferir_dinero` | **Liquidación Interbancaria** | Ejecuta transferencias P2P verificando saldo suficiente en el emisor, con registro dual (enviado/recibido). |
| 📡 `listar_servicios` | **Catálogo de Servicios** | Escanea los servicios conectados (Luz, Agua, Gas) que tienen facturas o recibos pendientes. |
| 💳 `pagar_servicio` | **Clearing Automático** | Liquida facturas de servicios debitando del saldo disponible y eliminando el pasivo en el acto. |
| 🏛️ `pagar_hipoteca` | **Amortización de Créditos** | Procesa pagos parciales de deuda hipotecaria, recalculando el balance pendiente al milisegundo. |

---

## 🏗️ Arquitectura del Sistema
+-------------------------------------------------------------------+
|                         CLIENT LAYER                              |
|          (cURL / Swagger UI / Web App / Mobile App)               |
+-------------------------------------------------------------------+
|
HTTP POST /chat [Payload: JSON]
v
+-------------------------------------------------------------------+
|                      FASTAPI GATEWAY                              |
|   - Validación de esquema Pydantic                                |
|   - Inyección del Thread ID para persistencia conversacional     |
+-------------------------------------------------------------------+
|
v
+-------------------------------------------------------------------+
|               LANGGRAPH COGNITIVE ENGINE                          |
|                                                                   |
|   [ START ] ---> ( AGENT NODE: LLM Reasoning )                    |
|                        |             ^                            |
|                 ¿Requiere Tool?      |                            |
|                    /        \        |                            |
|               [SÍ]/          [NO]   |                            |
|                  v            v      |                            |
|         ( TOOL NODE )      [ END ]   |                            |
|                  |                   |                            |
|                  +-------------------+                            |
+-------------------------------------------------------------------+
|
Lectura / Escritura Sub-milisegundo (Zero-Disk)
v
+-------------------------------------------------------------------+
|               IN-MEMORY CORE BANKING DB (RAM)                     |
|     { clientes: [...], cuentas: [...], movimientos: [...] }       |
+-------------------------------------------------------------------+

---

## ⚙️ Configuración del Entorno // SETUP

El sistema está diseñado para ser agnóstico al modelo (*Model-Agnostic*): puedes apuntarlo tanto a **LLMs Locales** (Llama 3, Qwen, Hermes corriendo en tu `llama-server`) como a **OpenAI**.

### 1. Instalación de Dependencias

Asegúrate de contar con Python 3.10+ y ejecuta:

```bash
pip install fastapi uvicorn pydantic python-dotenv langchain-openai langgraph

# ENGINE CONFIG
MODEL_API_KEY=not-needed
MODEL_BASE_URL=[http://127.0.0.1:8081/v1](http://127.0.0.1:8081/v1)
MODEL_NAME=hermes-2-pro-llama3-8b

# SERVER GATEWAY CONFIG
API_HOST=127.0.0.1
API_PORT=8000
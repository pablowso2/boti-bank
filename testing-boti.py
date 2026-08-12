import requests
import json
import time

# ==========================================
# CONFIGURACIÓN
# ==========================================
URL = "https://development-wc-019e6383-b65fad2b.agent-manager.us-east-2.cloud.wso2.com:443/botibank-xz-botibank-xz-endpoint/chat"

HEADERS = {
    "Content-Type": "application/json"
}

SESSION_ID = "sesion-automatica-002"

# ==========================================
# PREGUNTAS AUTOMÁTICAS (Basadas en tu data)
# ==========================================
PREGUNTAS_BASE = [
    # --- 1. Consultas Generales ---
    "Por favor, enumera a todos los clientes del banco.",
    "¿Me puedes decir cuáles son las cuentas bancarias y los saldos de la clienta Ana, con ID 71992c72-cc1c-4c5a-8b50-9ee4fb6c214d?",
    "¿Qué cuentas tiene registradas el cliente Pablo (ID: 88888888-cc1c-4c5a-8b50-9ee4fb6c214d)?",
    
    # --- 2. Ingreso de Dinero ---
    "Necesito hacer un depósito. Por favor, ingresa 500 en la cuenta CTA-999.",
    
    # --- 3. Transferencias (Éxito y Error) ---
    "Necesito hacer una transferencia de 200 desde la cuenta CTA-122 hacia la cuenta CTA-123 con el concepto 'Préstamo personal'.",
    "Intenta transferir 5000 desde la cuenta CTA-123 a la cuenta CTA-122 con el concepto 'Compra de auto'.", # Debe fallar por saldo insuficiente
    
    # --- 4. Pago de Servicios (Éxito y Error) ---
    "¿Qué servicios públicos tienen disponibles para pagar?",
    "Intenta pagar el servicio de luz (código LZ1) utilizando la cuenta CTA-999, por favor.", # Debe fallar porque la cuenta tiene 0.0 de saldo
    "Por favor, paga el servicio de luz (código LZ1) utilizando mi cuenta CTA-122.",
    
    # --- 5. Hipotecas (Error de existencia) ---
    "Quiero pagar 300 de mi hipoteca con ID HIP-001 usando la cuenta CTA-122." # Debe fallar porque la lista de hipotecas está vacía
]

def ejecutar_pruebas_automaticas():
    print("=" * 60)
    print("🤖 AUTOMATIZADOR DE PRUEBAS A2A - BOTIBANK")
    print("=" * 60)
    
    # 1. Pedir la cantidad de preguntas a ejecutar
    while True:
        try:
            cantidad_preguntas = int(input("¿Cuántas preguntas automáticas deseas enviar al agente?: "))
            if cantidad_preguntas > 0:
                break
            else:
                print("Por favor, ingresa un número mayor a 0.")
        except ValueError:
            print("Entrada inválida. Debes ingresar un número entero.")

    print(f"\n🚀 Iniciando batería de {cantidad_preguntas} pregunta(s) automáticas.")
    print("-" * 60)

    # 2. Ciclo de ejecución
    for i in range(cantidad_preguntas):
        # Usamos el operador módulo (%) para repetir las preguntas si 'cantidad' es mayor que la lista
        pregunta_actual = PREGUNTAS_BASE[i % len(PREGUNTAS_BASE)]
        
        print(f"\n▶ PREGUNTA {i + 1} DE {cantidad_preguntas}")
        print(f"✍️  Enviando: {pregunta_actual}")
        
        payload = {
            "message": pregunta_actual,
            "session_id": SESSION_ID
        }

        # --- INICIO DEL TRACKING ---
        print("\n" + "." * 60)
        print("🔍 [TRACK] ENVIANDO PETICIÓN (REQUEST)")
        print(f"URL     : {URL}")
        print(f"Headers : {json.dumps(HEADERS, indent=2)}")
        print(f"Body    : {json.dumps(payload, indent=2, ensure_ascii=False)}")
        print("." * 60)

        try:
            # Enviamos la petición
            response = requests.post(URL, headers=HEADERS, json=payload, timeout=30)
            
            # --- SEGUIMIENTO DE LA RESPUESTA ---
            print("\n🔍 [TRACK] RESPUESTA RECIBIDA (RESPONSE)")
            print(f"Status Code : {response.status_code}")
            
            try:
                raw_json = response.json()
                print(f"Raw JSON    :\n{json.dumps(raw_json, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError:
                print(f"Raw Text    : {response.text}")
            print("." * 60)

            # Validar si hubo error HTTP
            response.raise_for_status()
            
            # 3. Mostrar la respuesta final del agente
            respuesta_agente = raw_json.get("response", "[No se encontró el campo 'response']")
            print(f"\n🤖 BotiBank: {respuesta_agente}\n")
            print("-" * 60)

        except requests.exceptions.RequestException as e:
            print(f"\n❌ ERROR EN LA COMUNICACIÓN: {e}\n")
            print("-" * 60)
            
        # Pequeña pausa para no saturar el servidor ni el modelo de IA
        time.sleep(2)

    print("\n✅ Batería de pruebas automáticas finalizada.")

if __name__ == "__main__":
    ejecutar_pruebas_automaticas()
python3 -m venv .
python -m pip install -r requirements.txt
python main.py

curl -X 'POST' \
  'http://127.0.0.1:8000/chat' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "thread_id": "user_123",
  "message": "Hola, ¿puedes listar los clientes del banco?"
}'


Lista de tools
listar_clientes: Obtiene y devuelve la lista completa de clientes registrados en el banco.

consultar_cuentas: Requiere un cliente_id y devuelve todas las cuentas bancarias asociadas a ese cliente, incluyendo sus saldos.

ingresar_dinero: Permite depositar fondos. Requiere el cuenta_id y el monto a ingresar. Actualiza el saldo y registra el movimiento.

transferir_dinero: Permite mover fondos entre cuentas. Requiere la cuenta_origen, la cuenta_destino, el monto y un concepto. Valida que haya saldo suficiente antes de ejecutarla.

listar_servicios: Muestra el catálogo de servicios adheridos que están pendientes de pago (como luz, agua, etc.) y sus montos.

pagar_servicio: Requiere la cuenta_origen y el codigo_servicio. Descuenta el monto de la cuenta, elimina el servicio de la lista de pendientes y registra la operación.

pagar_hipoteca: Requiere la cuenta_origen, el id_hipoteca y el monto de la cuota. Resta el dinero de la cuenta del cliente y disminuye el balance pendiente de la hipoteca.
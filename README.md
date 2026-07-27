curl -X 'POST' \
  'http://127.0.0.1:8000/chat' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "thread_id": "user_123",
  "message": "Hola, ¿puedes listar los clientes del banco?"
}'
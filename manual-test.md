

curl -X POST "https://development-wc-019e6383-b65fad2b.agent-manager.us-east-2.cloud.wso2.com:443/botibank-xz-botibank-xz-endpoint/chat" \
     -H "Content-Type: application/json" \
     -d '{
           "message": "Please, list me the client of the bank",
           "session_id": "test-session-123"
         }'
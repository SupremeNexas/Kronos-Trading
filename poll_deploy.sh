for i in {1..30}; do
  status=$(curl -s https://api.render.com/v1/services/srv-daujihjncjis73fsmih0/deploys -H "Authorization: Bearer <placeholder>" | grep -o '"status":"[^"]*"' | head -1)
  echo "Current status: $status"
  sleep 10
done

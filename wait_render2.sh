for i in {1..7}; do
  status=$(curl -s -o /dev/null -w "%{http_code}" https://kronos-trading-ai.onrender.com/health)
  if [ "$status" = "200" ]; then
    echo "Render is ready!"
    break
  fi
  sleep 10
done

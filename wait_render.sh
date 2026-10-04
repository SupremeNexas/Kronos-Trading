#!/bin/bash
while true; do
  STATUS=$(curl -s "https://api.render.com/v1/services/srv-daujihjncjis73fsmih0/deploys/dep-davusr7f3r2c73agpf6g" -H "Authorization: Bearer $RENDER_API_KEY")
  echo $STATUS | grep -q '"status":"build_in_progress"'
  if [ $? -ne 0 ]; then
    echo "Deploy finished."
    break
  fi
  sleep 5
done

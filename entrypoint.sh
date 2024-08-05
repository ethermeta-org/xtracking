#!/bin/bash

trap stop SIGINT SIGTERM

if [ -e "/opt/xtrack/config.yaml" ]; then
  echo "/opt/xtrack/config.yaml already exists."
else
  cp /opt/config.yaml /opt/xtrack/
  echo "copy /opt/config.yaml /opt/xtrack/"
fi

#exec /start.sh
exec uvicorn --reload --host "0.0.0.0" --port "8011" "app.main:app"


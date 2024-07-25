#!/bin/bash

trap stop SIGINT SIGTERM

if [ -e "/app/config.yaml" ]; then
  echo "/app/config.yaml already exists."
else
  cp /opt/config.yaml /app/
  echo "copy /opt/config.yaml /app/"
fi


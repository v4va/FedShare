#!/bin/bash

export PYTHONUNBUFFERED=1

N=2
M=5

DEST_DIRECTORY="scotch-mnist-client-${M}-server-${N}"
echo "$DEST_DIRECTORY"
mkdir -p logs/${DEST_DIRECTORY}

nohup python logger_server.py &>logs/${DEST_DIRECTORY}/logger_server.log &

for ((SERVER = 0; SERVER < N; SERVER++)); do
  echo "Running server ${CLIENT}"
  nohup python scotchserver.py "${SERVER}" &>"logs/${DEST_DIRECTORY}/scotchserver-${SERVER}.log" &
done

for ((CLIENT = 0; CLIENT < M; CLIENT++)); do
  echo "Running client ${CLIENT}"
  nohup python scotchclient.py "${CLIENT}" &>"logs/${DEST_DIRECTORY}/scotchclient-${CLIENT}.log" &
done

python flask_starter.py

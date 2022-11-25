#!/bin/bash

export PYTHONUNBUFFERED=1

N=2
M=5

DEST_DIRECTORY="fedshare-mnist-client-${M}-server-${N}"
echo "$DEST_DIRECTORY"
mkdir -p logs/${DEST_DIRECTORY}

nohup python logger_server.py &>logs/${DEST_DIRECTORY}/logger_server.log &

nohup python fedshareleadserver.py &>logs/${DEST_DIRECTORY}/fedshareleadserver.log &

for ((SERVER = 0; SERVER < N; SERVER++)); do
  echo "Running server ${CLIENT}"
  nohup python fedshareserver.py "${SERVER}" &>"logs/${DEST_DIRECTORY}/fedshareserver-${SERVER}.log" &
done

for ((CLIENT = 0; CLIENT < M; CLIENT++)); do
  echo "Running client ${CLIENT}"
  nohup python fedshareclient.py "${CLIENT}" &>"logs/${DEST_DIRECTORY}/fedshareclient-${CLIENT}.log" &
done

python flask_starter.py

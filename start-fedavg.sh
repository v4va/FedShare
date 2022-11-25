#!/bin/bash

export PYTHONUNBUFFERED=1

M=5

DEST_DIRECTORY="logs/fedavg-mnist-client-${M}"
echo "$DEST_DIRECTORY"
mkdir -p ${DEST_DIRECTORY}

nohup python logger_server.py > ${DEST_DIRECTORY}/logger_server.log &

echo "Running server"
nohup python fedavgserver.py > ${DEST_DIRECTORY}/fedavgserver.log &

for ((CLIENT = 0; CLIENT < M; CLIENT++)); do
  echo "Running client ${CLIENT}"
  nohup python fedavgclient.py "${CLIENT}" > "${DEST_DIRECTORY}/fedavgclient-${CLIENT}.log" &
done

python flask_starter.py
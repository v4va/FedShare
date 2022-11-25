import pickle
import threading

import numpy as np
from flask import Flask, request

import flcommon
import time_logger
from config import FedAvgServerConfig

api = Flask(__name__)

config = FedAvgServerConfig()

clients_secret = []

total_download_cost = 0
total_upload_cost = 0


@api.route('/recv', methods=['POST'])
def recv():
    my_thread = threading.Thread(target=recv_thread, args=(request.data, request.remote_addr, clients_secret))
    my_thread.start()
    return {"response": "ok"}


def recv_thread(data, address, clients_secret: list):
    time_logger.server_received()

    len_joined_data = len(data)
    print(f"[DOWNLOAD] Secret of {address} received. size: {len_joined_data}")

    global total_download_cost
    total_download_cost += len_joined_data

    secret = pickle.loads(data)
    clients_secret.append(secret)

    if len(clients_secret) != config.number_of_clients:
        return

    time_logger.server_start()

    model = {}
    for layer_index in range(len(clients_secret[0])):
        alpha_list = []
        for client_index in range(len(clients_secret)):
            alpha = clients_secret[client_index][layer_index] * \
                    (config.clients_dataset_size[client_index] / config.total_dataset_size)
            alpha_list.append(alpha)
        model[layer_index] = np.array(alpha_list).sum(axis=0, dtype=np.float64)

    clients_secret.clear()
    pickle_model = pickle.dumps(model)
    flcommon.broadcast_to_clients(pickle_model, config, False)

    global total_upload_cost
    total_upload_cost += len(pickle_model) * config.number_of_clients

    print(f"[DOWNLOAD] Total download cost so far: {total_download_cost}")
    print(f"[UPLOAD] Total upload cost so far: {total_upload_cost}")

    print(f"********************** [ROUND] Round completed **********************")
    time_logger.server_idle()


api.run(host=config.server_address, port=config.fedavg_server_port, debug=True, threaded=True)

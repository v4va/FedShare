import pickle
import sys
import threading

import numpy as np
import requests
from flask import Flask, request
from requests_toolbelt.adapters import source

import time_logger
from config import ServerConfig

config = ServerConfig(int(sys.argv[1]))

api = Flask(__name__)

training_round = 0

clients_secret = []
clients_duration = []

total_download_cost = 0
total_upload_cost = 0


def recv_thread(clients_secret, data, remote_addr):
    time_logger.server_received()

    global total_download_cost
    total_download_cost += len(data)

    print(f"[DOWNLOAD] Secret of {remote_addr} received. size: {len(data)}")
    secret = pickle.loads(data)
    clients_secret.append(secret)
    print(f"[SECRET] Secret opened successfully.")

    if len(clients_secret) != config.number_of_clients:
        return

    time_logger.server_start()

    model = {}
    for layer_index in range(len(clients_secret[0])):
        alpha_list = []
        for client_index in range(config.number_of_clients):
            alpha = clients_secret[client_index][layer_index] * \
                    (config.clients_dataset_size[client_index] / config.total_dataset_size)
            alpha_list.append(alpha)
        model[layer_index] = np.array(alpha_list).sum(axis=0, dtype=np.float64)

    pickle_model = pickle.dumps(model)
    len_dumped_model = len(pickle_model)

    time_logger.server_start_upload()

    global total_upload_cost
    total_upload_cost += len(pickle_model)

    url = f'http://{config.master_server_address}:{config.master_server_port}/recv'
    s = requests.Session()
    new_source = source.SourceAddressAdapter(config.server_address)
    s.mount('http://', new_source)
    print(s.post(url, pickle_model).json())

    clients_secret.clear()

    global training_round
    training_round += 1

    print(f"[UPLOAD] Sent aggregated weights to the master, size: {len_dumped_model}")

    print(f"[DOWNLOAD] Total download cost so far: {total_download_cost}")
    print(f"[UPLOAD] Total upload cost so far: {total_upload_cost}")

    print(f"********************** [ROUND] Round {training_round} completed **********************")



    time_logger.server_idle()


@api.route('/recv', methods=['POST'])
def recv():
    my_thread = threading.Thread(target=recv_thread, args=(clients_secret,
                                                           request.data, request.remote_addr))
    my_thread.start()
    return {"response": "ok"}


api.run(host=config.server_address, port=int(config.server_base_port) + int(sys.argv[1]), debug=True, threaded=True)

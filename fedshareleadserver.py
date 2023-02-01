import pickle
import threading
import time

import numpy as np
from flask import Flask, request

import flcommon
import time_logger
from config import LeadConfig

api = Flask(__name__)

config = LeadConfig()

run_start_time = time.time()

total_upload_cost = 0
total_download_cost = 0

servers_secret = []


@api.route('/recv', methods=['POST'])
def recv():
    my_thread = threading.Thread(target=recv_thread, args=(servers_secret, request.data, request.remote_addr))
    my_thread.start()
    return {"response": "ok"}


def recv_thread(servers_secret, data, remote_addr):
    global total_download_cost
    total_download_cost += len(data)

    time_logger.lead_server_received()

    print(f"[DOWNLOAD] Secret of {remote_addr} received. size: {len(data)}")

    secret = pickle.loads(data)
    servers_secret.append(secret)

    print(f"[SECRET] Secret opened successfully.")

    if len(servers_secret) != config.num_servers:
        return {"response": "ok"}

    time_logger.lead_server_start()

    fedshare_weights = [None] * len(servers_secret[0])

    for layer_index in range(len(servers_secret[0])):
        layer_list = []
        for server_index in range(config.num_servers):
            layer_list.append(servers_secret[server_index][layer_index])
        fedshare_weights[layer_index] = np.array(layer_list).sum(axis=0, dtype=np.float64)

    servers_secret.clear()

    pickle_model = pickle.dumps(fedshare_weights)
    flcommon.broadcast_to_clients(pickle_model, config, lead_server=True)

    global total_upload_cost
    total_upload_cost += len(pickle_model) * config.number_of_clients

    print(f"[DOWNLOAD] Total download cost so far: {total_download_cost}")
    print(f"[UPLOAD] Total upload cost so far: {total_upload_cost}")

    print("[AGGREGATION] Model aggregation completed successfully.")

    time_logger.lead_server_idle()


api.run(host=config.master_server_address, port=int(config.master_server_port), debug=True, threaded=True)

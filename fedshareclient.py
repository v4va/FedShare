import pickle
import sys
import threading

import numpy as np
import requests
from flask import Flask, request
from requests_toolbelt.adapters import source

import flcommon
import mnistcommon
import time_logger
from config import ClientConfig

config = ClientConfig(int(sys.argv[1]))

client_datasets = mnistcommon.load_train_dataset(config.number_of_clients, permute=True)

field_size = np.finfo('float32').max
highest_range = np.finfo('float16').max

api = Flask(__name__)

round_weight = 0
training_round = 0
total_upload_cost = 0
total_download_cost = 0


def send_to_server(training_round, server, serialized_model):
    url = f'http://{config.server_address}:{config.server_base_port + server}/recv'
    s = requests.Session()
    new_source = source.SourceAddressAdapter(flcommon.get_ip(config))
    s.mount('http://', new_source)
    print(s.post(url, serialized_model[server]).json())

    print(f"Sent {training_round} to server {server}")


def start_next_round(data):
    time_logger.client_start()

    x_train, y_train = client_datasets[config.client_index][0], client_datasets[config.client_index][1]

    model = mnistcommon.get_model()
    global training_round
    if training_round != 0:
        global round_weight
        round_weight = pickle.loads(data)
        model.set_weights(round_weight)

    print(
        f"Model: FedShare, "
        f"Round: {training_round + 1}/{config.training_rounds}, "
        f"Client {config.client_index + 1}/{config.number_of_clients}, "
        f"Dataset Size: {len(x_train)}")
    model.fit(x_train, y_train, epochs=config.epochs, batch_size=config.batch_size, verbose=config.verbose,
              validation_split=config.validation_split)
    round_weight = np.array(model.get_weights())

    all_servers = []
    servers_model = []

    for server_index in range(config.num_servers):
        all_servers.append({})
        servers_model.append({})

    layer_dict, layer_shape, shares_dict = {}, {}, {}
    data = round_weight
    no_of_layers = len(data)
    for layer_index in range(no_of_layers):
        layer_dict[layer_index] = data[layer_index]
        layer_shape[layer_index] = data[layer_index].shape

    for layer_index in range(no_of_layers):
        shares_dict[layer_index] = np.zeros(shape=(config.num_servers,) + layer_shape[layer_index], dtype=np.float64)

        for server_index in range(config.num_servers - 1):
            shares_dict[layer_index][server_index] = np.random.uniform(low=0, high=highest_range,
                                                                       size=layer_shape[layer_index]).astype(np.float64)

        share_sum_except_last = np.array(shares_dict[layer_index][:config.num_servers - 1]).sum(axis=0,
                                                                                                dtype=np.float64)
        x = np.copy(np.array(layer_dict[layer_index], dtype=np.float64))
        diff = np.subtract(x, share_sum_except_last, dtype=np.float64)
        last_share = np.fmod(diff, field_size, dtype=np.float64)
        shares_dict[layer_index][config.num_servers - 1] = last_share

    for server_index in range(config.num_servers):
        for layer_index in range(len(shares_dict)):
            all_servers[server_index][layer_index] = shares_dict[layer_index][server_index]

    global total_upload_cost

    pickle_model_list = []
    for server in range(config.num_servers):
        pickle_model_list.append(pickle.dumps(all_servers[server]))
        len_serialized_model = len(pickle_model_list[server])
        total_upload_cost += len_serialized_model
        print(f"[Upload] Size of the object to send to server {server} is {len_serialized_model}")

    flcommon.send_to_servers(pickle_model_list, config)

    global total_download_cost
    print(f"[DOWNLOAD] Total download cost so far: {total_download_cost}")
    print(f"[UPLOAD] Total upload cost so far: {total_upload_cost}")

    print(f"********************** Round {training_round} completed **********************")
    training_round += 1
    print("Waiting to receive response from master server...")

    time_logger.client_idle()


def recv_thread(data, remote_addr):
    print(f"[DOWNLOAD] Secret of {remote_addr} received. size: {len(data)}")
    global total_download_cost
    total_download_cost += len(data)

    global training_round
    if config.training_rounds == training_round:
        time_logger.finish_training()
        time_logger.print_result()

        print(f"[DOWNLOAD] Total download cost so far: {total_download_cost}")
        print(f"[UPLOAD] Total upload cost so far: {total_upload_cost}")

        print("Training finished.")
        return

    start_next_round(data)


@api.route('/recv', methods=['POST'])
def recv():
    my_thread = threading.Thread(target=recv_thread, args=(request.data, request.remote_addr))
    my_thread.start()
    return {"response": "ok"}


@api.route('/start', methods=['GET'])
def start():
    time_logger.start_training()
    my_thread = threading.Thread(target=start_next_round, args=(0,))
    my_thread.start()
    return {"response": "ok"}


api.run(host=flcommon.get_ip(config), port=config.client_base_port + int(sys.argv[1]), debug=True, threaded=True)

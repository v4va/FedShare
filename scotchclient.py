import pickle
import sys
import threading

import numpy as np
from flask import Flask, request

import flcommon
import mnistcommon
import time_logger
from config import ClientConfig

config = ClientConfig(int(sys.argv[1]))

client_datasets = mnistcommon.load_train_dataset(config.number_of_clients, permute=True)
LD = len(client_datasets[0][0]) // config.training_rounds

f_to_i_v = np.vectorize(flcommon.f_to_i)
i_to_f_v = np.vectorize(flcommon.i_to_f)

api = Flask(__name__)

servers_secret = []

total_download_cost = 0
total_upload_cost = 0

training_round = 0


def start_next_round(round_weight):
    time_logger.client_start()

    global training_round
    print(f"[CLIENT] Round {training_round} started.")
    x_train, y_train = client_datasets[config.client_index][0], client_datasets[config.client_index][1]

    model = mnistcommon.get_model()
    if training_round != 0:
        model.set_weights(round_weight)

    print(
        f"Model: SCOTCH, "
        f"Round: {training_round + 1}/{config.training_rounds}, "
        f"Client {config.client_index + 1}/{config.number_of_clients}, "
        f"Dataset Size: {len(x_train)}")
    model.fit(x_train, y_train, epochs=config.epochs, batch_size=config.batch_size, verbose=config.verbose,
              validation_split=config.validation_split)

    all_servers = []
    servers_model = []

    for server_index in range(config.num_servers):
        all_servers.append({})
        servers_model.append({})

    layer_dict, layer_shape, shares_dict = {}, {}, {}
    data = np.array(model.get_weights())
    no_of_layers = len(data)
    for layer_index in range(no_of_layers):
        layer_dict[layer_index] = data[layer_index]
        layer_shape[layer_index] = data[layer_index].shape

    for layer_index in range(no_of_layers):
        shares_dict[layer_index] = np.random.randint(1000, size=(config.num_servers,) + layer_shape[layer_index],
                                                     dtype=np.uint64)
        x = f_to_i_v(layer_dict[layer_index])
        for server_index in range(config.num_servers - 1):
            shares_dict[layer_index][server_index] = np.random.randint(1000, size=layer_shape[layer_index],
                                                                       dtype=np.uint64)
            x = x - shares_dict[layer_index][server_index]
        shares_dict[layer_index][config.num_servers - 1] = x

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

    print(f"[DOWNLOAD] Total download cost so far: {total_download_cost}")
    print(f"[UPLOAD] Total upload cost so far: {total_upload_cost}")

    print(f"Round {training_round} completed")
    training_round += 1
    print("Waiting to receive response from server...")

    time_logger.client_idle()


@api.route('/recv', methods=['POST'])
def recv():
    my_thread = threading.Thread(target=recv_thread, args=(servers_secret, request.data, request.remote_addr))
    my_thread.start()
    return {"response": "ok"}


def recv_thread(servers_secret: list, data, address):
    print(f"[SECRET] Secret of {address} received. len(data): {len(data)}")

    global total_download_cost
    total_download_cost += len(data)

    secret = pickle.loads(data)
    servers_secret.append(secret)

    if len(servers_secret) != config.num_servers:
        return

    print(f"[CLIENT] Response of all servers received.")
    model = {}
    for layer_index in range(len(servers_secret[0])):
        secrets_summation = np.zeros(shape=servers_secret[0][layer_index].shape, dtype=np.uint64)
        for server_index in range(len(servers_secret)):
            secrets_summation += servers_secret[server_index][layer_index]
        model[layer_index] = i_to_f_v(secrets_summation)
    round_weight = model

    global training_round
    if config.training_rounds == training_round:
        time_logger.finish_training()
        time_logger.print_result()

        print(f"[DOWNLOAD] Total download cost so far: {total_download_cost}")
        print(f"[UPLOAD] Total upload cost so far: {total_upload_cost}")

        print("Training finished.")
        return

    servers_secret.clear()

    start_next_round(round_weight)


@api.route('/start', methods=['GET'])
def start():
    time_logger.start_training()
    my_thread = threading.Thread(target=start_next_round, args=(0,))
    my_thread.start()
    return {"response": "ok"}


api.run(host=flcommon.get_ip(config), port=config.client_base_port + int(sys.argv[1]), debug=True, threaded=True)

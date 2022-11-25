import ipaddress
import pickle

import numpy as np
import threading
import ipaddress
import requests
from requests_toolbelt.adapters import source
# ------------------------------------------------------------------------------
# Decimal-Integer Conversion
# ------------------------------------------------------------------------------
import time_logger


def f_to_i(x, scale=1 << 32):
    if x < 0:
        if pow(2, 64) - (abs(x) * (scale)) > (pow(2, 64) - 1):
            return np.uint64(0)
        x = pow(2, 64) - (abs(x) * (scale))
        return np.uint64(x)
    else:
        if x * scale > pow(2, 64):
            return np.uint64(9223372036854775807)
        real_value = scale * x
        x = np.uint64(real_value)
        # print(f"Real value: {real_value} converted to {x}")
        return np.uint64(x)

def i_to_f(x, scale=1 << 32):
    l = 64
    t = x > (pow(2, (l - 1)) - 1)
    if t:
        x = pow(2, l) - x
        y = np.uint64(x)
        y = np.float32(y * (-1)) / scale

    else:
        y = np.float32(np.uint64(x)) / scale

    return y


f_to_i_v = np.vectorize(f_to_i)
i_to_f_v = np.vectorize(i_to_f)


def check_test_accuracy(name, training_round, training_rounds, x_test, y_test, verbose, weights, model_generator, each):
    print(f"+++++++ round: {training_round}/{training_rounds} +++++++")
    if training_round % each == 0:
        model = model_generator()

        model.set_weights(weights)
        results = model.evaluate(x_test, y_test, verbose=verbose)
        print(f"{name} model test accuracy:\t {results[1]}")
    else:
        print("Ignoring test accuracy.")


def check_test_accuracy_simple(x_test, y_test, verbose, weights, model_generator):
    model = model_generator()
    model.set_weights(weights)
    results = model.evaluate(x_test, y_test, verbose=verbose)
    print(f"Model test accuracy:\t {results[1]}")


def broadcast_to_clients(pickle_model, config, lead_server=False):
    my_threads = []
    for client in range(config.number_of_clients):
        my_thread = threading.Thread(target=send_to_client, args=(client, pickle_model, config, lead_server))
        my_thread.start()
        my_threads.append(my_thread)
    for th in my_threads:
        print(f"[THREAD] Waiting for thread {th.name}")
        th.join()


def send_to_client(client, pickle_model, config, lead_server):
    if lead_server:
        time_logger.lead_server_start_upload()
    else:
        time_logger.server_start_upload()

    port = config.client_base_port + client

    url = f'http://{str(ipaddress.ip_address(config.client_address) + client)}:{port}/recv'
    s = requests.Session()
    new_source = source.SourceAddressAdapter(config.master_server_address)
    s.mount('http://', new_source)
    print(s.post(url, pickle_model).json())
    print(f"[CLIENT] model sent to client {client}")


def get_ip(config):
    return str(ipaddress.ip_address(config.client_address) + config.client_index)


def send_to_servers(pickle_model_list, config):
    my_threads = []
    for index in range(config.num_servers):
        my_thread = threading.Thread(target=send_to_server, args=(index, pickle_model_list[index], config))
        my_thread.start()
        my_threads.append(my_thread)
    for th in my_threads:
        print(f"[THREAD] Waiting for thread {th.name}")
        th.join()


def send_to_server(server, pickle_model, config):
    time_logger.client_start_upload()
    url = f'http://{config.server_address}:{config.server_base_port + server}/recv'
    s = requests.Session()
    new_source = source.SourceAddressAdapter(get_ip(config))
    s.mount('http://', new_source)
    print(s.post(url, pickle_model).json())

    print(f"Sent to server {server}")


def send_to_fedavg_server(pickle_model, config):
    time_logger.client_start_upload()
    url = f'http://{config.server_address}:{config.fedavg_server_port}/recv'
    s = requests.Session()
    new_source = source.SourceAddressAdapter(get_ip(config))
    s.mount('http://', new_source)
    print(s.post(url, pickle_model).json())

    print(f"Sent to fedavg server.")
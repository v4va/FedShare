import time

from flask import Flask

from config import Config

api = Flask(__name__)

client_start_list = []
client_start_upload_list = []
client_idle_list = []

server_received_list = []
server_start_list = []
server_start_upload_list = []
server_idle_list = []

lead_server_received_list = []
lead_server_start_list = []
lead_server_start_upload_list = []
lead_server_idle_list = []

start_training_list = []
finish_training_list = []


@api.route('/start_training', methods=['POST'])
def start_training():
    start_training_list.append(time.time())
    return {"response": "ok"}


@api.route('/finish_training', methods=['POST'])
def finish_training():
    finish_training_list.append(time.time())
    return {"response": "ok"}


@api.route('/client_start', methods=['POST'])
def client_start():
    client_start_list.append(time.time())
    return {"response": "ok"}


@api.route('/client_start_upload', methods=['POST'])
def client_start_upload():
    client_start_upload_list.append(time.time())
    return {"response": "ok"}


@api.route('/client_idle', methods=['POST'])
def client_idle():
    client_idle_list.append(time.time())
    return {"response": "ok"}


@api.route('/server_received', methods=['POST'])
def server_received():
    server_received_list.append(time.time())
    return {"response": "ok"}


@api.route('/server_start', methods=['POST'])
def server_start():
    server_start_list.append(time.time())
    return {"response": "ok"}


@api.route('/server_start_upload', methods=['POST'])
def server_start_upload():
    server_start_upload_list.append(time.time())
    return {"response": "ok"}


@api.route('/server_idle', methods=['POST'])
def server_idle():
    server_idle_list.append(time.time())
    return {"response": "ok"}


@api.route('/lead_server_received', methods=['POST'])
def lead_server_received():
    lead_server_received_list.append(time.time())
    return {"response": "ok"}


@api.route('/lead_server_start', methods=['POST'])
def lead_server_start():
    lead_server_start_list.append(time.time())
    return {"response": "ok"}


@api.route('/lead_server_start_upload', methods=['POST'])
def lead_server_start_upload():
    lead_server_start_upload_list.append(time.time())
    return {"response": "ok"}


@api.route('/lead_server_idle', methods=['POST'])
def lead_server_idle():
    lead_server_idle_list.append(time.time())
    return {"response": "ok"}


@api.route('/print_result', methods=['POST'])
def print_result():
    print(f"client_start_list = {client_start_list}")
    print(f"client_start_upload_list = {client_start_upload_list}")
    print(f"client_idle_list = {client_idle_list}")

    print(f"server_received_list = {server_received_list}")
    print(f"server_start_list = {server_start_list}")
    print(f"server_start_upload_list = {server_start_upload_list}")
    print(f"server_idle_list = {server_idle_list}")

    print(f"lead_server_received_list = {lead_server_received_list}")
    print(f"lead_server_start_list = {lead_server_start_list}")
    print(f"lead_server_start_upload_list = {lead_server_start_upload_list}")
    print(f"lead_server_idle_list = {lead_server_idle_list}")

    print(f"start_training_list = {start_training_list}")
    print(f"finish_training_list = {finish_training_list}")

    print(f"duration_training = {finish_training_list[-1] - start_training_list[0]}")

    my_dict = {
        "client_start_list": client_start_list,
        "client_start_upload_list": client_start_upload_list,
        "client_idle_list": client_idle_list,
        "server_received_list": server_received_list,
        "server_start_list": server_start_list,
        "server_start_upload_list": server_start_upload_list,
        "server_idle_list": server_idle_list,
        "lead_server_received_list": lead_server_received_list,
        "lead_server_start_list": lead_server_start_list,
        "lead_server_start_upload_list": lead_server_start_upload_list,
        "lead_server_idle_list": lead_server_idle_list,
        "start_training_list": start_training_list,
        "finish_training_list": finish_training_list
    }
    print(my_dict)

    return my_dict


config = Config()
api.run(host=config.logger_address, port=config.logger_port, threaded=True)

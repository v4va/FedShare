from config import Config
import requests

config = Config()


def client_start():
    url = f'http://{config.logger_address}:{config.logger_port}/client_start'
    post_print(url)


def client_start_upload():
    url = f'http://{config.logger_address}:{config.logger_port}/client_start_upload'
    post_print(url)


def client_idle():
    url = f'http://{config.logger_address}:{config.logger_port}/client_idle'
    post_print(url)


def server_received():
    url = f'http://{config.logger_address}:{config.logger_port}/server_received'
    post_print(url)


def server_start():
    url = f'http://{config.logger_address}:{config.logger_port}/server_start'
    post_print(url)


def server_start_upload():
    url = f'http://{config.logger_address}:{config.logger_port}/server_start_upload'
    post_print(url)


def server_idle():
    url = f'http://{config.logger_address}:{config.logger_port}/server_idle'
    post_print(url)


def lead_server_received():
    url = f'http://{config.logger_address}:{config.logger_port}/lead_server_received'
    post_print(url)


def lead_server_start():
    url = f'http://{config.logger_address}:{config.logger_port}/lead_server_start'
    post_print(url)


def lead_server_start_upload():
    url = f'http://{config.logger_address}:{config.logger_port}/lead_server_start_upload'
    post_print(url)


def lead_server_idle():
    url = f'http://{config.logger_address}:{config.logger_port}/lead_server_idle'
    post_print(url)


def start_training():
    url = f'http://{config.logger_address}:{config.logger_port}/start_training'
    post_print(url)


def finish_training():
    url = f'http://{config.logger_address}:{config.logger_port}/finish_training'
    post_print(url)


def print_result():
    url = f'http://{config.logger_address}:{config.logger_port}/print_result'
    post_print(url)

def post_print(url):
    print(requests.post(url).json())
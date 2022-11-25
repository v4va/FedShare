class Config:
    number_of_clients = 5
    train_dataset_size = 60000
    clients_dataset_size = [train_dataset_size/number_of_clients] * number_of_clients
    total_dataset_size = sum(clients_dataset_size)
    num_servers = 2
    training_rounds = 3
    epochs = 1
    batch_size = 16
    verbose = 1
    validation_split = 0.1
    server_base_port = 8500
    master_server_index = 0
    master_server_port = 7501
    client_address = '127.0.1.1'
    server_address = '127.0.0.3'
    master_server_address = '127.0.0.4'
    buffer_size = 4096
    client_base_port = 9500
    fedavg_server_port = 3500
    logger_address = '127.0.0.100'
    logger_port = 8778
    delay = 10


class ClientConfig(Config):
    def __init__(self, client_index):
        self.client_index = client_index


class ServerConfig(Config):
    def __init__(self, server_index):
        self.server_index = server_index


class LeadConfig(Config):
    def __init__(self):
        pass


class FedAvgServerConfig(Config):
    def __init__(self):
        pass

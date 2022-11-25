import numpy as np
from tensorflow.keras.layers import (Dense)
from tensorflow.keras.models import Sequential
from tensorflow.keras.utils import to_categorical
import emnist


def load_train_dataset(n_clients=3, permute=False):
    client_datasets = {}  # defining local datasets for each client

    x_train, y_train = emnist.extract_training_samples('digits')
    x_train = x_train.reshape(x_train.shape[0], 784)

    if permute == True:
        permutation_indexes = np.random.permutation(len(x_train))
        x_train = x_train[permutation_indexes]
        y_train = y_train[permutation_indexes]

    x_train = x_train.astype('float32')
    x_train /= 255

    y_train = to_categorical(y_train)

    for i in range(n_clients):
        client_datasets[i] = [
            x_train[i * (len(x_train) // n_clients):i * (len(x_train) // n_clients) + (len(x_train) // n_clients)],
            y_train[i * (len(y_train) // n_clients):i * (len(y_train) // n_clients) + (len(y_train) // n_clients)]]

    return client_datasets


def load_test_dataset():
    x_test, y_test = emnist.extract_test_samples('digits')
    x_test = x_test.reshape(x_test.shape[0], 784)
    x_test = x_test.astype('float32')
    x_test /= 255
    y_test = to_categorical(y_test)
    return x_test, y_test


def get_model():
    model = Sequential()
    model.add(Dense(350, input_shape=(784,), activation='relu'))
    model.add(Dense(50, activation='relu'))
    model.add(Dense(10, activation='softmax'))

    # Configure the model and start training
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    return model

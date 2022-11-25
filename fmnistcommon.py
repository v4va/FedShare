import numpy as np
from tensorflow.keras.datasets import fashion_mnist
from tensorflow.keras.layers import (Dense)
from tensorflow.keras.models import Sequential
from tensorflow.keras.utils import to_categorical


def load_train_dataset(n_clients=3, permute=False):
    client_datasets = {}  # defining local datasets for each client

    (X_train, Y_train), (_, _) = fashion_mnist.load_data()

    X_train = X_train.reshape(X_train.shape[0], 784)

    if permute == True:
        permutation_indexes = np.random.permutation(len(X_train))
        X_train = X_train[permutation_indexes]
        Y_train = Y_train[permutation_indexes]

    X_train = X_train.astype('float32')
    X_train /= 255

    Y_train = to_categorical(Y_train)

    for i in range(n_clients):
        client_datasets[i] = [
            X_train[i * (len(X_train) // n_clients):i * (len(X_train) // n_clients) + (len(X_train) // n_clients)],
            Y_train[i * (len(Y_train) // n_clients):i * (len(Y_train) // n_clients) + (len(Y_train) // n_clients)]]

    return client_datasets


def load_test_dataset():
    (_, _), (X_test, Y_test) = fashion_mnist.load_data()
    X_test = X_test.reshape(X_test.shape[0], 784)
    X_test = X_test.astype('float32')
    X_test /= 255
    Y_test = to_categorical(Y_test)
    return X_test, Y_test


def get_model():
    model = Sequential()
    model.add(Dense(512, input_shape=(784,), activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(10, activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    return model

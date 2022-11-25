import random

import pandas as pd
from keras.layers import Dropout
from sklearn.preprocessing import StandardScaler
from tensorflow.keras import initializers
from tensorflow.keras.layers import (Dense)
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import SGD
from tensorflow.python.keras.utils.np_utils import to_categorical

split_ratio = 0.9


def load_train():
    x_train = pd.read_csv('mhealth/x_train.csv').to_numpy()
    y_train = pd.read_csv('mhealth/y_train.csv').to_numpy()
    y_train_cat = to_categorical(y_train)
    x_test = pd.read_csv('mhealth/x_test.csv').to_numpy()
    y_test = pd.read_csv('mhealth/y_test.csv').to_numpy()
    y_test_cat = to_categorical(y_test)

    sc = StandardScaler()
    x_train = sc.fit_transform(x_train)
    x_test = sc.transform(x_test)

    return x_train, y_train_cat, x_test, y_test_cat


def load_train_dataset(n_clients, balanced=True):
    random.seed(9001)

    client_datasets = {}

    x_train, y_train_cat, x_test, y_test_cat = load_train()

    if balanced:
        for i in range(n_clients):
            length = (len(x_train) // n_clients)
            begin = i * length
            end = begin + length
            client_datasets[i] = [x_train[begin: end],
                                  y_train_cat[begin: end]]
    else:
        arr = [i * random.randint(1, 5) for i in range(1, n_clients + 1)]
        n = len(x_train)
        for i in range(n - (sum(arr))):
            arr[random.randint(0, n) % n_clients] += 1

        for i in range(n_clients):
            length = arr[i]
            begin = sum(arr[:i])
            end = begin + length
            client_datasets[i] = [x_train[begin: end],
                                  y_train_cat[begin: end]]
    return client_datasets, x_test, y_test_cat


def get_model():
    model = Sequential()

    model.add(Dense(128, input_shape=(6,), activation='leaky_relu',
                    kernel_initializer=initializers.GlorotNormal(seed=1)))
    model.add(Dense(64, activation='tanh',
                    kernel_initializer=initializers.GlorotNormal(seed=3)))
    model.add(Dense(8, activation='tanh', kernel_initializer=initializers.GlorotNormal(seed=4)))
    model.add(Dense(3, activation='softmax', kernel_initializer=initializers.GlorotNormal(seed=5)))

    # model.add(Dense(1024, input_shape=(6,), activation='relu', kernel_initializer=initializers.GlorotNormal(seed=1)))
    # model.add(Dropout(0.1, seed=2))
    # model.add(Dense(512, activation='relu', kernel_initializer=initializers.GlorotNormal(seed=5)))
    # model.add(Dropout(0.1, seed=48))
    # model.add(Dense(512, activation='relu', kernel_initializer=initializers.GlorotNormal(seed=2)))
    # model.add(Dropout(0.1, seed=53))
    # model.add(Dense(128, activation='relu', kernel_initializer=initializers.GlorotNormal(seed=8)))
    # model.add(Dropout(0.1, seed=35))
    # model.add(Dense(128, activation='relu', kernel_initializer=initializers.GlorotNormal(seed=87)))
    # model.add(Dropout(0.1, seed=46))
    # model.add(Dense(3, activation='softmax', kernel_initializer=initializers.GlorotNormal(seed=4)))

    # model.add(Dense(1024, input_shape=(6,), activation='tanh', kernel_initializer=initializers.GlorotNormal(seed=1)))
    # model.add(Dropout(0.1, seed=2))
    # model.add(Dense(512, activation='tanh', kernel_initializer=initializers.GlorotNormal(seed=5)))
    # model.add(Dropout(0.1, seed=48))
    # model.add(Dense(128, activation='tanh', kernel_initializer=initializers.GlorotNormal(seed=87)))
    # model.add(Dropout(0.1, seed=46))
    # model.add(Dense(3, activation='softmax', kernel_initializer=initializers.GlorotNormal(seed=4)))

    opt = SGD(learning_rate=0.0005)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])

    return model


if __name__ == "__main__":
    load_train_dataset(10, balanced=False)

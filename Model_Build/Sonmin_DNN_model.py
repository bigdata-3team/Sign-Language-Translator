import pandas as pd
from pandas import DataFrame
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

dataset_annotation = pd.read_excel("수어_데이터셋_어노테이션.xlsx")
dataset_annotation

unique = dataset_annotation["한국어"].unique()


print(unique.shape)


# #  RNN models in Tensorflow
# - 기본적인 input data 구조 : (batch size, time steps, input length)
#  > one, many의 의미는 time steps 와 관련 ex) many-to-one : 입력의 time steps > 1 / 출력의 time steps == 1
#  - Many-to-One : input 형태 - (batch size, t, input length), t > 1 / output 형태 (batch size, 1, 1)
# 

inputs = tf.keras.Input(shape=(10, 128, 128, 3))
input_shape = (10, 128, 128, 3)
classes = 524
inputs = tf.keras.Input(shape = input_shape)
conv1 = tf.keras.layers.Conv2D(32, (3, 3), activation="relu")
layer_conv1 = tf.keras.layers.TimeDistributed(conv1)(inputs)
maxpool1 = tf.keras.layers.MaxPooling2D(pool_size=(2,2), strides=(2, 2))
layer_maxpool1 = tf.keras.layers.TimeDistributed(maxpool1)(layer_conv1)
conv2 = tf.keras.layers.Conv2D(64, (3, 3), activation="relu")
layer_conv2 = tf.keras.layers.TimeDistributed(conv2)(layer_maxpool1)
maxpool2 = tf.keras.layers.MaxPooling2D(pool_size=(2,2), strides=(2, 2))
layer_maxpool2 = tf.keras.layers.TimeDistributed(maxpool2)(layer_conv2)
flatten = tf.keras.layers.Flatten()
layer_flatten = tf.keras.layers.TimeDistributed(flatten)(layer_maxpool2)
layer_lstm = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(1000, activation='tanh'))(layer_flatten)
outputs = tf.keras.layers.Dense(classes, activation="softmax")(layer_lstm)
model = tf.keras.models.Model(inputs = inputs, outputs = outputs)

model.summary()

model.compile(loss = "MSE", optimizer = "adam")
model.fit(x, y, epochs = 100, batch_size = 1, verbose = 1)


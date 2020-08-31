import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

import dataset_prepare as dp
import data_augmentation as da

dataset_annotation = pd.read_excel("수어_데이터셋_어노테이션.xlsx")
# 메모리 문제 해결 후에 삭제할 부분
dataset_annotation.loc[(dataset_annotation["한국어"].map(type) == int), "타입(단어/문장)"] = "숫자"

dataset_annotation = dataset_annotation[dataset_annotation["타입(단어/문장)"] != "문장"]
dataset_annotation = dataset_annotation[dataset_annotation["타입(단어/문장)"] != "숫자"]
dataset_annotation

unique = dataset_annotation["한국어"].unique()
print(unique.shape)

unique_idx_dict = dict(zip(unique, range(len(unique))))
del(dataset_annotation)

xlen, ylen = 120, 67
X, y, seq_len = dp.read_ai(xlen=xlen, ylen=ylen)

y = (pd.Series(y)).map(unique_idx_dict)
y = list(y); y
y = np.array(y)

for i in range(len(X)):
    X[i] = X[i].reshape(-1, *(X[i].shape))
    X[i] = X[i].astype(np.float32)

X = np.concatenate(X, axis = 0); print(X.shape)

# 검증셋 분리
X_train, y_train, X_valid, y_valid = dp.train_test_split(X, y, category=len(unique))
##############
del X
del y
X_train_len = X_train.shape[0]

# data augmentation 작업
# translate -> rotate -> Gaussian Noise
X_train_cat1 = da.apply_data_augmentation(X_train, [1, 2, 3])
X_train = np.concatenate([X_train, X_train_cat1], axis=0)
del X_train_cat1

# zoom -> rotate -> Gaussian Noise
X_train_cat2 = da.apply_data_augmentation(X_train[:X_train_len], [5, 2, 3])
X_train = np.concatenate([X_train, X_train_cat2], axis=0)
del X_train_cat2

y_train = np.concatenate([y_train, y_train, y_train])

y_valid_onehot = tf.keras.utils.to_categorical(y_valid, len(unique))
y_train_onehot = tf.keras.utils.to_categorical(y_train, len(unique))

# Model build
input_shape = (seq_len, ylen, xlen, 3)
classes = len(unique)
inputs = tf.keras.Input(shape = input_shape)
conv1 = tf.keras.layers.Conv2D(32, (5, 5), activation="relu")
layer_conv1 = tf.keras.layers.TimeDistributed(conv1)(inputs)
normal_conv1 = tf.keras.layers.BatchNormalization()(layer_conv1)
maxpool1 = tf.keras.layers.MaxPooling2D(pool_size=(2,2), strides=(2, 2))
layer_maxpool1 = tf.keras.layers.TimeDistributed(maxpool1)(normal_conv1)
conv2 = tf.keras.layers.Conv2D(64, (5, 5), activation="relu")
layer_conv2 = tf.keras.layers.TimeDistributed(conv2)(layer_maxpool1)
normal_conv2 = tf.keras.layers.BatchNormalization()(layer_conv2)
maxpool2 = tf.keras.layers.MaxPooling2D(pool_size=(2,2), strides=(2, 2))
layer_maxpool2 = tf.keras.layers.TimeDistributed(maxpool2)(normal_conv2)

conv3 = tf.keras.layers.Conv2D(64, (5, 5), activation="relu")
layer_conv3 = tf.keras.layers.TimeDistributed(conv3)(layer_maxpool2)
normal_conv3 = tf.keras.layers.BatchNormalization()(layer_conv3)
maxpool3 = tf.keras.layers.MaxPooling2D(pool_size=(2,2), strides=(2, 2))
layer_maxpool3 = tf.keras.layers.TimeDistributed(maxpool3)(normal_conv3)

flatten = tf.keras.layers.Flatten()
layer_flatten = tf.keras.layers.TimeDistributed(flatten)(layer_maxpool3)
batch_normalization = tf.keras.layers.BatchNormalization()(layer_flatten)
layer_lstm = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(2 * classes, activation='tanh'))(batch_normalization)
layer_dropout = tf.keras.layers.Dropout(0.25)(layer_lstm)
outputs = tf.keras.layers.Dense(classes, activation="softmax")(layer_dropout)
model = tf.keras.models.Model(inputs = inputs, outputs = outputs)

model.summary()

model.compile(loss = "categorical_crossentropy", optimizer = "rmsprop", metrics = ["accuracy"])

history = model.fit(X_train, y_train_onehot, batch_size=32, epochs=30, verbose = 1, validation_data = (X_valid, y_valid_onehot))

model.save("sonmin_model3.h5")


# 생성된 모델과 단어에 따른 인덱스 딕셔너리 저장
import pickle

with open("sonmin_word.p", "wb") as file:
    pickle.dump(unique_idx_dict, file)
model.save("sonmin_model2.h5")

# 모델 예측값에 대한 Confusion Matrix
from sklearn.metrics import confusion_matrix
predictions = model.predict(X_valid)
predictions = np.argmax(predictions, axis=1)
conf_mat = confusion_matrix(y_valid, predictions)
